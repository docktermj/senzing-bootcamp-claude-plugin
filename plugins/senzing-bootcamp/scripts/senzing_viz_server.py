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

- ``GET /``            single-page D3 v7 visualization (all tabs + summary banner)
- ``GET /api/stats``   aggregate resolution statistics (incl. per-bucket entity lists
  under ``bucket_entities`` for the clickable histogram, and ``data_sources_total``)
- ``GET /api/graph``   entity nodes + relationship edges (Entity Graph + Relationship
  Network tabs)
- ``GET /api/merges``  multi-record entities with constituent records
- ``GET /api/search``  search-by-attributes with resolution reasoning
- ``GET /api/why``     explain WHY the records in an entity resolved together
  (``why_records`` / ``why_record_in_entity``); ``?entity_id=<id>``
- ``GET /api/how``     explain HOW an entity was constructed from its records
  (``how_entity_by_entity_id``); ``?entity_id=<id>``
- ``GET /api/dashboard``  entity/match counts + a sample of resolved entities
- ``GET /api/overlap``    cross-source overlap matrix (which sources share entities)
- ``GET /api/matchkeys``  match-key frequency (which feature combos drive resolutions)
- ``GET /api/features``   feature-score distribution across a capped sample of
  multi-record entities (from ``why_records``; degrades gracefully)

These endpoints back a single consolidated, tabbed visualization app — the one artifact
Module 7 offers for results visualization (it no longer produces separate static pages).
The Relationship Network tab reuses ``/api/graph`` (the related-entity subgraph); the
entity-size distribution is the Merge Statistics histogram (``/api/stats``), not a
separate view.

Data source: ``get_entity_by_record_id`` with ``SZ_ENTITY_DEFAULT_FLAGS`` (which
includes ``SZ_ENTITY_INCLUDE_ALL_RELATIONS``), so nodes and edges come from one
call per loaded record. No direct SQL is ever run against the database.

