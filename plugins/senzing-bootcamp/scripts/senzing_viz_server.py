#!/usr/bin/env python3
"""Bundled Senzing entity-resolution visualization web app — the shipped reference.

Per INV-090 the Truth Set visualization server is built in the bootcamper's chosen
programming language, modeled on this reference and the ``visualization-api-reference.md``
contract; this Python script is run directly only when the chosen language is Python. It
delivers the standalone **Truth Set visualization module** (Module 3b) "wow moment" and is
reused for Module 7 result views. System Verification (Module 3) uses synthetic data and
does not visualize (INV-082/INV-087).

It builds an entity model from the records the bootcamper loaded (by looking each
one up through the Senzing SDK, so all data comes from real entity resolution),
then serves:

- ``GET /``            single-page D3 v7 visualization (4 tabs + summary banner)
- ``GET /api/stats``   aggregate resolution statistics (incl. per-bucket entity lists
  under ``bucket_entities`` for the clickable histogram)
- ``GET /api/graph``   entity nodes + relationship edges
- ``GET /api/merges``  multi-record entities with constituent records
- ``GET /api/search``  search-by-attributes with resolution reasoning
- ``GET /api/why``     explain WHY the records in an entity resolved together
  (``why_records`` / ``why_record_in_entity``); ``?entity_id=<id>``
- ``GET /api/how``     explain HOW an entity was constructed from its records
  (``how_entity_by_entity_id``); ``?entity_id=<id>``

Data source: ``get_entity_by_record_id`` with ``SZ_ENTITY_DEFAULT_FLAGS`` (which
includes ``SZ_ENTITY_INCLUDE_ALL_RELATIONS``), so nodes and edges come from one
call per loaded record. No direct SQL is ever run against the database.

Usage:
    # Serve the live web app (Python reference; run directly only when the chosen language is Python — INV-090):
    python3 senzing_viz_server.py --records src/system_verification/*.jsonl

    # Also write a persistent standalone snapshot (no server needed to view):
    python3 senzing_viz_server.py --records data/senzing-ready/*.jsonl \\
        --snapshot docs/visualizations/results.html

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

# Brand tokens ship in this same directory. Import them so the visualization shares
# the Senzing style guide's palette with the recap PDF; fall back to an inlined copy
# of the same values if the module is ever unavailable, so this script keeps working
# in isolation (mirrors the vendored-D3 offline fallback).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import brand_tokens as _bt

    SOURCE_COLORS = dict(_bt.SOURCE_COLORS)
    FALLBACK_COLORS = list(_bt.FALLBACK_COLORS)
    _BRAND = {
        "bg": _bt.WARM_OFF_WHITE, "surface": _bt.WHITE, "dark": _bt.DEEP,
        "ink": _bt.DARK_INK, "muted": _bt.BODY_INK, "accent": _bt.EMBER_CORE,
        "accent_hot": _bt.EMBER_HOT, "accent_soft": _bt.EMBER_SOFT,
        "line": _bt.WARM_LINE, "green": _bt.SIGNAL_GREEN,
        "font": _bt.FONT_STACK, "code_font": _bt.CODE_FONT_STACK,
    }
except Exception:  # defensive fallback — keep values in sync with brand_tokens.py
    SOURCE_COLORS = {"CUSTOMERS": "#F57826", "REFERENCE": "#3B6EA5", "WATCHLIST": "#C8922A"}
    FALLBACK_COLORS = ["#8b5cf6", "#ec4899", "#0ea5e9", "#a3a34a", "#ef4444", "#14b8a6"]
    _BRAND = {
        "bg": "#FAF8F3", "surface": "#FFFFFF", "dark": "#18160F",
        "ink": "#18160F", "muted": "#4A4640", "accent": "#F57826",
        "accent_hot": "#FF4E1F", "accent_soft": "#FDEEE3",
        "line": "#E5DFD3", "green": "#1D9E75",
        "font": "Roboto, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif",
        "code_font": "'Fira Code', 'Courier New', Courier, monospace",
    }


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
        ents = list(self.entities.values())
        hist = {"1": 0, "2": 0, "3": 0, "4+": 0}
        # Per-bucket entity lists so the histogram bars can be clicked to drill
        # down. Capped per bucket to bound the payload (and the embedded snapshot);
        # the `histogram` counts remain authoritative.
        buckets = {"1": [], "2": [], "3": [], "4+": []}
        for e in ents:
            c = e["record_count"]
            b = "4+" if c >= 4 else str(c)
            hist[b] = hist.get(b, 0) + 1
            if len(buckets[b]) < 200:
                buckets[b].append(
                    {
                        "entity_id": e["entity_id"],
                        "entity_name": e["entity_name"],
                        "record_count": c,
                    }
                )
        return {
            "records_total": self.records_total,
            "entities_total": len(self.entities),
            "multi_record_entities": sum(1 for e in ents if e["record_count"] > 1),
            "cross_source_entities": sum(1 for e in ents if len(e["data_sources"]) >= 2),
            "relationships_total": len(self.edges),
            "histogram": hist,
            "bucket_entities": buckets,
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

    def how(self, engine, sz, entity_id):
        """Explain HOW an entity was constructed from its records
        (SzEngine.how_entity_by_entity_id, SZ_HOW_ENTITY_DEFAULT_FLAGS)."""
        try:
            eid = int(entity_id)
        except (TypeError, ValueError):
            return {"error": "invalid entity_id"}
        try:
            raw = engine.how_entity_by_entity_id(eid, sz.SZ_HOW_ENTITY_DEFAULT_FLAGS)
            return {"entity_id": eid, "result": json.loads(raw)}
        except Exception as exc:
            return {"entity_id": eid, "error": "%s: %s" % (type(exc).__name__, exc)}

    def why(self, engine, sz, entity_id):
        """Explain WHY the records in an entity resolved together. Uses
        SzEngine.why_records between two of the entity's constituent records, or
        why_record_in_entity for a single-record entity (both feature-scored)."""
        try:
            eid = int(entity_id)
        except (TypeError, ValueError):
            return {"error": "invalid entity_id"}
        recs = (self.entities.get(eid) or {}).get("records", [])
        try:
            if len(recs) >= 2:
                (d1, r1), (d2, r2) = (
                    (recs[0]["data_source"], recs[0]["record_id"]),
                    (recs[1]["data_source"], recs[1]["record_id"]),
                )
                raw = engine.why_records(d1, r1, d2, r2, sz.SZ_WHY_RECORDS_DEFAULT_FLAGS)
                mode = "why_records"
            elif len(recs) == 1:
                raw = engine.why_record_in_entity(
                    recs[0]["data_source"],
                    recs[0]["record_id"],
                    sz.SZ_WHY_RECORD_IN_ENTITY_DEFAULT_FLAGS,
                )
                mode = "why_record_in_entity"
            else:
                return {"entity_id": eid, "error": "no records known for this entity"}
            return {"entity_id": eid, "mode": mode, "result": json.loads(raw)}
        except Exception as exc:
            return {"entity_id": eid, "error": "%s: %s" % (type(exc).__name__, exc)}


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
:root{__ROOT_VARS__}
*{box-sizing:border-box}
body{margin:0;font-family:__FONT_STACK__;color:var(--ink);background:var(--bg)}
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
.edge line{stroke:var(--line);stroke-width:1.5px}
.edge text{font-size:9px;fill:var(--muted)}
.tooltip{position:absolute;pointer-events:none;background:var(--navy);color:#fff;padding:6px 9px;border-radius:6px;font-size:12px;opacity:0;max-width:240px}
.card{background:#fff;border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin-bottom:10px}
.card h4{margin:0 0 6px;font-size:15px}
.recs{display:flex;gap:10px;flex-wrap:wrap}
.rec{border:1px solid var(--line);border-radius:6px;padding:8px 10px;font-size:12px;min-width:150px;background:var(--bg)}
.chip{display:inline-block;border:1px solid var(--blue);color:var(--blue);background:var(--accent-soft);border-radius:12px;padding:1px 8px;font-size:11px;margin:2px 2px 0 0;font-family:__CODE_FONT__}
.mk span{display:inline-block;border:1px solid var(--gold);background:var(--accent-soft);color:var(--ink);border-radius:4px;padding:0 5px;margin:1px;font-family:__CODE_FONT__;font-size:11px}
#search-in{padding:8px 10px;border:1px solid var(--line);border-radius:6px;font-size:14px;width:min(420px,100%)}
button.probe{border:1px solid var(--line);background:#fff;border-radius:16px;padding:5px 12px;margin:2px;cursor:pointer;font-size:13px}
.muted{color:var(--muted)}
.modal-bg{position:fixed;inset:0;background:rgba(15,13,12,.5);display:none;align-items:center;justify-content:center;z-index:50}
.modal{background:#fff;border-radius:10px;padding:18px 20px;max-width:420px;width:90%}
.modal h3{margin:0 0 8px}
.modal button{margin-top:10px;border:none;background:var(--blue);color:#fff;border-radius:6px;padding:6px 12px;cursor:pointer}
.modal.wide{max-width:680px}
.actions{margin-top:8px;display:flex;gap:6px}
.actions button{border:1px solid var(--blue);background:var(--accent-soft);color:var(--blue);border-radius:6px;padding:3px 10px;font-size:12px;cursor:pointer}
.explain pre{max-height:52vh;overflow:auto;background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:8px;font-family:__CODE_FONT__;font-size:11px;white-space:pre-wrap;word-break:break-word}
.bucket-list{margin-top:14px}
.bucket-list .rec{cursor:pointer}
.explain h4{margin:12px 0 4px}
.explain details{margin-top:14px}
.explain summary{cursor:pointer;color:var(--muted);font-size:12px}
.legend-note{font-size:12px;color:var(--muted);margin:6px 0 0}
.verdict{border-left:4px solid var(--blue);background:var(--accent-soft);padding:8px 12px;border-radius:0 6px 6px 0;margin:4px 0 10px}
.why-table{width:100%;border-collapse:collapse;margin-top:8px;font-size:13px}
.why-table th,.why-table td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
.why-table th{background:var(--bg);font-size:10px;text-transform:uppercase;letter-spacing:.03em;color:var(--muted)}
.why-table td.feat{font-weight:600;white-space:nowrap}
.score-bar{height:7px;border-radius:4px;background:var(--line);overflow:hidden;margin-top:4px}
.score-bar>span{display:block;height:100%}
.bucket{display:inline-block;border-radius:10px;padding:1px 8px;font-size:11px;font-weight:600;border:1px solid transparent}
.b-strong{background:#e6f4ea;color:#137333;border-color:#cdebd6}
.b-mid{background:#fef7e0;color:#8a6d00;border-color:#f3e2a6}
.b-weak{background:#fdeee3;color:#a1440a;border-color:#f6cfae}
.b-none{background:#fce8e6;color:#a50e0e;border-color:#f4c7c3}
.step{border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:8px 0;background:#fff}
.step .num{display:inline-block;background:var(--blue);color:#fff;border-radius:50%;width:22px;height:22px;line-height:22px;text-align:center;font-weight:700;font-size:12px;margin-right:6px}
</style></head>
<body>
<header><h1>__TITLE__</h1></header>
<div class="banner" id="banner"></div>
<nav id="nav"></nav>
<main>
  <section class="tab active" id="tab-graph"><div id="graph-container"><div class="tooltip" id="tt"></div></div></section>
  <section class="tab" id="tab-merges"><div id="merges"></div></section>
  <section class="tab" id="tab-stats"><div id="hist"></div></section>
  <section class="tab" id="tab-probe">__PROBE_BODY__</section>
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
function openModal(d){const m=d3.select("#modal");document.getElementById("modal").className="modal";
  m.html("<h3>"+esc(d.entity_name)+"</h3><div class='muted'>Entity ID "+d.entity_id+"</div>"+
    "<p><b>Data sources:</b> "+d.data_sources.join(", ")+"<br><b>Records:</b> "+d.record_count+"</p>"+
    "<div>"+d.records.map(function(r){return "<span class='chip'>"+r.data_source+":"+r.record_id+"</span>";}).join("")+"</div>"+
    "<button onclick='closeModal()'>Close</button>");
  document.getElementById("modal-bg").style.display="flex";}
function closeModal(){document.getElementById("modal-bg").style.display="none";}
function addExplainButtons(sel,eid,name){if(eid===undefined||eid===null)return;
  const a=sel.append("div").attr("class","actions");
  a.append("button").attr("title","Why did these records resolve together?").text("Why?").on("click",function(){explain("why",eid,name);});
  a.append("button").attr("title","How was this entity constructed?").text("How?").on("click",function(){explain("how",eid,name);});}
function explainTitle(kind){return kind==="why"?"Why did these records resolve together?":"How was this entity built?";}
async function explain(kind,eid,name){const m=d3.select("#modal");
  document.getElementById("modal").className="modal wide explain";
  const head="<h3>"+esc(explainTitle(kind))+"</h3><div class='muted'>"+esc(name||"")+" · Entity "+eid+"</div>";
  m.html(head+"<p class='muted'>Loading…</p>");document.getElementById("modal-bg").style.display="flex";
  let data;try{data=await getJSON("/api/"+kind+"?entity_id="+encodeURIComponent(eid));}catch(e){data={error:String(e)};}
  let html=head;
  if(data&&data.error){html+="<p class='muted'>"+esc(data.error)+"</p>";}
  else{html+=(kind==="why"?renderWhy(data):renderHow(data));
    html+="<details><summary>Show the raw Senzing response (JSON)</summary><pre>"+esc(JSON.stringify(data&&data.result!==undefined?data.result:data,null,2))+"</pre></details>";}
  html+="<button onclick='closeModal()'>Close</button>";m.html(html);}
function mkChips(mk){return (mk||"").split(/(?=[+-])/).filter(function(p){return p;})
  .map(function(p){return "<span class='chip'>"+esc(p)+"</span>";}).join("")||"<span class='muted'>(none)</span>";}
function humLevel(l){return ({RESOLVED:"the same entity",POSSIBLY_SAME:"possibly the same entity",
  POSSIBLY_RELATED:"possibly related",DISCLOSED_RELATION:"a disclosed relationship",
  NO_RELATION:"not related"})[l]||(l?l.toLowerCase().replace(/_/g," "):"related");}
function bucketMeta(b){b=(b||"").toUpperCase();
  if(b==="SAME")return ["b-strong","#137333","Same"];
  if(b==="CLOSE")return ["b-strong","#137333","Close"];
  if(b==="LIKELY")return ["b-mid","#8a6d00","Likely"];
  if(b==="PLAUSIBLE")return ["b-weak","#a1440a","Plausible"];
  if(b==="NO_CHANCE"||b==="UNLIKELY")return ["b-none","#a50e0e","No match"];
  return ["b-mid","#8a6d00",b||"—"];}
function renderWhy(data){const wr=((data.result||{}).WHY_RESULTS)||[];
  if(!wr.length)return "<p class='muted'>Senzing returned no comparison detail for these records.</p>";
  const mi=wr[0].MATCH_INFO||{};const key=mi.WHY_KEY||mi.MATCH_KEY||"";const rule=mi.WHY_ERRULE_CODE||mi.ERRULE_CODE||"";const level=mi.MATCH_LEVEL_CODE||"";
  let h="<div class='verdict'>Senzing considers these records <b>"+esc(humLevel(level))+"</b> — on match key "+mkChips(key)+(rule?" (rule <code>"+esc(rule)+"</code>)":"")+".</div>";
  const fs=mi.FEATURE_SCORES||{};const feats=Object.keys(fs);
  if(feats.length){
    h+="<h4>Feature-by-feature comparison</h4>";
    h+="<table class='why-table'><thead><tr><th>Feature</th><th>Record A</th><th>Record B</th><th>How well it matched</th></tr></thead><tbody>";
    feats.forEach(function(ft){(fs[ft]||[]).forEach(function(sc){
      const bm=bucketMeta(sc.SCORE_BUCKET);const sv=(sc.SCORE===0||sc.SCORE)?sc.SCORE:"";
      h+="<tr><td class='feat'>"+esc(ft)+"</td><td>"+esc(sc.INBOUND_FEAT_DESC||"")+"</td><td>"+esc(sc.CANDIDATE_FEAT_DESC||"")+"</td>"+
        "<td><span class='bucket "+bm[0]+"'>"+esc(bm[2])+(sv!==""?" · "+sv:"")+"</span>"+
        (sv!==""?"<div class='score-bar'><span style='width:"+Math.max(3,Math.min(100,sv))+"%;background:"+bm[1]+"'></span></div>":"")+"</td></tr>";
    });});
    h+="</tbody></table><p class='legend-note'>Each row compares one feature across the two records. The score (0–100) and its bucket show how strongly that feature agreed — green = strong, amber = likely, orange = plausible, red = no match.</p>";
  }
  return h;}
function _recordChips(members){var out=[];(members||[]).forEach(function(mb){(mb.RECORDS||[]).forEach(function(r){
  out.push("<span class='chip'>"+esc((r.DATA_SOURCE||"?")+":"+(r.RECORD_ID||"?"))+"</span>");});});
  return out.join("")||"<span class='muted'>—</span>";}
function renderHow(data){const hr=(data.result||{}).HOW_RESULTS||{};const steps=hr.RESOLUTION_STEPS||[];
  if(steps.length){
    let h="<div class='verdict'>Senzing built this entity in <b>"+steps.length+"</b> step(s), each merging two groups of records.</div>";
    steps.forEach(function(st,i){const mi=st.MATCH_INFO||{};const mk=mi.MATCH_KEY||"";const rule=mi.ERRULE_CODE||"";
      const v1=st.VIRTUAL_ENTITY_1||{};const v2=st.VIRTUAL_ENTITY_2||{};
      h+="<div class='step'><div><span class='num'>"+(st.STEP||(i+1))+"</span><b>Merged on</b> "+mkChips(mk)+(rule?" · <code>"+esc(rule)+"</code>":"")+"</div>"+
        "<div class='recs' style='margin-top:8px'><div class='rec'><b>Group A</b><br>"+_recordChips(v1.MEMBER_RECORDS)+"</div>"+
        "<div class='rec'><b>Group B</b><br>"+_recordChips(v2.MEMBER_RECORDS)+"</div></div></div>";});
    return h;}
  const ve=((hr.FINAL_STATE||{}).VIRTUAL_ENTITIES)||[];
  var members=[];ve.forEach(function(v){(v.MEMBER_RECORDS||[]).forEach(function(m){members.push(m);});});
  var n=0;members.forEach(function(m){n+=((m.RECORDS||[]).length);});
  return "<div class='verdict'>These records resolved <b>directly</b> into one entity — Senzing found them consistent enough to merge with no intermediate steps.</div>"+
    "<h4>"+n+" record"+(n===1?"":"s")+" in this entity</h4>"+
    "<div class='recs'><div class='rec' style='min-width:auto'>"+_recordChips(members)+"</div></div>";}
async function drawMerges(){const m=await getJSON("/api/merges");const box=d3.select("#merges");box.html("");
  if(!m.entities.length){box.append("p").attr("class","muted").text("No multi-record entities.");return;}
  m.entities.forEach(function(e){const card=box.append("div").attr("class","card");
    card.append("h4").text(e.entity_name+"  ");card.select("h4").append("span").attr("class","chip").text(e.data_sources.join(" + "));
    const rc=card.append("div").attr("class","recs");
    e.records.forEach(function(r){const d=rc.append("div").attr("class","rec");d.html("<b>"+r.data_source+"</b><br>record "+r.record_id);});
    addExplainButtons(card,e.entity_id,e.entity_name);});}
async function drawHist(){const s=await getJSON("/api/stats");const box=d3.select("#hist");box.html("");
  box.append("p").html("<b>"+s.records_total+"</b> records collapsed into <b>"+s.entities_total+"</b> entities, including <b>"+s.multi_record_entities+"</b> multi-record entities.");
  box.append("p").attr("class","muted").text("Click a bar to list the entities in that bucket.");
  const data=[["1 record","1"],["2 records","2"],["3 records","3"],["4+ records","4+"]]
    .map(function(z){return {label:z[0],key:z[1],n:s.histogram[z[1]]||0};});
  const W=Math.min(720,box.node().clientWidth),H=300,m={t:20,r:10,b:40,l:44};
  const svg=box.append("svg").attr("width",W).attr("height",H);
  const x=d3.scaleBand().domain(data.map(function(d){return d.label;})).range([m.l,W-m.r]).padding(0.25);
  const y=d3.scaleLinear().domain([0,d3.max(data,function(d){return d.n;})||1]).nice().range([H-m.b,m.t]);
  svg.append("g").attr("transform","translate(0,"+(H-m.b)+")").call(d3.axisBottom(x));
  svg.append("g").attr("transform","translate("+m.l+",0)").call(d3.axisLeft(y).ticks(5));
  svg.selectAll("rect").data(data).join("rect").attr("x",function(d){return x(d.label);}).attr("y",function(d){return y(d.n);})
    .attr("width",x.bandwidth()).attr("height",function(d){return y(0)-y(d.n);}).attr("rx",4).style("cursor","pointer")
    .attr("fill",function(d,i){return i===0?"__ACCENT__":"__ACCENT_HOT__";})
    .on("click",function(ev,d){showBucket(s,d.key,d.label);});
  svg.selectAll("text.v").data(data).join("text").attr("class","v").attr("x",function(d){return x(d.label)+x.bandwidth()/2;})
    .attr("y",function(d){return y(d.n)-6;}).attr("text-anchor","middle").attr("font-size",13).attr("font-weight",600).text(function(d){return d.n;});
  box.append("div").attr("id","bucket-list").attr("class","bucket-list");}
function showBucket(s,key,label){const box=d3.select("#bucket-list");if(box.empty())return;box.html("");
  const list=(s.bucket_entities&&s.bucket_entities[key])||[];
  const total=(s.histogram&&s.histogram[key])||list.length;
  box.append("h4").text(label+" — "+total+(total===1?" entity":" entities"));
  if(!list.length){box.append("p").attr("class","muted").text("No entities in this bucket.");return;}
  const wrap=box.append("div").attr("class","recs");
  list.forEach(function(en){const d=wrap.append("div").attr("class","rec");
    d.html("<b>"+esc(en.entity_name)+"</b><br>ID "+en.entity_id+" · "+en.record_count+" record(s)");
    d.on("click",function(){explain("how",en.entity_id,en.entity_name);});});
  if(total>list.length)box.append("p").attr("class","muted").text("Showing first "+list.length+" of "+total+".");}
async function doSearch(){const q=document.getElementById("search-in").value;const box=d3.select("#results");box.html("<p class='muted'>Searching…</p>");
  const r=await getJSON("/api/search?q="+encodeURIComponent(q));box.html("");
  if(!r.results||!r.results.length){box.append("p").attr("class","muted").text("No matching entities found.");return;}
  r.results.forEach(function(e){const card=box.append("div").attr("class","card");
    card.append("h4").text(e.entity_name);
    card.append("div").attr("class","muted").text("Entity "+e.entity_id+" · "+(e.record_count||"?")+" record(s) · "+(e.data_sources||[]).join(", "));
    if(e.match_key){const mk=card.append("div").attr("class","mk");e.match_key.split(/(?=[+-])/).forEach(function(p){if(p)mk.append("span").text(p);});}
    if(e.resolution_rule)card.append("div").append("code").text(e.resolution_rule);
    addExplainButtons(card,e.entity_id,e.entity_name);});}
async function loadProbes(){const m=await getJSON("/api/merges");const box=d3.select("#probe-btns");box.html("");
  m.entities.slice(0,6).forEach(function(e){box.append("button").attr("class","probe").text(e.entity_name)
    .on("click",function(){document.getElementById("search-in").value=e.entity_name;doSearch();});});}
function esc(s){return (s||"").replace(/[&<>]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;"}[c];});}
loadBanner();drawGraph();drawMerges();loadProbes();
window.addEventListener("resize",function(){if(d3.select("#tab-graph").classed("active"))drawGraph();});
</script></body></html>
"""


