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
- Verification: E3 two-build run Nov 17 ~02:20 ET — 14/14 MATCH within E3
  (baseline was 0/14). Cross-environment verification (E1+E2 of the fix
  commit) Nov 17 ~02:26–02:33 ET — 14/14 between EVERY pair (within-E1,
  within-E2, cross-env, incl. architectures). Verification time ~20 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.

## Project 3: Shitanshu686/shopping-app-backend @ d1b392e7 (1 artifact, 0/1 baseline)

Cause: TIMESTAMP, narrowly (7 of 543 entries, manifest + directory entries;
0 content differences; verified by entry-level comparison and diffoscope).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~10 min (entry-level zipfile check + diffoscope report, during
  pilot classification, Nov 17).
- Fix: ~10 min. Fork: kdiveshr/shopping-app-backend, branch
  `repro-step2-outputtimestamp`, commit 20386c56099a4cba5a5d47f3808fe2d267a2466f
  (parent = pinned d1b392e7). Diff: +2 lines in pom.xml (comment +
  `<project.build.outputTimestamp>1794884071</project.build.outputTimestamp>`,
  the pinned commit's timestamp 2026-11-17T02:54:31Z).
- Verification: E3 two-build run Nov 17 ~02:34 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1+E2 of the fix
  commit) Nov 17 ~02:39–02:47 ET — 1/1 between EVERY pair (within-E1,
  within-E2, cross-env, incl. architectures). Verification time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 5: operator-framework/josdk-spring-boot-starter @ 1090e662 (5 artifacts, 0/5 baseline)

Cause: TIMESTAMP (nearly all zip entries, 0 content differences in all 5
JARs; verified by entry-level comparison and diffoscope).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~10 min (entry-level zipfile check + diffoscope reports, during
  pilot classification, Nov 17).
- Fix: ~10 min. Fork: kdiveshr/josdk-spring-boot-starter, branch
  `repro-step2-outputtimestamp`, commit 2d5bc6f75acab612b2c599ddf213899079306bcd
  (parent = pinned 1090e662). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794847418</project.build.outputTimestamp>`,
  the pinned commit's timestamp 2026-11-16T16:43:38Z).
- Verification: E3 two-build run Nov 17 ~02:39 ET — 5/5 MATCH within E3
  (baseline was 0/5). Cross-environment verification (E1+E2 of the fix
  commit) Nov 17 ~02:49–02:55 ET — 5/5 between EVERY pair (within-E1,
  within-E2, cross-env, incl. architectures). Verification time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.
- Iterations so far: 1.
