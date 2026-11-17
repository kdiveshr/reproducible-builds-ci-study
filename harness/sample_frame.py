#!/usr/bin/env python3
"""Build the study sample frame from GitHub code-search pages.

Reads raw/*.json (code search for `spring-boot-maven-plugin filename:pom.xml`,
three order variants, 3 pages each), dedupes by repository, applies the
documented frame filters, shuffles with a recorded seed, and writes the
screening-order list. No network access: parsing only.

Frame filters applied HERE (from what code-search results carry):
  - not a fork (fork flag is present in results)
  - public (private flag is present in results)

Activity (pushed within 12 months) and license CANNOT be filtered here:
code-search repository objects are minimal and carry no pushed_at,
stargazers_count, license, size, or default_branch. Those checks happen at
screening time from the clone (latest commit date on the default branch,
LICENSE file), with no extra API calls. Per-repo metadata is recorded
during screening, not here.

Known limitation (recorded, not hidden): GitHub code search returns at most
1,000 results per query out of ~1.64M matches, ordered by GitHub's ranking.
This pool is an enumerated convenience sample with a randomized screening
order, NOT a random draw from all Spring Boot projects. Study claims stay
descriptive ("in our sample of 25...").
"""
import glob
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RAW = os.path.join(DATA, "raw")
SEED = 20261116
PUSHED_CUTOFF = "2025-11-16T00:00:00Z"

repos = {}
pages_ok, pages_bad = 0, 0
for path in sorted(glob.glob(os.path.join(RAW, "*.json"))):
    try:
        with open(path) as f:
            payload = json.load(f)
    except Exception:
        pages_bad += 1
        continue
    items = payload.get("items")
    if not isinstance(items, list):
        pages_bad += 1
        continue
    pages_ok += 1
    for item in items:
        repo = item.get("repository") or {}
        full_name = repo.get("full_name")
        if not full_name:
            continue
        entry = repos.setdefault(full_name, {
            "full_name": full_name,
            "html_url": repo.get("html_url"),
            "is_fork": repo.get("fork"),
            "is_private": repo.get("private"),
            "pom_files_seen": 0,
        })
        entry["pom_files_seen"] += 1

total_unique = len(repos)
after_fork = {k: v for k, v in repos.items() if v["is_fork"] is False}
after_public = {k: v for k, v in after_fork.items() if v["is_private"] is False}

pool = list(after_public.values())
random.seed(SEED)
random.shuffle(pool)
for rank, entry in enumerate(pool, start=1):
    entry["screen_rank"] = rank

with open(os.path.join(DATA, "frame-candidates.json"), "w") as f:
    json.dump(pool, f, indent=2)

summary = (
    f"pages read ok: {pages_ok}, pages bad/empty: {pages_bad}\n"
    f"unique repos seen: {total_unique}\n"
    f"after fork filter: {len(after_fork)}\n"
    f"after public filter (final pool): {len(pool)}\n"
    f"activity + license checks: deferred to clone-based screening\n"
    f"shuffle seed: {SEED}\n"
    f"frame query: spring-boot-maven-plugin filename:pom.xml "
    f"(total_count reported by GitHub: 1644544; API cap 1000/query)\n"
    f"enumeration stopped early: GitHub API rate limit (HTTP 403) after 7/9 pages\n"
)
with open(os.path.join(DATA, "frame-summary.txt"), "w") as f:
    f.write(summary)
print(summary)
print("first 10 in screening order:")
for entry in pool[:10]:
    print(f"  {entry['screen_rank']:3d} {entry['full_name']}")