# The live Search/Probe tab: an interactive search box backed by /api/search.
PROBE_BODY_LIVE = (
    '<div style="margin-bottom:10px">'
    '<input id="search-in" placeholder="Search a name (e.g. Robert Smith)"> '
    '<button class="probe" onclick="doSearch()">Search</button></div>'
    '<div id="probe-btns"></div><div id="results"></div>'
)


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


def render_page(title, data_shim="", probe_body=None):
    # Replace D3 and the data shim LAST so their contents are never rescanned for
    # the other placeholders.
    root_vars = (
        "--navy:%(dark)s;--blue:%(accent)s;--gold:%(accent_hot)s;--ink:%(ink)s;"
        "--muted:%(muted)s;--line:%(line)s;--bg:%(bg)s;--accent-soft:%(accent_soft)s;"
        "--green:%(green)s" % _BRAND
    )
    return (
        PAGE.replace("__TITLE__", title)
        .replace("__PROBE_BODY__", probe_body if probe_body is not None else PROBE_BODY_LIVE)
        .replace("__ROOT_VARS__", root_vars)
        .replace("__FONT_STACK__", _BRAND["font"])
        .replace("__CODE_FONT__", _BRAND["code_font"])
        .replace("__ACCENT_HOT__", _BRAND["accent_hot"])
        .replace("__ACCENT__", _BRAND["accent"])
        .replace("__SRC_COLORS__", json.dumps(SOURCE_COLORS))
        .replace("__DATA_SHIM__", data_shim)
        .replace("__D3_SCRIPT__", _d3_script())
    )


