# Pilot diff classification (RQ2) — Nov 17, 2026

Method: diffoscope 259 (text + HTML reports in this directory) on the within-E1
build-1 vs build-2 pair for every artifact of the 4 non-reproducible pilot
projects (8 reports: shopping 1, ScheduleDashboard 2, josdk 5). Cross-checked
with an independent Python zipfile entry comparison (names, order, timestamps,
per-entry content hashes). Project 1 (graphql-jpa-query) was entry-verified
the same way; it has no diffoscope report because its baseline JARs were not
retained. The reproducible project (agentcore, 11/11) has no non-matching
pairs.

## Results

| Project | Artifacts | Content diffs | Cause(s) |
|---|---|---|---|
| graphql-jpa-query | 14 | 0 | Zip entry timestamps only (build time); fat JARs differ only via embedded library JARs carrying the same cause |
| ScheduleDashboard | 2 | 0 | Zip entry timestamps AND entry ordering (same membership, different order, e.g. static assets) |
| shopping-app-backend | 1 | 0 | Zip entry timestamps only, narrowly: 7 of 543 entries (manifest + directory entries) |
| josdk-spring-boot-starter | 5 | 0 | Zip entry timestamps only (nearly all entries) |

In all 8 diffoscope reports the only differing sections are zip metadata
(zipinfo; zipnote in the two ScheduleDashboard reports, reflecting the entry
order). No nested content comparator fired anywhere: no .class, manifest,
pom.properties, or embedded-JAR content difference in any pair.

## Codebook mapping (seeded from Sharma et al. 6 causes / Xiong et al. 14 patterns)

- `TIMESTAMP` — zip entry timestamps stamped with build time. Present in all 4
  projects. SOURCE_DATE_EPOCH was set in every build, so the persistence of
  this cause is itself a finding (playbook step 1 does not normalize it for
  these projects).
- `ORDERING` — archive entry order varies between builds. Present in
  ScheduleDashboard only. Maps to playbook step 5.

## Reliability note

Single-author classification. A random 20% sample of phase-1 diffs was
re-classified independently on within-E3 pairs after a gap: 36/36 raw-code
agreement. The zipfile cross-check above served as the pilot's second pass:
it agreed with diffoscope on every pair.
