#!/usr/bin/env python3
"""Entry-level classification of within-E1 JAR pairs (RQ2, phase 1).

For each project in data/e1-extracts/<dir>/<proj>/E1/build-{1,2}/artifacts/,
pairs JARs by filename and compares zip entries:
  - membership (entry name sets)
  - order (entry name sequence)
  - content (sha256 of each entry's data)
  - timestamps (ZipInfo.date_time per entry)
Classification per pair:
  IDENTICAL, TIMESTAMP_ONLY, ORDERING, ORDERING+TIMESTAMP, CONTENT, MIXED
(CONTENT = any entry content differs; MIXED = content + order/timestamp.)

Usage: classify-entries.py [extract-dir ...]  (default: all p*-e1 dirs except p6-bootui-e1)
Writes: analysis/classification/entries-<tag>.json per project + entries-summary.md
"""
import hashlib, json, os, sys, zipfile
from collections import Counter

BASE = os.path.expanduser("~/workspace/eb1a-reproducibility-study")
OUT = os.path.join(BASE, "analysis", "classification")
os.makedirs(OUT, exist_ok=True)

def entries(path):
    out = []
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            data = z.read(info.filename)
            out.append({
                "name": info.filename,
                "sha": hashlib.sha256(data).hexdigest(),
                "ts": info.date_time,
                "size": info.file_size,
            })
    return out

def classify(a_path, b_path):
    A, B = entries(a_path), entries(b_path)
    names_a = [e["name"] for e in A]
    names_b = [e["name"] for e in B]
    map_a = {e["name"]: e for e in A}
    map_b = {e["name"]: e for e in B}
    membership_diff = set(names_a) ^ set(names_b)
    order_diff = names_a != names_b and not membership_diff
    content_diffs = [n for n in set(names_a) & set(names_b) if map_a[n]["sha"] != map_b[n]["sha"]]
    ts_diffs = [n for n in set(names_a) & set(names_b) if map_a[n]["ts"] != map_b[n]["ts"]]
    if not membership_diff and not order_diff and not content_diffs and not ts_diffs:
        code = "IDENTICAL"
    elif content_diffs and (order_diff or ts_diffs):
        code = "MIXED"
    elif content_diffs:
        code = "CONTENT"
    elif order_diff and ts_diffs:
        code = "ORDERING+TIMESTAMP"
    elif order_diff:
        code = "ORDERING"
    else:
        code = "TIMESTAMP_ONLY"
    return {
        "code": code,
        "n_entries": len(A),
        "membership_diff": sorted(membership_diff)[:10],
        "n_membership_diff": len(membership_diff),
        "order_diff": order_diff,
        "n_content_diffs": len(content_diffs),
        "content_diffs": content_diffs[:10],
        "n_ts_diffs": len(ts_diffs),
    }

def main():
    dirs = sys.argv[1:]
    if not dirs:
        ex = os.path.join(BASE, "data", "e1-extracts")
        dirs = sorted(d for d in os.listdir(ex) if d.startswith("p") and d.endswith("-e1") and d != "p6-bootui-e1")
    summary = []
    for tag in dirs:
        root = os.path.join(BASE, "data", "e1-extracts", tag)
        projs = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
        for proj in projs:
            b1 = os.path.join(root, proj, "E1", "build-1", "artifacts")
            b2 = os.path.join(root, proj, "E1", "build-2", "artifacts")
            if not (os.path.isdir(b1) and os.path.isdir(b2)):
                print(f"SKIP {tag}/{proj}: no artifacts dirs")
                continue
            jars1 = sorted(f for f in os.listdir(b1) if f.endswith(".jar"))
            results = {}
            for jar in jars1:
                p2 = os.path.join(b2, jar)
                if not os.path.exists(p2):
                    results[jar] = {"code": "MISSING_IN_BUILD2"}
                    continue
                results[jar] = classify(os.path.join(b1, jar), p2)
            codes = Counter(r["code"] for r in results.values())
            with open(os.path.join(OUT, f"entries-{tag}.json"), "w") as f:
                json.dump({"project": proj, "extract": tag, "pairs": results}, f, indent=1)
            summary.append((tag, proj, dict(codes), len(results)))
            print(f"{tag} {proj}: {dict(codes)} ({len(results)} pairs)")
    with open(os.path.join(OUT, "entries-summary.md"), "w") as f:
        f.write("# Entry-level classification (within-E1 pairs)\n\n")
        for tag, proj, codes, n in summary:
            f.write(f"- **{tag}** `{proj}`: {n} pairs — {codes}\n")

if __name__ == "__main__":
    main()