Usage:
    # Serve the live web app (Python reference; run directly only when the chosen language is Python — INV-090):
    python3 senzing_viz_server.py --records src/system_verification/truthset_data.jsonl

    # Also write a persistent standalone snapshot (no server needed to view):
    python3 senzing_viz_server.py --records data/senzing-ready/*.jsonl \\
        --snapshot docs/visualizations/results.html

    # Just build the snapshot and exit (no server), used by the completion gate:
    python3 senzing_viz_server.py --records src/system_verification/truthset_data.jsonl \\
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
        # Feature-score distribution, computed once (capped) after build via
        # compute_feature_dist(); an empty default keeps /api/features safe if it
        # was never computed or every why_records call failed (INV-077).
        self.feature_dist = {
            "features": [], "sampled": 0, "multi_record_total": 0, "capped": False
        }

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
                            # Per-record match key (how this record joined the
                            # entity); the seed record is typically empty. Drives
                            # the Match Keys tab. Present with the default entity
                            # flags' record-matching-info; falls back to "".
                            "match_key": r.get("MATCH_KEY", "") or "",
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
        all_sources = set()
        for e in ents:
            all_sources.update(e["data_sources"])
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
            # Distinct data-source count, so the client can decide whether the
            # Cross-Source tab is applicable (needs 2+ sources) without a second call.
            "data_sources_total": len(all_sources),
            "histogram": hist,
            "bucket_entities": buckets,
        }

    def dashboard(self):
        """Results-dashboard payload: headline counts, the records-per-entity
        histogram, and a sample of the largest resolved entities."""
        s = self.stats()
        sample = []
        for e in sorted(self.entities.values(), key=lambda x: -x["record_count"]):
            if e["record_count"] <= 1:
                continue
            sample.append(
                {
                    "entity_id": e["entity_id"],
                    "entity_name": e["entity_name"],
                    "record_count": e["record_count"],
                    "data_sources": e["data_sources"],
                }
            )
            if len(sample) >= 10:
                break
        return {
            "counts": {
                "records_total": s["records_total"],
                "entities_total": s["entities_total"],
                "multi_record_entities": s["multi_record_entities"],
                "cross_source_entities": s["cross_source_entities"],
                "relationships_total": s["relationships_total"],
            },
            "histogram": s["histogram"],
            "sample_entities": sample,
        }

    def overlap(self):
        """Cross-source overlap matrix: for each ordered pair of data sources, the
        number of resolved entities that contain records from both (diagonal = the
        entities present in that source)."""
        src_set = set()
        for e in self.entities.values():
            src_set.update(e["data_sources"])
        sources = sorted(src_set)
        idx = {s: i for i, s in enumerate(sources)}
        n = len(sources)
        matrix = [[0] * n for _ in range(n)]
        for e in self.entities.values():
            ds = sorted(set(e["data_sources"]))
            for s in ds:
                matrix[idx[s]][idx[s]] += 1
            for i in range(len(ds)):
                for j in range(i + 1, len(ds)):
                    a, b = idx[ds[i]], idx[ds[j]]
                    matrix[a][b] += 1
                    matrix[b][a] += 1
        return {"sources": sources, "matrix": matrix}

    def match_keys(self):
        """Match-key frequency: how often each per-record match key (e.g.
        '+NAME+ADDRESS') drove a resolution. Top keys only, with the distinct total."""
        counts = {}
        for e in self.entities.values():
            for r in e["records"]:
                mk = r.get("match_key") or ""
                if mk:
                    counts[mk] = counts.get(mk, 0) + 1
        items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return {
            "match_keys": [{"match_key": k, "count": v} for k, v in items[:20]],
            "distinct": len(counts),
            "capped": len(counts) > 20,
        }

    def feature_scores(self):
        """Return the pre-computed feature-score distribution (see
        compute_feature_dist). Safe before computation — returns the empty default."""
        return self.feature_dist

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

    def compute_feature_dist(self, engine, sz, cap=40):
        """Aggregate feature-score buckets across a **capped** sample of
        multi-record entities (via why_records) so the Feature Scores tab can show
        how tightly resolved records match. Fully guarded: any why failure skips
        that entity and never blocks the model/snapshot build (INV-077). The cap is
        surfaced to the UI (``sampled`` / ``multi_record_total`` / ``capped``) so
        the sample size is never hidden."""
        per_feature = {}   # feature -> {bucket: count}
        multi = [e for e in self.entities.values() if e["record_count"] > 1]
        multi.sort(key=lambda e: -e["record_count"])
        sampled = 0
        for e in multi:
            if sampled >= cap:
                break
            res = self.why(engine, sz, e["entity_id"])
            if not res or res.get("error") or "result" not in res:
                continue
            wr = (res.get("result") or {}).get("WHY_RESULTS") or []
            counted = False
            for w in wr:
                fs = (w.get("MATCH_INFO") or {}).get("FEATURE_SCORES") or {}
                for feat, scores in fs.items():
                    for sc in scores or []:
                        bucket = (sc.get("SCORE_BUCKET") or "").upper()
                        if not bucket:
                            continue
                        per_feature.setdefault(feat, {})
                        per_feature[feat][bucket] = per_feature[feat].get(bucket, 0) + 1
                        counted = True
            if counted:
                sampled += 1
        self.feature_dist = {
            "features": [
                {"feature": f, "buckets": per_feature[f]} for f in sorted(per_feature)
            ],
            "sampled": sampled,
            "multi_record_total": len(multi),
            "capped": len(multi) > cap,
        }
        return self.feature_dist


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
#graph-container,#network-container{position:relative;height:calc(100vh - 175px);min-height:360px;background:#fff;border:1px solid var(--line);border-radius:8px;overflow:hidden;padding:0}
#graph-container svg,#network-container svg{width:100%;height:100%;display:block}
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
nav{flex-wrap:wrap}
.kpis{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px}
.kpi{flex:1;min-width:130px;background:#fff;border:1px solid var(--line);border-radius:8px;padding:12px 14px}
.kpi .n{font-size:26px;font-weight:700;color:var(--blue)}
.kpi .l{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.03em}
.section-h{margin:16px 0 6px;font-size:14px}
.heat{border-collapse:collapse;font-size:12px;margin-top:8px}
.heat th,.heat td{border:1px solid var(--line);padding:6px 10px;text-align:center}
.heat th{background:var(--bg);color:var(--muted);font-weight:600}
.heat td.rowh{background:var(--bg);color:var(--muted);font-weight:600;text-align:right}
.heat td.cell{color:var(--ink);font-variant-numeric:tabular-nums}
</style></head>
<body>
<header><h1>__TITLE__</h1></header>
<div class="banner" id="banner"></div>
<nav id="nav"></nav>
<main>
  <section class="tab active" id="tab-graph"><div id="graph-container"><div class="tooltip" id="tt"></div></div></section>
  <section class="tab" id="tab-network"><div id="network-container"><div class="tooltip" id="tt2"></div></div></section>
  <section class="tab" id="tab-merges"><div id="merges"></div></section>
  <section class="tab" id="tab-stats"><div id="hist"></div></section>
  <section class="tab" id="tab-matchkeys"><div id="matchkeys"></div></section>
  <section class="tab" id="tab-features"><div id="features"></div></section>
  <section class="tab" id="tab-overlap"><div id="overlap"></div></section>
  <section class="tab" id="tab-dashboard"><div id="dashboard"></div></section>
  <section class="tab" id="tab-probe">__PROBE_BODY__</section>
</main>
<div class="modal-bg" id="modal-bg" onclick="if(event.target.id==='modal-bg')closeModal()"><div class="modal" id="modal"></div></div>
<script>
const ALL_TABS=[["graph","Entity Graph"],["network","Relationship Network"],["merges","Record Merges"],["stats","Merge Statistics"],["matchkeys","Match Keys"],["features","Feature Scores"],["overlap","Cross-Source"],["dashboard","Results Dashboard"],["probe","Search / Probe"]];
const SRC_COLORS=__SRC_COLORS__;
function color(src){return SRC_COLORS[src]||"#8b5cf6";}
const CSSV=getComputedStyle(document.documentElement);
function cssv(n,f){var v=CSSV.getPropertyValue(n).trim();return v||f;}
const C_BLUE=cssv('--blue','#F57826'),C_GOLD=cssv('--gold','#FF4E1F'),C_GREEN=cssv('--green','#1D9E75'),C_MUTED=cssv('--muted','#4A4640');
function hexRgb(h){h=(h||"").replace('#','');if(h.length===3)h=h.split('').map(function(c){return c+c;}).join('');var n=parseInt(h,16)||0;return [(n>>16)&255,(n>>8)&255,n&255];}
let STATS=null;
// A tab is shown only when its data exists: relationships for the network,
// 2+ sources for cross-source overlap, multi-record entities for match keys /
// feature scores. The others always apply.
function tabApplicable(id){const s=STATS||{};
  if(id==="network")return (s.relationships_total||0)>0;
  if(id==="overlap")return (s.data_sources_total||0)>=2;
  if(id==="features")return (s.multi_record_entities||0)>0;
  if(id==="matchkeys")return (s.multi_record_entities||0)>0;
  return true;}
function drawFor(id){
  if(id==="graph")drawGraph();
  else if(id==="network")drawNetwork();
  else if(id==="stats")drawHist();
  else if(id==="matchkeys")drawMatchKeys();
  else if(id==="features")drawFeatures();
  else if(id==="overlap")drawOverlap();
  else if(id==="dashboard")drawDashboard();}
function activate(id){d3.selectAll("nav button").classed("active",false);d3.select("#navbtn-"+id).classed("active",true);
  d3.selectAll(".tab").classed("active",false);d3.select("#tab-"+id).classed("active",true);drawFor(id);}
function buildNav(){const nav=d3.select("#nav");nav.html("");
  const tabs=ALL_TABS.filter(function(t){return tabApplicable(t[0]);});
  tabs.forEach(function(t,i){nav.append("button").attr("id","navbtn-"+t[0]).attr("class",i===0?"active":"").text(t[1]).on("click",function(){activate(t[0]);});});
  d3.selectAll(".tab").classed("active",false);if(tabs.length)d3.select("#tab-"+tabs[0][0]).classed("active",true);}
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
// Relationship Network: the subgraph of entities connected by relationships
// (possible matches / disclosed relations), edges colored by relationship type.
// Distinct from Entity Graph, which shows the full entity population.
async function drawNetwork(){
  const c=document.getElementById("network-container");const W=c.clientWidth,H=c.clientHeight;
  const g=await getJSON("/api/graph");const box=d3.select("#network-container");
  d3.select("#network-container svg").remove();d3.select("#network-container .legend").remove();
  const links0=g.edges.map(function(e){return {source:e.source_entity_id,target:e.target_entity_id,match_key:e.match_key,rtype:e.relationship_type||"RELATED"};});
  const connected=new Set();links0.forEach(function(e){connected.add(e.source);connected.add(e.target);});
  const nodes=g.nodes.filter(function(n){return connected.has(n.entity_id);}).map(function(n){return Object.assign({},n,{id:n.entity_id});});
  if(!nodes.length){box.append("div").attr("class","muted").style("padding","14px").text("No relationships between entities were found in this data.");return;}
  const idset=new Set(nodes.map(function(n){return n.id;}));
  const links=links0.filter(function(e){return idset.has(e.source)&&idset.has(e.target);});
  const rtypes=Array.from(new Set(links.map(function(e){return e.rtype;})));
  const rcolor=d3.scaleOrdinal().domain(rtypes).range([C_BLUE,C_GOLD,C_GREEN,"#8b5cf6","#ec4899","#0ea5e9"]);
  const svg=box.append("svg").attr("width",W).attr("height",H).attr("viewBox",[0,0,W,H]);
  const root=svg.append("g");
  svg.call(d3.zoom().scaleExtent([0.2,4]).on("zoom",function(ev){root.attr("transform",ev.transform);}));
  const sim=d3.forceSimulation(nodes)
    .force("link",d3.forceLink(links).id(function(d){return d.id;}).distance(100))
    .force("charge",d3.forceManyBody().strength(-180))
    .force("center",d3.forceCenter(W/2,H/2))
    .force("collide",d3.forceCollide().radius(function(d){return radius(d)+6;}));
  const edge=root.append("g").selectAll("g").data(links).join("g").attr("class","edge");
  edge.append("line").attr("stroke",function(d){return rcolor(d.rtype);}).attr("stroke-width",2);
  edge.append("text").text(function(d){return d.match_key||"";});
  const node=root.append("g").selectAll("g").data(nodes).join("g").attr("class","node")
    .call(d3.drag().on("start",ns).on("drag",nd).on("end",ne))
    .on("click",function(ev,d){openModal(d);})
    .on("mousemove",function(ev,d){const tt=d3.select("#tt2");
      tt.style("opacity",1).style("left",(ev.offsetX+14)+"px").style("top",(ev.offsetY+8)+"px")
        .html("<b>"+esc(d.entity_name)+"</b><br>ID "+d.entity_id+" · "+d.record_count+" record(s)<br>"+d.data_sources.join(", "));})
    .on("mouseout",function(){d3.select("#tt2").style("opacity",0);});
  node.append("circle").attr("r",radius).attr("fill",function(d){return color(d.data_sources[0]);});
  node.append("text").attr("dy",function(d){return radius(d)+11;}).attr("text-anchor","middle")
      .text(function(d){var n=d.entity_name||"";return n.length>20?n.slice(0,19)+"…":n;});
  sim.on("tick",function(){
    edge.select("line").attr("x1",function(d){return d.source.x;}).attr("y1",function(d){return d.source.y;})
      .attr("x2",function(d){return d.target.x;}).attr("y2",function(d){return d.target.y;});
    edge.select("text").attr("x",function(d){return (d.source.x+d.target.x)/2;}).attr("y",function(d){return (d.source.y+d.target.y)/2;});
    node.attr("transform",function(d){return "translate("+d.x+","+d.y+")";});
  });
  const l=box.append("div").attr("class","legend");
  l.append("div").style("font-weight","600").style("margin-bottom","3px").text("Relationship");
  rtypes.forEach(function(t){const r=l.append("div").attr("class","row");r.append("span").attr("class","dot").style("background",rcolor(t));r.append("span").text(humLevel(t));});
  function ns(ev,d){if(!ev.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;}
  function nd(ev,d){d.fx=ev.x;d.fy=ev.y;}
  function ne(ev,d){if(!ev.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}
}
// Cross-Source overlap heatmap: entities shared between each pair of data sources.
async function drawOverlap(){const o=await getJSON("/api/overlap");const box=d3.select("#overlap");box.html("");
  const src=o.sources||[],m=o.matrix||[];
  box.append("p").html("Each cell is the number of resolved entities that appear in <b>both</b> data sources; the diagonal is the entities present in that source.");
  if(src.length<2){box.append("p").attr("class","muted").text("Cross-source overlap needs at least two data sources.");return;}
  let max=1;for(let i=0;i<m.length;i++)for(let j=0;j<m.length;j++){if(i!==j&&m[i][j]>max)max=m[i][j];}
  const rgb=hexRgb(C_BLUE);
  const t=box.append("table").attr("class","heat");
  const head=t.append("thead").append("tr");head.append("th").text("");
  src.forEach(function(s){head.append("th").text(s);});
  const tb=t.append("tbody");
  src.forEach(function(s,i){const tr=tb.append("tr");tr.append("td").attr("class","rowh").text(s);
    src.forEach(function(_,j){const v=(m[i]&&m[i][j])||0;const td=tr.append("td").attr("class","cell").text(v);
      if(i===j){td.style("background","var(--bg)").style("font-weight","600");}
      else if(v>0){const a=0.15+0.85*v/max;td.style("background","rgba("+rgb[0]+","+rgb[1]+","+rgb[2]+","+a.toFixed(3)+")");if(a>0.55)td.style("color","#fff");}
    });});
}
// Results Dashboard: headline counts, records-per-entity histogram, sample entities.
async function drawDashboard(){const d=await getJSON("/api/dashboard");const box=d3.select("#dashboard");box.html("");
  const c=d.counts||{};
  const kpis=[["Records",c.records_total],["Entities",c.entities_total],["Multi-record",c.multi_record_entities],["Cross-source",c.cross_source_entities],["Relationships",c.relationships_total]];
  const kw=box.append("div").attr("class","kpis");
  kpis.forEach(function(k){const el=kw.append("div").attr("class","kpi");el.append("div").attr("class","n").text(k[1]!=null?k[1]:"—");el.append("div").attr("class","l").text(k[0]);});
  box.append("h3").attr("class","section-h").text("Records per entity");
  const hist=d.histogram||{};const data=[["1 record","1"],["2 records","2"],["3 records","3"],["4+ records","4+"]].map(function(z){return {label:z[0],n:hist[z[1]]||0};});
  const W=Math.min(560,box.node().clientWidth),H=220,mm={t:16,r:10,b:34,l:44};
  const svg=box.append("svg").attr("width",W).attr("height",H);
  const x=d3.scaleBand().domain(data.map(function(z){return z.label;})).range([mm.l,W-mm.r]).padding(0.25);
  const y=d3.scaleLinear().domain([0,d3.max(data,function(z){return z.n;})||1]).nice().range([H-mm.b,mm.t]);
  svg.append("g").attr("transform","translate(0,"+(H-mm.b)+")").call(d3.axisBottom(x));
  svg.append("g").attr("transform","translate("+mm.l+",0)").call(d3.axisLeft(y).ticks(5));
  svg.selectAll("rect").data(data).join("rect").attr("x",function(z){return x(z.label);}).attr("y",function(z){return y(z.n);})
    .attr("width",x.bandwidth()).attr("height",function(z){return y(0)-y(z.n);}).attr("rx",4).attr("fill",C_BLUE);
  svg.selectAll("text.v").data(data).join("text").attr("class","v").attr("x",function(z){return x(z.label)+x.bandwidth()/2;})
    .attr("y",function(z){return y(z.n)-6;}).attr("text-anchor","middle").attr("font-size",12).attr("font-weight",600).text(function(z){return z.n;});
  box.append("h3").attr("class","section-h").text("Largest resolved entities");
  const samp=d.sample_entities||[];
  if(!samp.length){box.append("p").attr("class","muted").text("No multi-record entities.");return;}
  const wrap=box.append("div").attr("class","recs");
  samp.forEach(function(e){const el=wrap.append("div").attr("class","rec");el.style("cursor","pointer");
    el.html("<b>"+esc(e.entity_name)+"</b><br>"+e.record_count+" records · "+(e.data_sources||[]).join(", "));
    el.on("click",function(){explain("how",e.entity_id,e.entity_name);});});
}
// Match Keys: which feature combinations drove the most resolutions.
async function drawMatchKeys(){const d=await getJSON("/api/matchkeys");const box=d3.select("#matchkeys");box.html("");
  const items=d.match_keys||[];
  box.append("p").html("Which feature combinations (match keys) drove the most resolutions across your data.");
  if(!items.length){box.append("p").attr("class","muted").text("No match keys were recorded for the resolved records.");return;}
  const W=Math.min(720,box.node().clientWidth),barh=26,mm={t:6,r:44,b:6,l:190},H=mm.t+mm.b+items.length*barh;
  const svg=box.append("svg").attr("width",W).attr("height",H);
  const x=d3.scaleLinear().domain([0,d3.max(items,function(z){return z.count;})||1]).range([mm.l,W-mm.r]);
  const y=d3.scaleBand().domain(items.map(function(z){return z.match_key;})).range([mm.t,H-mm.b]).padding(0.2);
  svg.selectAll("rect").data(items).join("rect").attr("x",mm.l).attr("y",function(z){return y(z.match_key);})
    .attr("width",function(z){return Math.max(0,x(z.count)-mm.l);}).attr("height",y.bandwidth()).attr("rx",3).attr("fill",C_BLUE);
  svg.selectAll("text.k").data(items).join("text").attr("class","k").attr("x",mm.l-8).attr("y",function(z){return y(z.match_key)+y.bandwidth()/2;})
    .attr("text-anchor","end").attr("dominant-baseline","middle").attr("font-size",11).attr("font-family","__CODE_FONT__").text(function(z){return z.match_key;});
  svg.selectAll("text.c").data(items).join("text").attr("class","c").attr("x",function(z){return x(z.count)+5;}).attr("y",function(z){return y(z.match_key)+y.bandwidth()/2;})
    .attr("dominant-baseline","middle").attr("font-size",11).attr("font-weight",600).text(function(z){return z.count;});
  if(d.capped)box.append("p").attr("class","muted").text("Showing the top "+items.length+" of "+d.distinct+" distinct match keys.");
}
// Feature Scores: how tightly each feature agreed across resolved records
// (from a capped why_records sample; the sample size is always shown).
async function drawFeatures(){const d=await getJSON("/api/features");const box=d3.select("#features");box.html("");
  const feats=d.features||[];
  box.append("p").html("How tightly each feature agreed across resolved records — greener means stronger agreement.");
  if(!feats.length){box.append("p").attr("class","muted").text("Feature-score details come from the live server; none were sampled (no multi-record entities, or the sample is unavailable in this snapshot).");return;}
  const order=["SAME","CLOSE","PLUS","LIKELY","PLAUSIBLE","UNLIKELY","NO_CHANCE"];
  const bcolor={SAME:"#137333",CLOSE:"#137333",PLUS:C_GREEN,LIKELY:"#8a6d00",PLAUSIBLE:"#a1440a",UNLIKELY:"#a50e0e",NO_CHANCE:"#a50e0e"};
  const rows=feats.map(function(f){const b=f.buckets||{};const total=Object.keys(b).reduce(function(s,k){return s+b[k];},0)||1;return {feature:f.feature,buckets:b,total:total};});
  const W=Math.min(720,box.node().clientWidth),barh=32,mm={t:6,r:10,b:6,l:130},H=mm.t+mm.b+rows.length*barh;
  const x=d3.scaleLinear().domain([0,1]).range([mm.l,W-mm.r]);
  const y=d3.scaleBand().domain(rows.map(function(z){return z.feature;})).range([mm.t,H-mm.b]).padding(0.25);
  const svg=box.append("svg").attr("width",W).attr("height",H);
  rows.forEach(function(r){let acc=0;const keys=order.filter(function(k){return r.buckets[k];}).concat(Object.keys(r.buckets).filter(function(k){return order.indexOf(k)<0;}));
    keys.forEach(function(k){const frac=r.buckets[k]/r.total;svg.append("rect").attr("x",x(acc)).attr("y",y(r.feature)).attr("width",Math.max(0,x(acc+frac)-x(acc))).attr("height",y.bandwidth()).attr("fill",bcolor[k]||C_MUTED).append("title").text(k+": "+r.buckets[k]);acc+=frac;});
    svg.append("text").attr("x",mm.l-8).attr("y",y(r.feature)+y.bandwidth()/2).attr("text-anchor","end").attr("dominant-baseline","middle").attr("font-size",12).attr("font-weight",600).text(r.feature);});
  box.append("p").attr("class","muted").text("Based on "+d.sampled+" of "+d.multi_record_total+" multi-record entities"+(d.capped?" (sampled to bound cost).":"."));
}
function esc(s){return (s||"").replace(/[&<>]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;"}[c];});}
async function init(){STATS=await getJSON("/api/stats");await loadBanner();buildNav();drawGraph();drawMerges();loadProbes();}
init();
window.addEventListener("resize",function(){
  if(d3.select("#tab-graph").classed("active"))drawGraph();
  else if(d3.select("#tab-network").classed("active"))drawNetwork();});
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
                if path == "/api/dashboard":
                    return self._send(200, json.dumps(model.dashboard()))
                if path == "/api/overlap":
                    return self._send(200, json.dumps(model.overlap()))
                if path == "/api/matchkeys":
                    return self._send(200, json.dumps(model.match_keys()))
                if path == "/api/features":
                    return self._send(200, json.dumps(model.feature_scores()))
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
    # Pre-compute the (capped) feature-score distribution so the Feature Scores tab
    # works in the live app and the offline snapshot. Guarded so a why failure or a
    # single-record-only data set never blocks the model/snapshot build (INV-077).
    try:
        model.compute_feature_dist(engine, SzEngineFlags)
    except Exception:
        pass
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
        "dashboard": model.dashboard(),
        "overlap": model.overlap(),
        "matchkeys": model.match_keys(),
        "features": model.feature_scores(),
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
