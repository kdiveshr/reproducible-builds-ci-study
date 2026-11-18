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

## Project 6: luanferreiradev/algafood-api-algaworks @ 6d6a357c (1 artifact, 0/1 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pair; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result; no separate diagnosis needed).
- Fix: ~10 min. Fork: kdiveshr/algafood-api-algaworks, branch
  `repro-step2-outputtimestamp`, commit 911ac5f37ddf438e87aa7f2f963407be2f04d150
  (parent = pinned 6d6a357c). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794885669</project.build.outputTimestamp>`,
  the pinned commit's timestamp). Tab-indented pom.
- Verification: E3 two-build run Nov 17 ~18:23 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1 run 44198983480 + E2 pipeline
  3081592309) Nov 17 ~18:43 ET — 1/1 between EVERY pair (within-E1,
  within-E2, cross-env, incl. architectures). Verification time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 7: Pawan-Ghode/Fintech-Payment-Processing-API @ 15e31719 (1 artifact, 0/1 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pair; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/Fintech-Payment-Processing-API, branch
  `repro-step2-outputtimestamp`, commit eee7403bd9a06677021bb4de74adfd04bd9b310f
  (parent = pinned 15e31719). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794888894</project.build.outputTimestamp>`,
  the pinned commit's timestamp). Tab-indented pom.
