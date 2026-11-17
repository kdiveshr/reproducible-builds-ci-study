# Effort ledger (RQ3) — contemporaneous record

Times are wall-clock, single author, estimated to the nearest 5 minutes.
Diagnosis = time to identify the cause from build outputs/diffs. Fix = time to
write and commit the change. Verification = time to run the confirming builds
and compare (excludes CI queue time). Fixes live on branches in forks under
kdiveshr; no upstream pull requests (out of scope, decided Nov 16).

## Project 1: introproventures/graphql-jpa-query @ 649307fc (14 artifacts, 0/14 baseline)

Cause: TIMESTAMP (zip entry timestamps = build time; 0 content differences;
verified by entry-level comparison and diffoscope).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~25 min (entry-level zipfile check + diffoscope reports +
  cross-check, during pilot classification, Nov 17).
- Fix: ~15 min. Fork: kdiveshr/graphql-jpa-query, branch
  `repro-step2-outputtimestamp`, commit ec198afeb540d5f5b3c65c389d330ec94cc1e475
  (parent = pinned 649307fc). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1774388038</project.build.outputTimestamp>`,
  the pinned commit's timestamp 2026-03-24T21:33:58Z). Property inherited by
  all modules; no plugin configuration changed.
- Verification: E3 two-build run launched Nov 17 ~02:20 ET — PENDING.
- Outcome: TBD.
- Iterations so far: 1.
