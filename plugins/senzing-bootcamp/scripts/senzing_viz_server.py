#!/usr/bin/env python3
"""Bundled Senzing entity-resolution visualization web app.

A single, self-contained, tested visualization the bootcamp can run
deterministically so the Module 3 "wow moment" (and later result views) ALWAYS
happens, instead of the agent hand-writing a server + D3 page every run.

It builds an entity model from the records the bootcamper loaded (by looking each
one up through the Senzing SDK, so all data comes from real entity resolution),
then serves:

- ``GET /``            single-page D3 v7 visualization (4 tabs + summary banner)
- ``GET /api/stats``   aggregate resolution statistics
- ``GET /api/graph``   entity nodes + relationship edges
- ``GET /api/merges``  multi-record entities with constituent records
- ``GET /api/search``  search-by-attributes with resolution reasoning

Data source: ``get_entity_by_record_id`` with ``SZ_ENTITY_DEFAULT_FLAGS`` (which
includes ``SZ_ENTITY_INCLUDE_ALL_RELATIONS``), so nodes and edges come from one
call per loaded record. No direct SQL is ever run against the database.

Usage:
    # Serve the live web app (Module 3 default):
    python3 senzing_viz_server.py --records src/system_verification/*.jsonl

    # Also write a persistent standalone snapshot (no server needed to view):
    python3 senzing_viz_server.py --records data/transformed/*.jsonl \\
        --snapshot docs/visualizations/results.html --serve-once-check

    # Just build the snapshot and exit (no server), used by the completion gate:
    python3 senzing_viz_server.py --records src/system_verification/*.jsonl \\
        --snapshot docs/visualizations/truthset_verification.html --no-serve

Settings come from ``--settings`` (default ``config/engine_config.json``) or the
``SENZING_ENGINE_CONFIGURATION_JSON`` env var. The Senzing native library must be
importable (source the project ``src/scripts/senzing-env.sh`` first).

Exit code 0 means the entity model was built successfully (and, if requested, the
snapshot was written); non-zero means it could not be built.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

SOURCE_COLORS = {
    "CUSTOMERS": "#3b82f6",
    "REFERENCE": "#22c55e",
    "WATCHLIST": "#f59e0b",
}
FALLBACK_COLORS = ["#8b5cf6", "#ec4899", "#14b8a6", "#ef4444", "#0ea5e9", "#a3a34a"]


# --------------------------------------------------------------------------- #
# Entity model (built from the SDK)
# --------------------------------------------------------------------------- #
def _iter_record_keys(patterns):
    """Yield (data_source, record_id) from the loaded JSONL files."""
    seen = set()
    files = []
    for pat in patterns:
        files.extend(sorted(glob.glob(pat)))
    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    ds = d.get("DATA_SOURCE")
                    rid = d.get("RECORD_ID")
                    if ds is None or rid is None:
                        continue
                    key = (str(ds), str(rid))
                    if key not in seen:
                        seen.add(key)
                        yield key
        except OSError:
            continue


class Model:
    def __init__(self):
        self.records_total = 0
        self.entities = {}   # entity_id -> {...}
        self.edges = {}      # (min,max) -> {match_key, relationship_type}

    def build(self, engine, flags, record_keys):
        get = engine.get_entity_by_record_id
        for ds, rid in record_keys:
            self.records_total += 1
            try:
                resp = json.loads(get(ds, rid, flags))
            except Exception:
                continue
            re_ = resp.get("RESOLVED_ENTITY", {})
            eid = re_.get("ENTITY_ID")
            if eid is None:
                continue
            if eid not in self.entities:
                records = re_.get("RECORDS", [])
                sources = sorted({r.get("DATA_SOURCE", "?") for r in records})
                self.entities[eid] = {
                    "entity_id": eid,
                    "entity_name": re_.get("ENTITY_NAME") or f"Entity {eid}",
                    "record_count": len(records),
                    "data_sources": sources,
                    "records": [
                        {
                            "data_source": r.get("DATA_SOURCE", "?"),
                            "record_id": str(r.get("RECORD_ID", "?")),
                        }
                        for r in records
                    ],
                }
            for rel in resp.get("RELATED_ENTITIES", []):
                tid = rel.get("ENTITY_ID")
                if tid is None:
                    continue
                key = (min(eid, tid), max(eid, tid))
                if key not in self.edges:
                    self.edges[key] = {
                        "match_key": rel.get("MATCH_KEY", ""),
                        "relationship_type": rel.get("MATCH_LEVEL_CODE")
                        or rel.get("ERRULE_CODE")
                        or "RELATED",
                    }
        return self

    # ---- API payloads ---------------------------------------------------- #
    def stats(self):
        ents = self.entities.values()
        hist = {"1": 0, "2": 0, "3": 0, "4+": 0}
        for e in ents:
            c = e["record_count"]
            hist["4+" if c >= 4 else str(c)] = hist.get("4+" if c >= 4 else str(c), 0) + 1
        return {
            "records_total": self.records_total,
            "entities_total": len(self.entities),
            "multi_record_entities": sum(1 for e in ents if e["record_count"] > 1),
            "cross_source_entities": sum(1 for e in ents if len(e["data_sources"]) >= 2),
            "relationships_total": len(self.edges),
            "histogram": hist,
        }

    def graph(self):
        node_ids = set(self.entities)
        nodes = list(self.entities.values())
        edges = []
        for (a, b), meta in self.edges.items():
            if a in node_ids and b in node_ids:
                edges.append(
                    {
                        "source_entity_id": a,
                        "target_entity_id": b,
                        "match_key": meta["match_key"],
                        "relationship_type": meta["relationship_type"],
                    }
                )
        return {"nodes": nodes, "edges": edges}

    def merges(self):
        out = [e for e in self.entities.values() if e["record_count"] > 1]
        out.sort(key=lambda e: -e["record_count"])
        return {"entities": out}

    def search(self, engine, flags, query):
        query = (query or "").strip()
        if not query:
            return {"results": []}
        attrs = json.dumps({"NAME_FULL": query})
        try:
            try:
                raw = engine.search_by_attributes(attrs, flags)
            except TypeError:
                raw = engine.search_by_attributes(attrs, flags, "")
            resp = json.loads(raw)
        except Exception as exc:
            return {"results": [], "error": str(exc)}
        results = []
        for item in resp.get("RESOLVED_ENTITIES", [])[:10]:
            ent = item.get("ENTITY", {}).get("RESOLVED_ENTITY", {})
            eid = ent.get("ENTITY_ID")
            match = item.get("MATCH_INFO", {})
            local = self.entities.get(eid, {})
            results.append(
                {
                    "entity_id": eid,
                    "entity_name": ent.get("ENTITY_NAME") or local.get("entity_name", "?"),
                    "record_count": local.get("record_count"),
                    "data_sources": local.get("data_sources", []),
                    "match_key": match.get("MATCH_KEY", ""),
                    "resolution_rule": match.get("ERRULE_CODE", ""),
                }
            )
        return {"results": results}


# --------------------------------------------------------------------------- #
# HTML (single page, D3 v7). Placeholders filled with .replace() to avoid brace
# conflicts with the CSS/JS braces.
# --------------------------------------------------------------------------- #
PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
__D3_SCRIPT__
__DATA_SHIM__
<style>
:root{--navy:#0c2340;--blue:#175ca8;--gold:#c8922a;--ink:#1e293b;--muted:#64748b;--line:#e2e8f0;--bg:#f8fafc}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}
header{background:var(--navy);color:#fff;padding:12px 20px;border-bottom:3px solid var(--gold);position:sticky;top:0;z-index:10}
header h1{margin:0;font-size:18px}
.banner{display:flex;gap:10px;flex-wrap:wrap;padding:12px 20px;background:#fff;border-bottom:1px solid var(--line)}
.stat{flex:1;min-width:120px;text-align:center}
.stat .n{font-size:24px;font-weight:700;color:var(--blue)}
.stat .l{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.03em}
.stat .arrow{color:var(--gold);font-weight:700;align-self:center}
nav{display:flex;gap:4px;padding:0 20px;background:#fff;border-bottom:1px solid var(--line)}
nav button{border:none;background:none;padding:10px 14px;font-size:14px;color:var(--muted);cursor:pointer;border-bottom:3px solid transparent}
nav button.active{color:var(--blue);border-bottom-color:var(--blue);font-weight:600}
main{padding:0}
.tab{display:none;padding:16px 20px}
.tab.active{display:block}
#graph-container{position:relative;height:calc(100vh - 175px);min-height:360px;background:#fff;border:1px solid var(--line);border-radius:8px;overflow:hidden;padding:0}
#graph-container svg{width:100%;height:100%;display:block}
.legend{position:absolute;top:10px;right:10px;background:rgba(255,255,255,.92);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:12px}
.legend .row{display:flex;align-items:center;gap:6px;margin:2px 0}
.legend .dot{width:12px;height:12px;border-radius:50%}
.node circle{stroke:#fff;stroke-width:1.5px;cursor:pointer}
.node text{font-size:10px;fill:var(--ink);pointer-events:none}
.edge line{stroke:#cbd5e1;stroke-width:1.5px}
.edge text{font-size:9px;fill:var(--muted)}
.tooltip{position:absolute;pointer-events:none;background:var(--navy);color:#fff;padding:6px 9px;border-radius:6px;font-size:12px;opacity:0;max-width:240px}
.card{background:#fff;border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin-bottom:10px}
.card h4{margin:0 0 6px;font-size:15px}
.recs{display:flex;gap:10px;flex-wrap:wrap}
.rec{border:1px solid var(--line);border-radius:6px;padding:8px 10px;font-size:12px;min-width:150px;background:#f8fafc}
.chip{display:inline-block;border:1px solid var(--blue);color:var(--blue);background:#eff6ff;border-radius:12px;padding:1px 8px;font-size:11px;margin:2px 2px 0 0;font-family:monospace}
.mk span{display:inline-block;border:1px solid var(--gold);background:#fdf6e9;color:#8a6d1f;border-radius:4px;padding:0 5px;margin:1px;font-family:monospace;font-size:11px}
#search-in{padding:8px 10px;border:1px solid var(--line);border-radius:6px;font-size:14px;width:min(420px,100%)}
button.probe{border:1px solid var(--line);background:#fff;border-radius:16px;padding:5px 12px;margin:2px;cursor:pointer;font-size:13px}
.muted{color:var(--muted)}
.modal-bg{position:fixed;inset:0;background:rgba(15,23,42,.45);display:none;align-items:center;justify-content:center;z-index:50}
.modal{background:#fff;border-radius:10px;padding:18px 20px;max-width:420px;width:90%}
.modal h3{margin:0 0 8px}
.modal button{margin-top:10px;border:none;background:var(--blue);color:#fff;border-radius:6px;padding:6px 12px;cursor:pointer}
</style></head>
<body>
<header><h1>__TITLE__</h1></header>
<div class="banner" id="banner"></div>
<nav id="nav"></nav>
<main>
  <section class="tab active" id="tab-graph"><div id="graph-container"><div class="tooltip" id="tt"></div></div></section>
  <section class="tab" id="tab-merges"><div id="merges"></div></section>
  <section class="tab" id="tab-stats"><div id="hist"></div></section>
  <section class="tab" id="tab-probe">
    <div style="margin-bottom:10px"><input id="search-in" placeholder="Search a name (e.g. Robert Smith)"> <button class="probe" onclick="doSearch()">Search</button></div>
    <div id="probe-btns"></div><div id="results"></div>
  </section>
</main>
<div class="modal-bg" id="modal-bg" onclick="if(event.target.id==='modal-bg')closeModal()"><div class="modal" id="modal"></div></div>
<script>
const TABS=[["graph","Entity Graph"],["merges","Record Merges"],["stats","Merge Statistics"],["probe","Search / Probe"]];
const SRC_COLORS=__SRC_COLORS__;
function color(src){return SRC_COLORS[src]||"#8b5cf6";}
const nav=d3.select("#nav");
TABS.forEach(([id,label],i)=>{nav.append("button").attr("class",i===0?"active":"").text(label).on("click",function(){
  d3.selectAll("nav button").classed("active",false);d3.select(this).classed("active",true);
  d3.selectAll(".tab").classed("active",false);d3.select("#tab-"+id).classed("active",true);
  if(id==="graph")drawGraph();if(id==="stats")drawHist();
});});
async function getJSON(u){const r=await fetch(u);return r.json();}
async function loadBanner(){const s=await getJSON("/api/stats");
  const items=[["Records Loaded",s.records_total],["Resolved Entities",s.entities_total],["Multi-Record",s.multi_record_entities],["Cross-Source",s.cross_source_entities],["Relationships",s.relationships_total]];
  const b=d3.select("#banner");b.html("");
  items.forEach((it,i)=>{const d=b.append("div").attr("class","stat");d.append("div").attr("class","n").text(it[1]);d.append("div").attr("class","l").text(it[0]);
    if(i<items.length-1)b.append("div").attr("class","arrow").text("→");});}
let graphDrawn=false;
async function drawGraph(){
  const c=document.getElementById("graph-container");const W=c.clientWidth,H=c.clientHeight;
  const g=await getJSON("/api/graph");
  d3.select("#graph-container svg").remove();
  const svg=d3.select("#graph-container").append("svg").attr("width",W).attr("height",H).attr("viewBox",[0,0,W,H]);
  const root=svg.append("g");
  svg.call(d3.zoom().scaleExtent([0.2,4]).on("zoom",function(ev){root.attr("transform",ev.transform);}));
  const nodes=g.nodes.map(function(n){return Object.assign({},n,{id:n.entity_id});});
  // EDGE-KEY MAPPING: forceLink resolves against id via source/target; map before use.
  const idset=new Set(nodes.map(function(n){return n.id;}));
  const links=g.edges.map(function(e){return {source:e.source_entity_id,target:e.target_entity_id,match_key:e.match_key};})
                     .filter(function(e){return idset.has(e.source)&&idset.has(e.target);});
  const sim=d3.forceSimulation(nodes)
    .force("link",d3.forceLink(links).id(function(d){return d.id;}).distance(90))
    .force("charge",d3.forceManyBody().strength(-160))
    .force("center",d3.forceCenter(W/2,H/2))
    .force("collide",d3.forceCollide().radius(function(d){return radius(d)+6;}));
  const edge=root.append("g").selectAll("g").data(links).join("g").attr("class","edge");
  edge.append("line");
  edge.append("text").text(function(d){return d.match_key||"";});
  const node=root.append("g").selectAll("g").data(nodes).join("g").attr("class","node")
    .call(d3.drag().on("start",dstart).on("drag",dragged).on("end",dend))
    .on("click",function(ev,d){openModal(d);})
    .on("mousemove",function(ev,d){const tt=d3.select("#tt");
      tt.style("opacity",1).style("left",(ev.offsetX+14)+"px").style("top",(ev.offsetY+8)+"px")
        .html("<b>"+esc(d.entity_name)+"</b><br>ID "+d.entity_id+" · "+d.record_count+" record(s)<br>"+d.data_sources.join(", "));})
    .on("mouseout",function(){d3.select("#tt").style("opacity",0);});
  node.append("circle").attr("r",radius).attr("fill",function(d){return color(d.data_sources[0]);});
  node.append("text").attr("dy",function(d){return radius(d)+11;}).attr("text-anchor","middle")
      .text(function(d){var n=d.entity_name||"";return n.length>20?n.slice(0,19)+"…":n;});
  sim.on("tick",function(){
    edge.select("line").attr("x1",function(d){return d.source.x;}).attr("y1",function(d){return d.source.y;})
      .attr("x2",function(d){return d.target.x;}).attr("y2",function(d){return d.target.y;});
    edge.select("text").attr("x",function(d){return (d.source.x+d.target.x)/2;}).attr("y",function(d){return (d.source.y+d.target.y)/2;});
    node.attr("transform",function(d){return "translate("+d.x+","+d.y+")";});
  });
  drawLegend();
  function dstart(ev,d){if(!ev.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;}
  function dragged(ev,d){d.fx=ev.x;d.fy=ev.y;}
  function dend(ev,d){if(!ev.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}
}
function radius(d){return Math.min(Math.max(8+d.record_count*4,8),40);}
function drawLegend(){d3.select("#graph-container .legend").remove();
  const srcs=Object.keys(SRC_COLORS);const l=d3.select("#graph-container").append("div").attr("class","legend");
  srcs.forEach(function(s){const r=l.append("div").attr("class","row");r.append("span").attr("class","dot").style("background",color(s));r.append("span").text(s);});}
function openModal(d){const m=d3.select("#modal");
  m.html("<h3>"+esc(d.entity_name)+"</h3><div class='muted'>Entity ID "+d.entity_id+"</div>"+
    "<p><b>Data sources:</b> "+d.data_sources.join(", ")+"<br><b>Records:</b> "+d.record_count+"</p>"+
    "<div>"+d.records.map(function(r){return "<span class='chip'>"+r.data_source+":"+r.record_id+"</span>";}).join("")+"</div>"+
    "<button onclick='closeModal()'>Close</button>");
  document.getElementById("modal-bg").style.display="flex";}
function closeModal(){document.getElementById("modal-bg").style.display="none";}
async function drawMerges(){const m=await getJSON("/api/merges");const box=d3.select("#merges");box.html("");
  if(!m.entities.length){box.append("p").attr("class","muted").text("No multi-record entities.");return;}
  m.entities.forEach(function(e){const card=box.append("div").attr("class","card");
    card.append("h4").text(e.entity_name+"  ");card.select("h4").append("span").attr("class","chip").text(e.data_sources.join(" + "));
    const rc=card.append("div").attr("class","recs");
    e.records.forEach(function(r){const d=rc.append("div").attr("class","rec");d.html("<b>"+r.data_source+"</b><br>record "+r.record_id);});});}
async function drawHist(){const s=await getJSON("/api/stats");const box=d3.select("#hist");box.html("");
  box.append("p").html("<b>"+s.records_total+"</b> records collapsed into <b>"+s.entities_total+"</b> entities, including <b>"+s.multi_record_entities+"</b> multi-record entities.");
  const data=[["1 record",s.histogram["1"]||0],["2 records",s.histogram["2"]||0],["3 records",s.histogram["3"]||0],["4+ records",s.histogram["4+"]||0]];
  const W=Math.min(720,box.node().clientWidth),H=300,m={t:20,r:10,b:40,l:44};
  const svg=box.append("svg").attr("width",W).attr("height",H);
  const x=d3.scaleBand().domain(data.map(function(d){return d[0];})).range([m.l,W-m.r]).padding(0.25);
  const y=d3.scaleLinear().domain([0,d3.max(data,function(d){return d[1];})||1]).nice().range([H-m.b,m.t]);
  svg.append("g").attr("transform","translate(0,"+(H-m.b)+")").call(d3.axisBottom(x));
  svg.append("g").attr("transform","translate("+m.l+",0)").call(d3.axisLeft(y).ticks(5));
  svg.selectAll("rect").data(data).join("rect").attr("x",function(d){return x(d[0]);}).attr("y",function(d){return y(d[1]);})
    .attr("width",x.bandwidth()).attr("height",function(d){return y(0)-y(d[1]);}).attr("rx",4)
    .attr("fill",function(d,i){return i===0?"#175ca8":"#c8922a";});
  svg.selectAll("text.v").data(data).join("text").attr("class","v").attr("x",function(d){return x(d[0])+x.bandwidth()/2;})
    .attr("y",function(d){return y(d[1])-6;}).attr("text-anchor","middle").attr("font-size",13).attr("font-weight",600).text(function(d){return d[1];});}
async function doSearch(){const q=document.getElementById("search-in").value;const box=d3.select("#results");box.html("<p class='muted'>Searching…</p>");
  const r=await getJSON("/api/search?q="+encodeURIComponent(q));box.html("");
  if(!r.results||!r.results.length){box.append("p").attr("class","muted").text("No matching entities found.");return;}
  r.results.forEach(function(e){const card=box.append("div").attr("class","card");
    card.append("h4").text(e.entity_name);
    card.append("div").attr("class","muted").text("Entity "+e.entity_id+" · "+(e.record_count||"?")+" record(s) · "+(e.data_sources||[]).join(", "));
    if(e.match_key){const mk=card.append("div").attr("class","mk");e.match_key.split(/(?=[+-])/).forEach(function(p){if(p)mk.append("span").text(p);});}
    if(e.resolution_rule)card.append("div").append("code").text(e.resolution_rule);});}
async function loadProbes(){const m=await getJSON("/api/merges");const box=d3.select("#probe-btns");box.html("");
  m.entities.slice(0,6).forEach(function(e){box.append("button").attr("class","probe").text(e.entity_name)
    .on("click",function(){document.getElementById("search-in").value=e.entity_name;doSearch();});});}
function esc(s){return (s||"").replace(/[&<>]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;"}[c];});}
loadBanner();drawGraph();drawMerges();loadProbes();
window.addEventListener("resize",function(){if(d3.select("#tab-graph").classed("active"))drawGraph();});
</script></body></html>
"""


