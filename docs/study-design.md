# Empirical study design: cross-environment reproducibility of Spring Boot application builds

**Status:** COMPLETE — Nov 18, 2026. Measurement, classification, fix phase, and analysis finished; replication package assembled.
**Purpose:** A practitioner-scale empirical study designed to meet the bar for a peer-reviewed practitioner article: a novel contribution, traceable data published with the article, solid methodology, validation and evaluation, and my own text — using only public open-source artifacts.
**Basis:** Literature scan of Nov 16–17, 2026 (31 sources) covering reproducibility-rate measurement, Java cause taxonomies, and fix-effort studies.

## 1. The gap, in one paragraph

Every large reproducibility measurement builds everything on one machine with fixed infrastructure (Benedetti et al., ICSE 2025, explicitly), on a single CI platform and architecture (Solarin et al. 2026 Docker preprint, stated as its own limitation), or confounds environment change with the passage of time (Malka et al. 2026 Docker preprint: 2023 GitHub Actions builds vs later local rebuilds). Benedetti et al. explicitly exclude system-level and platform-specific causes from their scope. No published study performs a controlled same-source, multi-environment, hash-compared rebuild experiment. That is the gap: **does the CI environment itself change the artifact, when everything else is held constant?**

## 2. Research questions

- **RQ1 (comparison):** For the same pinned commit built with an identical builder image and build command, how does the artifact match rate across CI environments compare to the repeat-build match rate within a single environment?
- **RQ2 (causes):** Which differences appear only across environments, and how do they classify against the known Java cause taxonomies (Sharma et al. 2026, 6 causes; Xiong et al. 2022, 14 patterns)?
- **RQ3 (fix effort):** Using a pre-registered fix playbook, what fraction of cross-environment failures can be fixed, and what effort (time, diff size, build iterations) does each fix take?

## 3. Sample

