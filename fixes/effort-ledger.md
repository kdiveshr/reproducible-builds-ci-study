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

## Project 2: VarshaUpadhyay/ScheduleDashboard @ 831e0542 (2 artifacts, 0/2 baseline)

Causes: TIMESTAMP + ORDERING (zip entry timestamps AND entry order varies;
0 content differences; verified by entry-level comparison and diffoscope).
Toolchain note: Spring Boot 2.1.4 parent (2019-era) manages an old
maven-jar-plugin/maven-archiver, which may predate outputTimestamp support —
step 2 is attempted first per the playbook, and the result determines whether
explicit archiver configuration (still step 2) is needed.

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~15 min (entry-level zipfile check incl. order verification +
  diffoscope reports, during pilot classification, Nov 17).
- Fix: ~10 min. Fork: kdiveshr/ScheduleDashboard, branch
  `repro-step2-outputtimestamp`, commit 3301d5ba4861cecf2fcfe805187c8e94b7f272b3
  (parent = pinned 831e0542). Diff: +2 lines in pom.xml (comment +
  `<project.build.outputTimestamp>1779689639</project.build.outputTimestamp>`,
  the pinned commit's timestamp 2026-05-25T06:13:59Z).
- Verification: E3 two-build run Nov 17 ~02:57 ET — 0/2, sizes identical.
  Entry-level check of the fixed JARs: timestamps STILL build time (property
  ignored by the old archiver), entry order STILL differs, 0 content diffs.
  Verification time ~15 min.
- Outcome: NOT FIXED — the outputTimestamp property alone has no effect on
  this toolchain (Spring Boot 2.1.4 manages maven-jar-plugin 3.1.2 /
  maven-archiver pre-3.6.0, which predates outputTimestamp support).

### Attempt 2 — playbook step 2 continued (maven-archiver configuration)

- Diagnosis: ~10 min (entry-level check of attempt-1 JARs showed the property
  was ignored; pom read confirmed the 2019-era toolchain).
- Fix: ~10 min. Second commit on the same branch, c040bd444792fd2c39fdb22a863e986c3e275fa7
  (parent = attempt-1 commit 3301d5ba). Diff: +6 lines in pom.xml — pins
  `maven-jar-plugin` to 3.3.0 (bundles maven-archiver 3.6.x, which honors
  outputTimestamp). The property from attempt 1 is kept.
- Verification: E3 two-build run launched Nov 17 ~06:02 ET — 1/2 MATCH
  within E3: the plain JAR is fixed (timestamps normalized AND entry order
  now stable), but the -exec fat JAR still differs. Entry-level check: 0
  content diffs, order now equal; the 13 remaining timestamp-only diffs are
  all entries the repackage goal writes itself (Boot loader classes +
  manifest), stamped with build time — Boot 2.1.4's repackage predates
  outputTimestamp support (added in 2.3.0, per official plugin docs).
  Verification time ~20 min.
- Outcome: PARTIALLY FIXED — plain JAR fixed; fat JAR blocked on the
  repackage goal.

### Attempt 3 — playbook step 2 continued (repackage outputTimestamp)

- Diagnosis: ~15 min (entry-level check of attempt-2 JARs isolated the
  residual to repackage-written loader entries; official docs confirmed
  repackage outputTimestamp support since plugin 2.3.0).
- Fix: ~10 min. Third commit on the same branch, e682bf1e990716448d7ce90ceccc79ea1f5f0b39
  (parent = attempt-2 commit c040bd44). Diff: +1 line in pom.xml — pins
  `spring-boot-maven-plugin` to 2.3.12.RELEASE (last 2.3.x patch; minimal
  version with repackage outputTimestamp support). Property + jar-plugin pin
  from attempts 1–2 kept.
- Verification: E3 two-build run Nov 17 ~06:15 ET — 2/2 MATCH within E3
  (baseline was 0/2). The ORDERING cause was resolved as a side effect of
  the modern archiver (attempt 2); no separate step-5 change was needed.
  Cross-environment verification (E1+E2 of the fix commit) Nov 17
  ~06:24–06:31 ET — 2/2 between EVERY pair (within-E1, within-E2,
  cross-env, incl. architectures). Verification time ~15 min.
- Outcome: FIXED — playbook step 2 only, 3 iterations (property + jar-plugin
  pin + boot-plugin pin), 9-line total diff.
- Iterations so far: 3.

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