def _d3_script():
    """Return an inline <script> carrying the vendored D3, so the visualization
    renders with no network access. Fall back to the CDN tag only if the vendored
    asset is missing."""
    vendored = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "vendor", "d3.v7.min.js"
    )
    try:
        with open(vendored, encoding="utf-8") as fh:
            return "<script>" + fh.read() + "</script>"
    except OSError:
        return '<script src="https://d3js.org/d3.v7.min.js"></script>'


def render_page(title, data_shim=""):
    # Replace D3 and the data shim LAST so their contents are never rescanned for
    # the other placeholders.
    return (
        PAGE.replace("__TITLE__", title)
        .replace("__SRC_COLORS__", json.dumps(SOURCE_COLORS))
        .replace("__DATA_SHIM__", data_shim)
        .replace("__D3_SCRIPT__", _d3_script())
    )


# --------------------------------------------------------------------------- #
# Server
# --------------------------------------------------------------------------- #
def make_handler(model, engine, flags, title):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):  # quiet
            pass

        def _send(self, code, body, ctype="application/json"):
            data = body.encode("utf-8") if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path
            try:
                if path in ("/", "/index.html"):
                    return self._send(200, render_page(title), "text/html; charset=utf-8")
                if path == "/api/stats":
                    return self._send(200, json.dumps(model.stats()))
                if path == "/api/graph":
                    return self._send(200, json.dumps(model.graph()))
                if path == "/api/merges":
                    return self._send(200, json.dumps(model.merges()))
                if path == "/api/search":
                    q = parse_qs(parsed.query).get("q", [""])[0]
                    return self._send(200, json.dumps(model.search(engine, flags, q)))
                return self._send(404, json.dumps({"error": "not found"}))
            except Exception as exc:  # never 500-crash silently
                return self._send(500, json.dumps({"error": str(exc)}))

    return Handler