- Verification: E3 two-build run Nov 17 ~18:23 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1 run 44198996083 + E2 pipeline
  3081597137) Nov 17 ~18:43 ET — 1/1 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 8: bulangya-bu/linguamate-agent @ 48f8e1c6 (1 artifact, 0/1 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pair; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/linguamate-agent, branch
  `repro-step2-outputtimestamp`, commit 4a695f8a2838ff182b694fb1bbc5786d88e54c65
  (parent = pinned 48f8e1c6). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794893355</project.build.outputTimestamp>`,
  the pinned commit's timestamp). Space-indented pom.
- Verification: E3 two-build run Nov 17 ~18:23 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1 run 44199007456 + E2 pipeline
  3081598175) Nov 17 ~18:43 ET — 1/1 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.


## Project 9: Coelho-Techne/detectionSystem @ 5b25beca (1 artifact, 0/1 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pair; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/detectionSystem, branch
  `repro-step2-outputtimestamp`, commit d8b30c2b772703c68f4a8d8a51f4278eb6679ce2
  (parent = pinned 5b25beca). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794886851</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~19:00 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1 run 44204258144 + E2 pipeline
  3081677065) Nov 17 ~19:19 ET — 1/1 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 10: Thissvane/PetsUniverseSpringBoot @ 0daf2f16 (1 artifact, 0/1 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pair; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/PetsUniverseSpringBoot, branch
  `repro-step2-outputtimestamp`, commit be499f20b93b08c2be831101a0990d77bf4ca781
  (parent = pinned 0daf2f16). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794885379</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~19:00 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1 run 44204269203 + E2 pipeline
  3081677854) Nov 17 ~19:19 ET — 1/1 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 13: jdbc-observations/datasource-micrometer @ b7c62115 (4 artifacts, 0/4 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pairs; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/datasource-micrometer, branch
  `repro-step2-outputtimestamp`, commit a3db1bba0ccd84828e592ada05610ef7bb7711fb
  (parent = pinned b7c62115). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794886647</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~19:00 ET — 4/4 MATCH within E3
  (baseline was 0/4). Cross-environment verification (E1 run 44204280878 + E2 pipeline
  3081678740) Nov 17 ~19:19 ET — 4/4 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 12: HQfire/book-manager @ 7073ab1d (1 artifact, 0/1 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pair; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/book-manager, branch
  `repro-step2-outputtimestamp`, commit 7ff53ca4c06b09972c3dfbd0d49b49412294e259
  (parent = pinned 7073ab1d). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794891400</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~19:34 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1 run 44208883146 + E2 pipeline
  3081766246) Nov 17 ~19:51 ET — 1/1 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 14: lunasaw/zlm-spring-boot-starter @ 59a262c0 (1 artifact, 0/1 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pair; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/zlm-spring-boot-starter, branch
  `repro-step2-outputtimestamp`, commit eb9af3e384ca18e7df93311e7239532960c6f0c6
  (parent = pinned 59a262c0). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1781099355</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~19:34 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1 run 44208894171 + E2 pipeline
  3081767506) Nov 17 ~19:51 ET — 1/1 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 15: bansh2eBreak/SpringVulnBoot-backend @ 31ea29b5 (1 artifact, 0/1 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pair; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/SpringVulnBoot-backend, branch
  `repro-step2-outputtimestamp`, commit 18d600d88623c94e5ba0a3699c48baa502d5cae4
  (parent = pinned 31ea29b5). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794675824</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~19:34 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1 run 44208904909 + E2 pipeline
  3081769435) Nov 17 ~19:51 ET — 1/1 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 16: diva154/SpringMVC-to-SpringBoot-CRUDoperation-Migration @ 4fa9ea7c (1 artifact, 0/1 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pair; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/SpringMVC-to-SpringBoot-CRUDoperation-Migration,
  branch `repro-step2-outputtimestamp`, commit 1262dc3145d237b1cf5fcfb00c9ff1cfbfb62eb4
  (parent = pinned 4fa9ea7c). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794891004</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~20:07 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1 run 44213296731 + E2 pipeline
  3081846017) Nov 17 ~20:24 ET — 1/1 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 19: penpencil721-lab/spring-boot-practice @ 518e0564 (1 artifact, 0/1 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pair; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/spring-boot-practice, branch
  `repro-step2-outputtimestamp`, commit c60d059ea3b3dd34d61563884664c2ecd8c6a611
  (parent = pinned 518e0564). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794891815</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~20:07 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1 run 44213307711 + E2 pipeline
  3081847871) Nov 17 ~20:24 ET — 1/1 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 20: JoseOtavioJunqueira/desafio-itau-backend @ 1d409ea9 (1 artifact, 0/1 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pair; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/desafio-itau-backend, branch
  `repro-step2-outputtimestamp`, commit dc2f9a29a33ece1404db31810922575c03350b62
  (parent = pinned 1d409ea9). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794884755</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~20:07 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1 run 44213318201 + E2 pipeline
  3081851154) Nov 17 ~20:24 ET — 1/1 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 25: thangtranitwork/social-network @ 739b9d7b (1 artifact, 0/1 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pair; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/social-network, branch
  `repro-step2-outputtimestamp`, commit 4ae0e7523a4487037380d7392e757028f3ffb069
  (parent = pinned 739b9d7b). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794887645</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~20:40 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1 run 44217540809 + E2 pipeline
  3081920140) Nov 17 ~20:52 ET — 1/1 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 26: Temirlan222/trello-main @ 5f70a856 (1 artifact, 0/1 baseline)

Cause: TIMESTAMP (entry-level sweep, within-E1 pair; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/trello-main, branch
  `repro-step2-outputtimestamp`, commit 3c87f1505a2aac9935d1a5aa3da6ea3a19c93195
  (parent = pinned 5f70a856). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794893290</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~20:40 ET — 1/1 MATCH within E3
  (baseline was 0/1). Cross-environment verification (E1 run 44217552216 + E2 pipeline
  3081920612) Nov 17 ~20:52 ET — 1/1 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 22: codecentric/chaos-monkey-spring-boot @ ecd224b7 (9 artifacts, 0/9 baseline)

Cause: TIMESTAMP incl. nested propagation (entry-level sweep: 4 TIMESTAMP_ONLY
+ 5 MIXED resolved to nested embedded-JAR timestamps, 0 genuine content diffs).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result + nested resolution).
- Fix: ~10 min. Fork: kdiveshr/chaos-monkey-spring-boot, branch
  `repro-step2-outputtimestamp`, commit 18d71cee89430c83dc541f016cda8465e1928017
  (parent = pinned ecd224b7). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794760224</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~20:40 ET — 9/9 MATCH within E3
  (baseline was 0/9). Cross-environment verification (E1 run 44217562145 + E2 pipeline
  3081921303) Nov 17 ~20:52 ET — 9/9 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 8: dapr/java-sdk @ f8c4c282 (17 artifacts, 0/17 baseline)

Cause: TIMESTAMP incl. nested propagation (entry-level sweep: 16 TIMESTAMP_ONLY
+ 1 MIXED resolved to nested embedded-JAR timestamps, 0 genuine content diffs).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result + nested resolution).
- Fix: ~10 min. Fork: kdiveshr/java-sdk, branch
  `repro-step2-outputtimestamp`, commit b1dad6750a5e8d40348ec9879168a354066d338d
  (parent = pinned f8c4c282). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794852054</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~21:13 ET — 17/17 MATCH within E3
  (baseline was 0/17). Cross-environment verification (E1 run 44221599083 + E2 pipeline
  3081998858) Nov 17 ~21:36 ET — 17/17 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 9: amqphub/amqp-10-jms-spring-boot @ 7d86d0c6 (8 artifacts, uniform 2/8 baseline)

Cause: TIMESTAMP (entry-level sweep: 2 IDENTICAL plain library JARs + 6
TIMESTAMP_ONLY Boot-repackaged example fat JARs; 0 content differences).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~5 min (entry-level sweep result).
- Fix: ~10 min. Fork: kdiveshr/amqp-10-jms-spring-boot, branch
  `repro-step2-outputtimestamp`, commit 88afa81bb0b8a3b0bf242e58cee5ae8fa9df58cb
  (parent = pinned 7d86d0c6). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1793893525</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~21:13 ET — 8/8 MATCH within E3
  (baseline was uniform 2/8). Cross-environment verification (E1 run 44221607664 + E2 pipeline
  3081999591) Nov 17 ~21:36 ET — 8/8 between EVERY pair (baseline was
  uniform 2/8). Verification time ~15 min.
- Outcome: FIXED — playbook step 2 only, 1 iteration, 2-line diff.
- Iterations so far: 1.

## Project 23: spring-petclinic/spring-petclinic-data-jdbc @ d601d3a8 (1 artifact, 0/1 baseline)

Cause: TIMESTAMP + EMBEDDED_TIME (entry-level sweep MIXED: build.time in
META-INF/build-info.properties and git.build.time/git.build.host in
BOOT-INF/classes/git.properties differ as file content, plus 95 zip-ts diffs).
Playbook order: step 2 first; step 6 for the embedded build-time fields if
they persist after step 2.

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~10 min (entry-level sweep + diffoscope confirmation).
- Fix: ~10 min. Fork: kdiveshr/spring-petclinic-data-jdbc, branch
  `repro-step2-outputtimestamp`, commit 00b8d6602d2d252dd2389248b2849b80578c9a81
  (parent = pinned d601d3a8). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1767810134</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~21:13 ET — 1/1 MATCH within E3
  (baseline was 0/1): step 2 alone normalized the embedded build-time
  fields within E3; whether git.build.host (container hostname) breaks
  cross-environment matching is the open question for the E1/E2 check.
  Cross-environment verification (E1 run 44221614886 + E2 pipeline
  3082000498) Nov 17 ~21:36 ET — PARTIAL: 1/1 within every environment,
  0/1 across environments. Diagnosis: the only differing entry is
  BOOT-INF/classes/git.properties, and the only differing field is
  git.build.host (the Docker container hostname, e.g. f986c71db991 vs
  4033d0a12e11). Step 2 normalized everything else, including build.time
  (pinned to the commit time) and all zip timestamps. Verification time
  ~15 min.
- Outcome of attempt 1: PARTIAL — within-environment only; ambient build
  context (host) persists across environments.

### Attempt 2 — playbook step 6 (neutralize build-time metadata)

- Diagnosis: ~10 min (entry diff of the E1 vs E3 fix-build JARs; single
  field identified).
- Fix: ~10 min. Same fork/branch, commit 510d610f6957d0e935b078aea509426344ca7e19
  (parent = step-2 commit 00b8d660). Diff: +5 lines in the
  git-commit-id-maven-plugin <configuration> — <excludeProperties> with
  ^git\.build\.host$ — dropping the container hostname from
  git.properties.
- Verification: E3 two-build run Nov 17 ~21:47 ET — 1/1 MATCH within E3.
  Cross-environment verification (E1 run 44225727965 + E2 pipeline
  3082072930) Nov 17 ~22:04 ET — PARTIAL: E1 and E3 now match each other
  1/1, but E2 differs from both. Diagnosis via the plugin's verbose
  'Collected' lines in the E1 vs E2 build logs (the E2 JAR is not
  uploaded under the narrowed shim): in E2 the plugin reads CI context
  from the GitLab runner environment — git.branch=main (from the CI ref
  name, where E1/E3 record the detached commit SHA), git.build.number=69
  and git.build.number.unique=3082072930 (pipeline IID/ID) — and writes
  them into git.properties. Second instance of the CI_CONTEXT leak, this
  time E2-side via plugin environment detection. Verification time ~20 min.
- Outcome of attempt 2: PARTIAL — host leak fixed; CI-env leak in E2
  remains.

### Attempt 3 — playbook step 6, iteration 2 (extend the exclusion list)

- Diagnosis: ~15 min (build-log comparison; no E2 JAR available).
- Fix: ~10 min. Same fork/branch, commit 8209b81b8666054de26108a9cdefa879208bca75
  (parent = step-6 commit 510d610f). Diff: +2 lines — the
  <excludeProperties> list now also excludes ^git\.branch$ and
  ^git\.build\.number(\.unique)?$.
- Verification: E3 two-build run Nov 17 ~22:14 ET — 1/1 MATCH within E3.
  Cross-environment verification (E1 run 44228923246 + E2 pipeline
  3082136625) Nov 17 ~22:31 ET — 1/1 between EVERY pair. Verification
  time ~15 min.
- Outcome: FIXED — playbook steps 2 + 6 (3 attempts, 9 lines total:
  2 for step 2, 7 for the step-6 exclusion list across 2 iterations).
- Iterations so far: 3.

## Project 24: apolloconfig/apollo @ 504e5cd7 (12 artifacts, 0/12 baseline)

Cause: TIMESTAMP + EMBEDDED_TIME (entry-level sweep: 12 MIXED — apollo-git.properties
in all 12 modules (comment timestamp + git.build.time), apollo-portal's 33 static
HTML content diffs = build-time cache-buster query strings ?v=yyyyMMddHHmmss, plus
nested apollo JAR timestamp propagation). Playbook order: step 2 first; step 6
for the embedded build-time fields if they persist.

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~10 min (entry-level sweep + diffoscope confirmation).
- Fix: ~10 min. Fork: kdiveshr/apollo, branch
  `repro-step2-outputtimestamp`, commit c6244b9d3fbc550eefdcf77a1d35582b3a4ab0bb
  (parent = pinned 504e5cd7). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794751106</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 17 ~22:51 ET — 0/12 within E3: step 2
  did NOT fix apollo even within one environment. Diagnosis: (1) the
  git-commit-id plugin is version 2.2.6, which ignores outputTimestamp —
  apollo-git.properties still carries a wall-clock file-header comment,
  git.build.host (container hostname) and wall-clock git.build.time;
  (2) the portal's maven-replacer-plugin stamps ?v=${maven.build.timestamp}
  (wall-clock yyyyMMddHHmmss) into 33 HTML files at prepare-package.
  Verification time ~15 min.
- Outcome of attempt 1: NOT FIXED — embedded wall-clock content persists.

### Attempt 2 — playbook step 6 (neutralize build-time metadata)

- Diagnosis: ~20 min (entry diffs of the E3 fix-build JARs + pom inspection;
  no module pom redeclares the git plugin, so the root-pom change covers
  all 12 modules).
- Fix: ~15 min. Same fork/branch, commit 93b97d135657537c1380452720e98a040c784cb1
  (parent = step-2 commit c6244b9d). Two sub-changes, both step 6:
  (a) root pom.xml — upgrade git-commit-id plugin 2.2.6
  (pl.project13.maven) to 9.0.2 (io.github.git-commit-id), which honors
  outputTimestamp, and add <excludeProperties> for ^git\.build\.host$,
  ^git\.branch$ and ^git\.build\.number(\.unique)?$ (the CI-env leak
  found in petclinic); (b) apollo-portal/pom.xml — replacer values
  ${maven.build.timestamp} replaced by ${project.build.outputTimestamp}
  (2 lines), so the cache-buster is pinned to the commit time.
- Verification: E3 two-build run Nov 17 ~23:13 ET — 12/12 MATCH within E3.
  Cross-environment verification (E1 run 44235736896 + E2 pipeline
  3082264535) Nov 17 ~23:37 ET — 12/12 between EVERY pair. Verification
  time ~20 min.
- Outcome: FIXED — playbook steps 2 + 6 (2 attempts; step-2 property +
  plugin upgrade/exclusions + cache-buster pin).
- Iterations so far: 2.

## Project 17: jdubois/boot-ui @ 1f5b25ed (2,895 artifacts; baseline within-env 2,818/2,895, E1-vs-E2/E3 2,781/2,895)

Cause: TIMESTAMP (77 artifacts differ within every environment) + CI_CONTEXT
(19 artifacts — the bootui-quarkus module JAR + 18 copies — stable within every
environment but differing E1-vs-E2/E3 on one field only, scm-url, because the
harness passes GITHUB_REPOSITORY into the E1 container and the Quarkus plugin
resolves scm-url from it). Per the recorded design decision, the harness is
left unchanged for the fix phase; the 19 CI_CONTEXT artifacts are a disclosed
harness confound, NOT a project defect, and fix verification is judged with
the confound disclosed: success = all non-confound artifacts matching between
every pair (within-env 2,895/2,895 on common paths; E1 cross-env differing
only on the 19 confound artifacts).

### Attempt 1 — playbook step 2 (outputTimestamp property)

- Diagnosis: ~10 min (entry-level sweep + targeted classification).
- Fix: ~10 min. Fork: kdiveshr/boot-ui, branch
  `repro-step2-outputtimestamp`, commit cff3cc176b5f9fb0312420e58057329d64cd07ff
  (parent = pinned 1f5b25ed). Diff: +2 lines in root pom.xml (comment +
  `<project.build.outputTimestamp>1794893937</project.build.outputTimestamp>`,
  the pinned commit's timestamp).
- Verification: E3 two-build run Nov 18 ~00:17 ET — both builds FAILED
  (exit 1, 17 artifacts each before the failing module). Diagnosis: the
  Quarkus Maven plugin (3.40.1.1) maps project.build.outputTimestamp to
  quarkus.package.output-timestamp and rejects epoch seconds —
  SRCFG00039 config conversion failure in bootui-quarkus-integration-tests.
  The epoch form is valid for Maven but not for Quarkus, which requires
  ISO-8601. Verification time ~10 min.
- Outcome of attempt 1: NOT FIXED — toolchain rejects the epoch form.

### Attempt 2 — playbook step 2, iteration 2 (ISO-8601 outputTimestamp)

- Diagnosis: ~10 min (build-log error + Quarkus config requirement).
- Fix: ~10 min. Same fork/branch, head commit
  ba52c5fb695724e804411f3010d97e014a7c9c26 (parent b832b03d, which first
  switched the value to ISO form with an incorrect time-of-day; the head
  commit corrects it to the pinned commit time: 1794893937 =
  2026-11-17T05:38:57Z). Diff vs attempt 1: the outputTimestamp value
  only, epoch seconds -> ISO-8601 string of the same instant. Maven's
  reproducible-builds spec allows both forms; the ISO form is the one
  Quarkus accepts.
- Verification: E3 two-build run Nov 18 ~00:51 ET — both builds SUCCEEDED
  (2,895 artifacts each); within-env 2,892/2,895. The 3 remaining
  artifacts (bootui-agent JAR, bootui-cli -all JAR, cli-docs.jar) differ
  ONLY in zip-entry timestamps, 0 content diffs. Diagnosis: all three are
  written (or, for the -all JAR, fed via extraJars) by maven-antrun-plugin
  Ant <jar> tasks, which do not honor project.build.outputTimestamp — Ant
  archive tasks do not read SOURCE_DATE_EPOCH either (only <tstamp> does);
  they need the modificationtime attribute (since Ant 1.10.2). The
  -all JAR inherits cli-docs.jar's unpinned entry times through shade's
  extraJars path. Verification time ~15 min.
- Outcome of attempt 2: PARTIAL — 2,892/2,895 within E3.

### Attempt 3 — playbook step 2, iteration 3 (Ant jar-task modificationtime)

- Diagnosis: ~20 min (entry-level diffs + plugin-config inspection +
  Ant manual verification of the modificationtime attribute).
- Fix: ~10 min. Same fork/branch, commit
  cb2312fb2ec7bbfb2acce46ecfb9c1c050a6b6ce (parent ba52c5fb). Diff:
  +1 attribute on each of the two Ant <jar> tasks (bootui-agent/pom.xml
  and bootui-cli/pom.xml): modificationtime="${project.build.outputTimestamp}",
  so the Ant-written JARs pin every entry to the same instant as the
  Maven-written ones. The -all JAR is expected to follow via the pinned
  cli-docs.jar.
- Verification: E3 two-build run Nov 18 ~01:33 ET — 2,895/2,895 MATCH
  within E3. Cross-environment verification (E1 run 44252162040 + E2
  pipeline 3082577595) Nov 18 ~02:24 ET: within every environment
  2,895/2,895; E2-vs-E3 2,895/2,895; E1-vs-E2/E3 2,840/2,895. On the
  2,877 common paths, 37 differ E1-vs-E3: the 19 known scm-url confound
  artifacts (expected, disclosed) PLUS 18 quarkus generated-bytecode.jar
  files that match within every environment but differ E1-vs-ARM —
  masked in the baseline by the within-environment timestamp diffs.
  Diagnosis of the 18 generated-bytecode jars is in progress (E1 members
  being re-downloaded selectively from the 1.79GB artifact).
  Verification time ~20 min so far.
- Outcome: FIXED WITH DISCLOSED RESIDUALS. Attempt 3 (step 2, 3
  iterations) achieved full within-environment reproducibility
  (2,895/2,895 in E1, E2 and E3) and full E2-vs-E3 match. E1-vs-E2/E3
  stands at 2,840/2,895; the remaining gap is (a) 18 arch-specific
  artifact paths (brotli native JARs, expected), (b) the 19 disclosed
  scm-url confound artifacts (harness artifact, not a project defect),
  and (c) 18 Quarkus generated-bytecode.jar files carrying a GENUINE
  cross-environment ORDERING effect: entry-level comparison of all 18
  E1-vs-E3 pairs shows 0 timestamp diffs and 1-2 differing generated
  recorder classes each (StaticResourcesProcessor$runtimeInit in all
  18; TracerProcessor$setupSampler in 3), with identical constant
  multisets in a different constant-pool order (verified on the base
  module: 218 string runs, same multiset, 2 positions swapped —
  favicon.ico vs a RuntimeInsights asset). The ordering is stable
  within each environment and differs E1-vs-ARM, consistent with
  filesystem-enumeration/hash-iteration order feeding Quarkus's
  bytecode generation. No playbook step addresses generated-code
  constant ordering (step 5 covers archive ordering only), so this
  residual is recorded as a finding, not a fixable defect.
- Iterations: 3 (all within step 2). Diagnosis total ~45 min, fix
  total ~30 min, verification ~45 min across attempts.