# --------------------------------------------------------------------------- #
# Server
# --------------------------------------------------------------------------- #
def make_handler(model, engine, flags, sz, title):
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
                if path == "/api/why":
                    eid = parse_qs(parsed.query).get("entity_id", [""])[0]
                    return self._send(200, json.dumps(model.why(engine, sz, eid)))
                if path == "/api/how":
                    eid = parse_qs(parsed.query).get("entity_id", [""])[0]
                    return self._send(200, json.dumps(model.how(engine, sz, eid)))
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
    # Return the flags class too, so the why/how endpoints can use the
    # MCP-confirmed default flag groups (SZ_HOW_ENTITY_DEFAULT_FLAGS, etc.).
    return factory, model, engine, flags, SzEngineFlags


def _esc_html(s):
    return (
        str("" if s is None else s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _match_key_chips(match_key):
    """Split a Senzing match key (e.g. '+NAME+ADDRESS-DOB') into <span> chips,
    mirroring the live app's doSearch() rendering."""
    mk = match_key or ""
    parts, cur = [], ""
    for ch in mk:
        if ch in "+-":
            if cur:
                parts.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        parts.append(cur)
    return "".join("<span>" + _esc_html(p) + "</span>" for p in parts if p)


def _result_card(searched, res):
    """Render one pre-rendered example search-result card (mirrors doSearch())."""
    rc = res.get("record_count")
    html = ['<div class="card">']
    html.append(
        '<div class="muted" style="margin-bottom:4px">Searched: <b>'
        + _esc_html(searched)
        + "</b></div>"
    )
    html.append("<h4>" + _esc_html(res.get("entity_name", "?")) + "</h4>")
    html.append(
        '<div class="muted">Entity '
        + _esc_html(res.get("entity_id"))
        + " · "
        + _esc_html(rc if rc is not None else "?")
        + " record(s) · "
        + _esc_html(", ".join(res.get("data_sources") or []))
        + "</div>"
    )
    if res.get("match_key"):
        html.append('<div class="mk">' + _match_key_chips(res["match_key"]) + "</div>")
    if res.get("resolution_rule"):
        html.append("<div><code>" + _esc_html(res["resolution_rule"]) + "</code></div>")
    html.append("</div>")
    return "".join(html)


def _snapshot_probe_html(model, engine, flags):
    """Build the static snapshot's Search/Probe tab: a note plus a fixed set of
    pre-rendered example search results (no live search box, which cannot work in a
    static file). Examples are drawn from this snapshot's own multi-record entities
    and enriched via a real search so the match keys are truthful; if a search
    cannot run, the card falls back to the merge data (no match key)."""
    merges = model.merges().get("entities", [])
    # Prefer cross-source merges (the most interesting), then the rest, by size.
    ordered = sorted(
        merges,
        key=lambda e: (len(e.get("data_sources", [])) < 2, -e.get("record_count", 0)),
    )
    cards = []
    for ent in ordered:
        if len(cards) >= 5:
            break
        name = ent.get("entity_name") or ""
        if not name:
            continue
        res = None
        try:
            hits = model.search(engine, flags, name).get("results", [])
            res = next(
                (h for h in hits if h.get("entity_id") == ent.get("entity_id")),
                hits[0] if hits else None,
            )
        except Exception:
            res = None
        if res is None:  # search unavailable — render from the merge data itself
            res = {
                "entity_id": ent.get("entity_id"),
                "entity_name": name,
                "record_count": ent.get("record_count"),
                "data_sources": ent.get("data_sources", []),
                "match_key": "",
                "resolution_rule": "",
            }
        cards.append(_result_card(name, res))
    note = (
        '<p class="muted">This is a saved snapshot, so live search is disabled. Below are '
        "example searches run against this Truth Set. In the live app "
        "(<code>http://localhost:8080</code>) you can search any name.</p>"
    )
    if not cards:
        return note + '<p class="muted">No multi-record entities to show.</p>'
    return note + '<div id="results">' + "".join(cards) + "</div>"


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
        "if(p==='why'||p==='how'){return Promise.resolve({json:function(){return Promise.resolve({error:'Why/How explanations run only against the live visualization server (start it with: python3 senzing_viz_server.py --records ...).'});}});}"
        "return Promise.resolve({json:function(){return Promise.resolve(__DATA__[p]);}});};</script>"
    )
    page = render_page(
        title, data_shim=shim, probe_body=_snapshot_probe_html(model, engine, flags)
    )
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
        factory, model, engine, flags, sz = build_model(settings, args.records)
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

    handler = make_handler(model, engine, flags, sz, args.title)
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