def build_model(settings, patterns):
    from senzing import SzEngineFlags
    from senzing_core import SzAbstractFactoryCore

    # Keep the factory alive for the caller's lifetime: if it is garbage
    # collected, it destroys the engine it created ("engine object has been
    # destroyed"), which would break later /api/search requests.
    factory = SzAbstractFactoryCore("bootcamp_viz", settings, verbose_logging=False)
    engine = factory.create_engine()
    flags = SzEngineFlags.SZ_ENTITY_DEFAULT_FLAGS
    model = Model().build(engine, flags, _iter_record_keys(patterns))
    return factory, model, engine, flags


def write_snapshot(model, engine, flags, title, out_path):
    """Write a fully self-contained HTML snapshot with D3 and data embedded, so it
    renders with no server and no network access."""
    payload = {
        "stats": model.stats(),
        "graph": model.graph(),
        "merges": model.merges(),
    }
    # The embedded-data shim runs after D3 and before the page bootstrap, replacing
    # the fetch-based bootstrap with the inlined data.
    shim = (
        "<script>const __DATA__=" + json.dumps(payload) + ";"
        "window.fetch=function(u){var p=u.split('?')[0].replace('/api/','');"
        "var q=(u.split('?')[1]||'');"
        "if(p==='search'){return Promise.resolve({json:function(){return Promise.resolve({results:[]});}});}"
        "return Promise.resolve({json:function(){return Promise.resolve(__DATA__[p]);}});};</script>"
    )
    page = render_page(title, data_shim=shim)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(page)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--settings", default="config/engine_config.json")
    ap.add_argument("--records", nargs="+", required=True,
                    help="JSONL file(s)/glob(s) of the records that were loaded")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--title", default="Senzing Entity Resolution")
    ap.add_argument("--snapshot", default=None,
                    help="also write a self-contained standalone HTML to this path")
    ap.add_argument("--no-serve", action="store_true",
                    help="build the model (and snapshot) then exit without serving")
    args = ap.parse_args(argv)

    if os.path.exists(args.settings):
        settings = open(args.settings, encoding="utf-8").read()
    else:
        settings = os.getenv("SENZING_ENGINE_CONFIGURATION_JSON", "")
    if not settings:
        sys.stderr.write("No engine settings (missing --settings file and env var).\n")
        return 2

    try:
        factory, model, engine, flags = build_model(settings, args.records)
    except Exception as exc:
        sys.stderr.write(f"Could not build entity model: {type(exc).__name__}: {exc}\n")
        return 1
    # `factory` must stay referenced for the whole run so the engine survives.
    _ = factory

    s = model.stats()
    print(f"Entity model built: {s['records_total']} records, {s['entities_total']} entities, "
          f"{s['multi_record_entities']} merged, {s['cross_source_entities']} cross-source, "
          f"{s['relationships_total']} relationships")

    if args.snapshot:
        write_snapshot(model, engine, flags, args.title, args.snapshot)
        print(f"Snapshot written: {args.snapshot}")

    if args.no_serve:
        return 0

    handler = make_handler(model, engine, flags, args.title)
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Visualization running: http://localhost:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