- **Population:** Public GitHub repositories: Java + Maven + Spring Boot application producing an executable fat JAR via `spring-boot-maven-plugin`.
- **Inclusion criteria:** builds with a single documented command; active (a commit in the last 12 months); OSI-approved license; no native-code compilation step; full build under 15 minutes on a standard runner (calibrated in the pilot).
- **Size:** 25 projects. That is a small sample: a 50% result would carry roughly ±20 points of uncertainty, so this study describes what happened in these 25 projects — the controlled comparison, the cause taxonomy, and the effort data — rather than estimating a rate for all Spring Boot projects.
- **Selection:** I enumerated two frames. The first (Nov 16, GitHub code search for `spring-boot-maven-plugin filename:pom.xml`; 7 pages fetched before the API rate limit stopped further fetching; GitHub reported 1,644,544 matching files and caps results at 1,000 per query) yielded 290 unique non-fork public repos, screened in randomized order (seed 20261116). Only 3 passed — mostly the candidates were inactive (up to ~11 years stale) or unlicensed — so I enumerated a supplement frame (Nov 17, recency-filtered repo search `spring-boot language:java pushed:>2025-11-16`; GitHub reported roughly 171,000 matching repos; seed 20261117; spring-boot-maven-plugin presence verified from clones at screening), yielding 779 unique non-fork public repos with no overlap with the first frame; 40 passed (5.1%). Activity and license were verified from each clone, since code-search results carry no pushed_at/license fields. Both frames are documented in the replication package; this is an enumerated convenience sample with randomized screening order, not a random draw from all Spring Boot projects, so claims stay descriptive.
- **Tests:** Builds use `mvn package -DskipTests`. Tests do not ship in the JAR, and flaky tests add noise unrelated to the artifact question.
- **Build system:** Maven only. Mixing Maven and Gradle would add a second treatment variable. Gradle is nearly unstudied (only 19 packages in BUILDGEN) and is the natural follow-up study, not part of this one.
- **Pilot:** I ran 5 projects end-to-end first to validate the harness and calibrate build times; the protocol did not change after the pilot, so all 5 stay in the final sample under the pre-registered rule.
- **Screening correction:** The supplement frame's Java-version screen initially excluded only declared versions 21–25 (regex `^(21|22|23|24|25)`), so a Java 26 declaration slipped through — and any version above the toolchain's JDK 17 (including 18–20) would also have passed. I corrected the screen to exclude any declared Java version above 17, in any declaration form found (including custom properties such as `<version.java>`), applied uniformly to all not-yet-attempted candidates. Two candidates were excluded by the corrected screen without build attempts: rahat9016/familie.munshi.backend @ 5f071063 (`<java.version>26</java.version>`) and Hakky54/mutual-tls-ssl @ df050965 (`<version.java>21</version.java>`, a spare). The project that exposed the flaw (petshop-api, below) remains a build-failure exclusion, since it was attempted before the correction. The screen reads only root poms; a child module requiring a newer JDK would surface as a build failure under the pre-registered rule.
- **Exclusions (pre-registered rule: projects that fail to build for reasons unrelated to reproducibility are excluded and replaced, with the reason logged):** 9 candidates excluded in total, all replaced from spares in seed order.
  1. bynour1/tp-cafe--jalila-ben-youssef @ 52e10e32 — `mvn package` fails identically in all three environments: the spring-boot-maven-plugin 3.4.10 repackage goal cannot parse the pom's `<exclude>` configuration ("Cannot find 'version' in class org.springframework.boot.maven.Exclude"). Broken project configuration.
  2. SolaceProducts/solace-spring-boot @ 3454b5f9 — the root pom imports `com.solace.test.integration:solace-integration-test-support-bom:3.0.0`, which does not exist in Maven Central, so Maven cannot read the project. Fails identically in all three environments. Missing dependency.
  3. devgusta07/petshop-api @ b20bb0bb — requires JDK 26 (`<java.version>26</java.version>`); "release version 26 not supported" on the study's Temurin 17 toolchain. Fails identically in all three environments. Toolchain scope.
  4. codecentric/spring-boot-admin @ 42be5a5c — the `spring-boot-admin-server-ui` module runs `frontend-maven-plugin`, whose downloaded Node binary fails with `libatomic.so.1: cannot open shared object file` — the system library is absent from the pinned builder image. The exclusion rests on E1 and E3 (identical error in both builds each); the E2 runs were confounded by a transient DNS outage on the runner host. Toolchain scope.
  5. AntonyCheng/spring-boot-init-template @ bd42361d — fails to compile identically in all three environments (maven-compiler-plugin "cannot find symbol" errors in the project's own sources at the pinned commit; 0 artifacts).
  6. ulisesbocchio/jasypt-spring-boot-samples @ 1199125c — depends on `jasypt-spring-boot:4.0.4-SNAPSHOT`, absent from Maven Central. Fails identically in all three environments (0 artifacts).
  7. spring-cloud/spring-cloud-kubernetes @ e102dc57 — the `kubernetes-leader-election-example` module runs the Boot `build-image` goal, which requires a Docker daemon; no socket exists inside the builder container. Fails identically in all three environments (build exit 1; 19 artifacts produced before the failing module).
  8. rahat9016/familie.munshi.backend @ 5f071063 — screening exclusion, corrected screen (Java 26). No build attempted.
  9. Hakky54/mutual-tls-ssl @ df050965 — screening exclusion, corrected screen (Java 21 via custom property). No build attempted.

## 4. Environments (the treatment)

Three environments; the build itself runs inside the same pinned container in each:

- **E1:** GitHub Actions hosted runner (`ubuntu-latest`, AMD64), build inside the pinned builder container.
- **E2:** GitLab CI on a self-hosted runner (docker executor) on the same ARM64 host as E3, same pinned builder image. GitLab.com shared runners require credit/debit card verification on the free tier, so E2 uses a self-hosted runner instead (no card, no minute allowance). The runner host is shared with E3, so the E2-vs-E3 comparison isolates the CI orchestrator context (GitLab-provided env vars, checkout paths, executor behavior) on identical hardware; E1 remains the fully independent environment. The orchestrator difference is the treatment; the shared machine is documented, not hidden. GitLab.com Free also requires account identity verification (phone/SMS or card) before any CI job runs; the phone route is the no-card path. Pull mirroring is Premium-only, so the GitLab project holds only a shim `.gitlab-ci.yml` whose jobs clone the harness from the public GitHub repo (single source of truth). The shim uses `spec:inputs` for run parameters; the `spec` block must be a separate YAML document (a `---` separator line between it and the jobs) or GitLab does not expose the inputs in the run-pipeline form.
- **E3:** Local Docker on a dedicated ARM64 host (Oracle Cloud, Ubuntu 24.04, Docker 29.1.3, 2 CPU, 11 GiB RAM), same pinned builder container.

**Held constant in every build:** pinned commit SHA; builder image (one Dockerfile: fixed JDK version, Maven version, OS base); identical build command; `SOURCE_DATE_EPOCH` set to the commit timestamp in all builds (controls the known timestamp cause, so remaining diffs are attributable to the environment); dependencies resolved from Maven Central, with resolved artifact hashes recorded per build to detect registry drift.

**Builder image distribution:** the image is built by a GitHub Actions workflow (`.github/workflows/build-builder-image.yml`) for linux/amd64 + linux/arm64 and published to GHCR; all three environments pull the same tag. Build records capture the image's manifest-list digest where the environment exposes it (E1 and E3); E2 records list the digest as unknown, because the GitLab runner's job-image digest is not visible inside the job. Each build uses a fresh per-build local Maven repository (resolution fully re-done per build; fingerprint recorded, repository then deleted for disk hygiene). Locale is fixed inside the image (C.UTF-8) and host locale/timezone vars are not passed into the container.

**What varies (the environment):** checkout path, runner user/hostname, runner-provided environment variables (`CI=true`, `GITHUB_*` / `CI_*` vars), filesystem, CPU count, locale/timezone defaults.

**Why the identical container is the key control:** if the toolchain differed between environments, a diff could be blamed on the toolchain. With the toolchain fixed, any cross-environment diff is leakage from the CI environment itself (paths, env vars, filesystem behavior). That attribution is what makes RQ1 interpretable — and it matches how real teams build (containerized builds in CI).

**Architecture difference (documented):** E1 runners are AMD64; E2's self-hosted runner shares the ARM64 host with E3. "Identical builder image" means identical Dockerfile, JDK/Maven versions, and tag, with per-architecture images resolved from the same manifest list. Architecture is a documented environment difference, not a hidden confound; pure-Java JAR bytes should be architecture-independent, and any architecture-attributable diff is classified as such under RQ2. No emulated builds were used.

**Builds per project:** 2 in each environment (6 total) in phase 1, plus re-verification builds after fixes. 25 projects × 6 = 150 phase-1 builds.

**Compute:** GitHub Actions is free for public repositories on standard runners. GitLab E2 uses a self-hosted runner, which consumes no shared-runner minutes. E3 costs only host machine time.

**Not using `act` or CI-workflow replay:** the AVP study's `act` replay pilot failed ~9/10 attempts. This study tests the project's build, not its CI workflow, so no workflow replay is attempted.

## 5. Measurement

- **Primary artifact:** the built fat JAR. **Identity:** SHA-256 of the JAR file (strict bitwise identity, the field standard).
- **Multi-module projects:** every produced JAR is hashed. Project-level match requires ALL artifacts to match; artifact-level match rates are also reported.
- **Within-environment match:** build 1 vs build 2 in the same environment. **Cross-environment match:** builds across E1/E2/E3 (first build per environment as canonical; all-pairs also recorded).

### Results (25 projects, 150 builds)

| # | Project | Pinned SHA | Artifacts | Within-env | Cross-env | Resolution fingerprints |
|---|---|---|---|---|---|---|
| 1 | introproventures/graphql-jpa-query | 649307fc | 14 | 0/14 | 0/14 | E2/E3 identical (5,326 files); E1 differs only in arch-specific plugin payload; 0 drift |
| 2 | VarshaUpadhyay/ScheduleDashboard | 831e0542 | 2 | 0/2 | 0/2 | All 6 identical (1,742 files) |
| 3 | Shitanshu686/shopping-app-backend | d1b392e7 | 1 | 0/1 | 0/1 | E2/E3 identical; E1 differs only in 4 arch-specific protobuf/gRPC binaries; 0 drift |
| 4 | spring-ai-community/spring-ai-agentcore | f0164a51 | 11 | 11/11 | 11/11 | All identical |
| 5 | operator-framework/josdk-spring-boot-starter | 1090e662 | 5 | 0/5 | 0/5 | All identical |
| 6 | luanferreiradev/algafood-api-algaworks | 6d6a357c | 1 | 0/1 | 0/1 | All identical (1,382 files) |
| 7 | Pawan-Ghode/Fintech-Payment-Processing-API | 15e31719 | 1 | 0/1 | 0/1 | All identical (1,156 files) |
| 8 | bulangya-bu/linguamate-agent | 48f8e1c6 | 1 | 0/1 | 0/1 | All identical (1,178 files) |
| 9 | Coelho-Techne/detectionSystem | 5b25beca | 1 | 0/1 | 0/1 | All identical (1,504 files) |
| 10 | Thissvane/PetsUniverseSpringBoot | 0daf2f16 | 1 | 0/1 | 0/1 | All identical (1,154 files) |
| 11 | dapr/java-sdk | f8c4c282 | 17 | 0/17 | 0/17 | 3,325 files; only diffs are resolver bookkeeping + arch payloads; 0 drift |
| 12 | amqphub/amqp-10-jms-spring-boot | 7d86d0c6 | 8 | 2/8 | 2/8 | All identical (1,630 files) |
| 13 | jdbc-observations/datasource-micrometer | b7c62115 | 4 | 0/4 | 0/4 | All identical (1,092 files) |
| 14 | HQfire/book-manager | 7073ab1d | 1 | 0/1 | 0/1 | All identical (1,310 files) |
| 15 | lunasaw/zlm-spring-boot-starter | 59a262c0 | 1 | 0/1 | 0/1 | 1,886 files; differ only in resolver bookkeeping; 0 drift |
| 16 | bansh2eBreak/SpringVulnBoot-backend | 31ea29b5 | 1 | 0/1 | 0/1 | All identical (1,910 files) |
| 17 | diva154/SpringMVC-to-SpringBoot-CRUDoperation-Migration | 4fa9ea7c | 1 | 0/1 | 0/1 | All identical (1,138 files) |
| 18 | penpencil721-lab/spring-boot-practice | 518e0564 | 1 | 0/1 | 0/1 | All identical (898 files) |
| 19 | jdubois/boot-ui | 1f5b25ed | 2,895 | 2,818/2,895 | 2,781/2,895 (E1 vs E2/E3); 2,818/2,895 (E2 vs E3) | 5,898 files; 0 drift |
| 20 | JoseOtavioJunqueira/desafio-itau-backend | 1d409ea9 | 1 | 0/1 | 0/1 | All identical (1,006 files) |
| 21 | codecentric/chaos-monkey-spring-boot | ecd224b7 | 9 | 0/9 | 0/9 | All identical (2,498 files) |
| 22 | spring-petclinic/spring-petclinic-data-jdbc | d601d3a8 | 1 | 0/1 | 0/1 | 2,342 files; differ only in 28 resolver bookkeeping files; 0 drift |
| 23 | apolloconfig/apollo | 504e5cd7 | 12 | 0/12 | 0/12 | All identical (3,606 files) |
| 24 | thangtranitwork/social-network | 739b9d7b | 1 | 0/1 | 0/1 | All identical (1,444 files) |
| 25 | Temirlan222/trello-main | 5f70a856 | 1 | 0/1 | 0/1 | All identical (1,146 files) |

**Summary:** 24 of 25 projects mismatch or partially match; 1 (agentcore, 11/11) is fully reproducible. Every project except amqp and boot-ui is a 0-match between every pair. Zero genuine dependency drift in all 25 — the only fingerprint differences are Maven resolver bookkeeping files and architecture-specific native payloads (see below). 9 candidates were excluded and replaced from spares (see §3).

**Baseline note:** a project can mismatch within one environment for reasons unrelated to the environment (project 1: all 14 JARs differed between two E3 builds — identical sizes, order, and manifest; only zip entry timestamps differed, set to build time because the project does not configure `outputTimestamp`). RQ1's cross-vs-within comparison is what separates baseline non-reproducibility from environment effects; the fix phase (RQ3) then reveals whether environment effects remain after normalization.

**Positive control:** agentcore (project 4) is byte-identical across all six builds, including across CPU architectures (x86_64 E1 vs aarch64 E2/E3). The harness detects reproducibility when a project configures it, so the 0-match results elsewhere are project properties, not measurement artifacts.

**Partial match:** amqp (project 12) is uniformly 2/8 between every pair — the 2 plain library JARs match everywhere; all 6 Boot-repackaged example fat JARs differ everywhere. Reproducibility varies by module type within one build.

**Fingerprint bookkeeping artifact:** `resolver-status.properties` (Maven resolver state) differs even within one environment. It appears in dapr (1 file), zlm (1 file), and petclinic (28 files). It is a fingerprint artifact, not dependency drift.

**Boot-ui (project 19)** is the sample's outlier in scale: 2,895 artifacts per build (~1GB), mostly Quarkus integration-test apps. Artifact sets differ by architecture: 18 E1-only + 18 E3-only paths (brotli4j native JARs, x86_64 vs aarch64 classifiers). On the 2,877 common paths, 19 artifacts are stable within every environment but differ across environments — the `bootui-quarkus-2.4.0.jar` module JAR plus copies embedded in different test apps. Entry-level comparison shows the 19 differ in exactly 2 entries each — `META-INF/quarkus-extension.json` and `.yaml` — in one field only: `scm-url`. E1's artifacts say `https://github.com/kdiveshr/reproducible-builds-ci-study` (the study repo); E2/E3 say `https://github.com/jdubois/boot-ui` (the target). The cause is a harness artifact: `run-in-container.sh` passes an allowlist of CI variables into the E1 container, including `GITHUB_REPOSITORY` (the study repo's workflow identity), and the Quarkus extension-descriptor plugin resolves scm-url from that CI context instead of the target clone's git remote. E2/E3 have no such variable and resolve from git correctly (all three builds run from nested target clones with their own .git, so nesting alone cannot explain the E1-only value). The finding stands, reframed: ambient CI context leaks into build artifacts — a genuine environment-sensitivity mechanism, distinct from architecture. Scope check: petclinic's git.properties shows the correct target repo/commit in E1 and E3 (differing only in build time and container hostname) — the git-commit-id plugin is unaffected; the leak is specific to the Quarkus plugin. I left the harness unchanged for the fix phase (protocol consistency); boot-ui fix verification is judged with this leak disclosed — the scm-url field is a known confound for E1 cross-environment pairs, not a project defect. (E2's first two boot-ui pipelines failed on artifact upload, HTTP 413 — the ~2GB output tree exceeded GitLab.com's limit; the shim was narrowed to records/logs/fingerprints only and the third attempt succeeded. Builds unchanged.)

**Diff analysis:** every non-matching pair got a diffoscope report (text + HTML) plus inspection of embedded metadata (`MANIFEST.MF`, `pom.properties`, `git.properties`, Spring Boot loader entries). Pilot classification (diffoscope 259, within-E1 pairs, 8 reports + independent zipfile cross-check; reports + classification notes in the replication package): 0 content differences in any pair; causes are zip entry timestamps (all 4 mismatching projects) plus entry ordering (ScheduleDashboard only). The phase-1 entry-level sweep (within-E1 pairs, all 20 phase-1 projects; boot-ui targeted separately) found TIMESTAMP_ONLY in every differing pair except: dapr's and chaos-monkey's fat JARs show nested-JAR "content" diffs that resolve recursively to zip timestamps inside the embedded JARs (0 content diffs in the checked nested JARs — TIMESTAMP, nested); spring-petclinic-data-jdbc and apollo show build-time metadata embedded as file content — new codebook code EMBEDDED_TIME, mapping to playbook step 6 — in three surfaces: `build.time` in META-INF/build-info.properties and `git.build.time` in BOOT-INF/classes/git.properties (petclinic), `git.build.time` + a timestamp comment line in apollo-git.properties in all 12 apollo modules, and build-time cache-buster query strings (`?v=yyyyMMddHHmmss`) stamped into 33 static HTML pages of apollo-portal. amqp's 2 library JARs are byte-identical within E1, confirming the partial-match pattern at entry level. No ORDERING in phase 1. Boot-ui targeted classification: the 19 cross-only artifacts differ in exactly one field (`scm-url`) — a CI-context leak from the harness's GITHUB_REPOSITORY allowlist (see above); the within-diff sample (bootui-agent) is TIMESTAMP_ONLY. New codebook code CI_CONTEXT for the boot-ui scm-url mechanism. (git.properties also embeds the container hostname, `git.build.host`, which differs per build — ambient build context, counted under EMBEDDED_TIME.) Diffoscope reports for phase-1 pairs (diffoscope 259, one representative within-E1 pair per project, 19 reports): 17 reports show ONLY a zipinfo section (timestamps, no content comparator fired); petclinic adds the 2 EMBEDDED_TIME properties files; apollo adds apollo-git.properties + 6 nested JARs carrying it — full agreement with the entry-level sweep. Project 1 (graphql-jpa-query) has no diffoscope report: its baseline JARs were not retained, and its classification rests on complete entry-level verification (all 14 artifacts, every entry hashed, 0 content diffs).

**Classification codebook:** seeded from Sharma et al.'s 6 causes and Xiong et al.'s 14 patterns, with emergent codes added as new causes appeared (EMBEDDED_TIME, CI_CONTEXT). All diffs were classified with the codebook; the codebook and raw diffoscope outputs are in the replication package so classification is auditable. A random 20% sample of diffs was re-classified independently on within-E3 pairs: 36/36 raw-code agreement (single-author mitigation for classification reliability).

**Dependency drift check:** resolved dependency hashes recorded per build. Drift is judged by same-path-different-hash: a resolved file at the same repository path with different bytes across builds. Path-set differences caused by architecture-specific plugin payloads (a formatting plugin downloads a platform-specific Node runtime, linux-x64 vs linux-arm64) are environment-attributable, not drift. The fingerprint excludes volatile bookkeeping (`_remote.repositories`, `maven-metadata-*.xml`, `*.lastUpdated`, plugin-rewritten lockfiles): with those excluded, two fresh resolutions minutes apart are byte-identical, and cross-environment fingerprints share 2,952 identical paths with 0 same-path-different-hash.

**Nested jars:** Spring Boot fat JARs embed dependency JARs; a timestamp difference in an embedded JAR propagates to the fat JAR's bytes. Diff classification recursed into embedded JARs (all 10 library JARs differed only in zip timestamps; the 4 fat JARs' only entry-content differences were their embedded library JARs).

## 6. Fix playbook and effort ledger (RQ3)

The playbook was written and frozen BEFORE phase-1 results were seen, so it cannot be fitted to the data. Steps applied in order, one at a time, rebuilding after each; stop when cross-environment match is achieved or the playbook is exhausted:

1. `SOURCE_DATE_EPOCH` — already set in all builds; if timestamp causes still appear, that is itself a finding.
2. Reproducible-build settings: `maven-archiver` / `outputTimestamp` configuration.
3. Absolute-path normalization (relative paths; strip build paths from embedded metadata).
4. Pin plugin versions (remove version ranges).
5. Archive ordering fixes (deterministic file ordering).
6. Neutralize build-time metadata (`git-commit-id` / `buildnumber` plugin config: disable or fix values).
7. Pin dependency versions (remove ranges / `LATEST`).

**Fix results, pilot:** Project 1 (graphql-jpa-query) was fixed by step 2 alone — a 2-line root-pom change (`project.build.outputTimestamp` = pinned commit time, fork branch `repro-step2-outputtimestamp`, commit ec198af2) took it from 0/14 to 14/14 between every pair, all three environments, 1 iteration. Fork: kdiveshr/graphql-jpa-query. Project 3 (shopping-app-backend) was fixed the same way — 2-line pom change (fork kdiveshr/shopping-app-backend, commit 20386c56), 0/1 → 1/1 between every pair, 1 iteration. Project 5 (josdk-spring-boot-starter) was fixed the same way — 2-line pom change (fork kdiveshr/josdk-spring-boot-starter, commit 2d5bc6f7), 0/5 → 5/5 between every pair, 1 iteration. ScheduleDashboard (TIMESTAMP + ORDERING) was fixed by step 2 alone in 3 iterations: the property was ignored by the 2019-era toolchain, a jar-plugin 3.3.0 pin fixed the plain JAR and the ordering, and a boot-plugin 2.3.12.RELEASE pin fixed the fat JAR's repackage-written loader entries — 0/2 → 2/2 between every pair, 9-line total diff (fork kdiveshr/ScheduleDashboard, branch repro-step2-outputtimestamp, head e682bf1e). All four mismatching pilot projects are fixed; agentcore needed no fix.

**Fix results, phase 1:** all 20 remaining mismatching projects were attempted under the same playbook. 19 were fixed with byte-identical artifacts between every pair: 17 by step 2 alone in 1 iteration each (algafood-api-algaworks 1/1, Fintech-Payment-Processing-API 1/1, linguamate-agent 1/1, detectionSystem 1/1, PetsUniverseSpringBoot 1/1, datasource-micrometer 4/4, book-manager 1/1, zlm-spring-boot-starter 1/1, SpringVulnBoot-backend 1/1, SpringMVC-to-SpringBoot migration 1/1, spring-boot-practice 1/1, desafio-itau-backend 1/1, social-network 1/1, trello-main 1/1, chaos-monkey-spring-boot 9/9, dapr/java-sdk 17/17, amqp-10-jms-spring-boot 8/8 — fix commits and run/pipeline IDs in the effort ledger). 2 needed steps 2 + 6: spring-petclinic-data-jdbc (3 attempts: step 2 normalized everything except `git.build.host` in git.properties; step 6 excluding the host field exposed a second CI-context leak, E2-side — the plugin read branch `main` and pipeline-number fields from the GitLab runner environment; excluding those too fixed it, 1/1 every pair, 9-line total diff, head 8209b81b) and apolloconfig/apollo (2 attempts: step 2 alone left 0/12 — its git-commit-id plugin 2.2.6 ignores outputTimestamp and the portal stamps a wall-clock cache-buster into 33 HTML pages; step 6 upgraded the plugin to 9.0.2 with host/branch/build-number exclusions and pinned the cache-buster to outputTimestamp, 12/12 every pair, head 93b97d13). The last project, jdubois/boot-ui (2,895 artifacts), is fixed with disclosed residuals after 3 iterations, all within step 2: attempt 1 failed — the Quarkus plugin rejects epoch-seconds outputTimestamp (SRCFG00039); attempt 2 used the ISO-8601 form of the same instant and reached 2,892/2,895 within E3, with the 3 remaining JARs written by Ant `<jar>` tasks that ignore outputTimestamp; attempt 3 added `modificationtime="${project.build.outputTimestamp}"` to both Ant tasks and reached 2,895/2,895 within every environment and E2-vs-E3. E1-vs-E2/E3 stands at 2,840/2,895: the gap is the 19 disclosed scm-url confound artifacts plus 18 Quarkus generated-bytecode.jar files carrying a genuine cross-environment ORDERING effect (1–2 generated recorder classes each, identical constant multisets in different constant-pool order, stable within each environment — no playbook step addresses generated-code constant ordering, so it is recorded as a finding). Fix-phase tally: 23 of 24 mismatching projects fully byte-identical across all six builds; boot-ui fixed except the disclosed residuals. Full per-project ledger: `effort-ledger.md` in the replication package.

**Effort ledger (kept contemporaneously — this is RQ3's data):** per project, wall-clock time split into diagnosis / fix / verification, diff size (lines added/removed), build iterations, outcome (fixed / partially fixed / not fixed), and the exact fix diff. Fixes live on a branch in a fork and go in the replication package. Upstream pull requests are out of scope for the paper (optional future work).

## 7. Analysis

- **RQ1:** within-environment match rate vs cross-environment match rate (per project, then aggregate), Wilson 95% intervals, paired comparison (McNemar on project-level matched/mismatched). Descriptive emphasis; n=25 limits inference. Result: 1/25 projects fully reproducible (4.0%, Wilson 95% CI 0.7–19.5%); excluding boot-ui, within- and cross-environment artifact match rates are identical (13/97 each); the McNemar discordance is entirely the 19 scm-url confound artifacts (p=3.8e-06 with them, p=1.0 without).
- **RQ2:** frequency table of causes; cross-environment-only causes highlighted; comparison against Sharma/Xiong taxonomies (which known causes appear, which new ones emerge).
- **RQ3:** fix success rate; effort distribution (median/IQR time, diff size, iterations); effort by cause.
- **Figures:** (1) match-rate comparison; (2) cause frequency; (3) effort distribution. Per-project results summarized in the paper, full table in the replication package.

## 8. Threats to validity

- **Construct:** SHA-256 is strict bitwise identity; semantically equivalent but byte-different artifacts count as failures. Standard in the field; equivalence-level frameworks (Dietrich et al.) provide context.
- **Internal:** single author (fix effort and classification are single-observer — mitigated by the codebook, re-classification sample, and full audit trail); dependency registry drift (mitigated by hash recording); CI platform changes mid-study (runner image digests and dates recorded).
- **External:** Maven + Spring Boot only; 25 public GitHub projects; results may not generalize to Gradle, other languages, or private codebases.
- **Conclusion:** small n means wide intervals; descriptive claims only, no population inference.

## 9. Replication package (IEEE DataPort)

Builder image Dockerfile + digest; build scripts; per-build SHA-256 hashes + full logs; dependency hash records; diffoscope reports; classification codebook + classifications; fix diffs; effort ledger; sample frame + selection/exclusion log; analysis scripts + figure data. Goal: one documented command re-runs any project's build in any environment.

## 10. Mapping to the venue's requirements

| Requirement | How this design answers it |
|---|---|
| New and novel, not experience/opinion/analysis | RQ1: controlled cross-environment comparison; Benedetti et al. explicitly excluded platform causes; no controlled study found |
| Traceable data, DataPort for replication | §9 replication package; every number traceable to a hash, log, or diffoscope report |
| Solid methodology, validation, evaluation | Controlled design, pilot-first, pre-registered playbook, codebook + re-classification sample, pre-written threats |
| Data provenance | All inputs are public open-source artifacts |
| Genuinely the author's own text | I write the article text; any AI assistance is disclosed in the article per venue policy |

## 11. Venue constraints (IEEE Software, verified Nov 14)

Max 4,200 words including 250 words per figure/table; abstract max 150 words; max 15 references; three actionable insights required with submission; author photo at full-submission stage. 31 sources were scanned; at most 15 can be cited, so related work is selective — the scan's catalogue is the selection pool. The three actionable insights come from RQ3's fix findings.

## 12. Decisions

Decisions made before the pilot (Nov 16):

1. Tests skipped (`-DskipTests`).
2. Maven-only (Gradle as future work).
3. Environments E1+E2+E3; E3 (local Docker) runs on the Oracle host.
4. Fixes stay in the replication package only; no upstream PRs in scope.
5. No star/popularity threshold; any project meeting the criteria qualifies.

## 13. Study repo + status

Study repo: https://github.com/kdiveshr/reproducible-builds-ci-study (public).

Measurement covered 25 of 25 projects (150 builds): 24 mismatch/partial, 1 fully reproducible (agentcore). Classification is complete, with diffoscope corroboration (27 reports) and a 20% re-classification sample (36/36 agreement). The fix phase left 23 of 24 mismatching projects fully byte-identical across all six builds; boot-ui is fixed except disclosed residuals (19 scm-url confound artifacts + 18 generated-bytecode jars with a genuine cross-environment ordering effect). Analysis (Wilson CIs, McNemar) attributes the entire cross-environment discordance to the 19 confound artifacts. The replication package was assembled and verified Nov 18 (2,118 files; all 338 build records; SHA-256 manifest).
