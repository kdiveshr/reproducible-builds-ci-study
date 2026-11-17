# Empirical study design: cross-environment reproducibility of Spring Boot application builds

**Status:** DRAFT for user review — Nov 16, 2026. Nothing run yet; no contact with IEEE Software.
**Purpose:** A practitioner-scale empirical study that answers the editor-in-chief's bar (novel contribution, traceable data on IEEE DataPort, solid methodology/validation/evaluation, genuinely the author's own text) using ONLY public open-source artifacts.
**Basis:** Literature scan of Nov 16–17, 2026 (31 sources).

## 1. The gap, in one paragraph

Every large reproducibility measurement builds everything on one machine with fixed infrastructure (Benedetti et al., ICSE 2025, explicitly), on a single CI platform and architecture (Solarin et al. 2026 Docker preprint, stated as its own limitation), or confounds environment change with the passage of time (Malka et al. 2026 Docker preprint: 2023 GitHub Actions builds vs later local rebuilds). Benedetti et al. explicitly exclude system-level and platform-specific causes from their scope. No published study performs a controlled same-source, multi-environment, hash-compared rebuild experiment. That is the gap: **does the CI environment itself change the artifact, when everything else is held constant?**

## 2. Research questions

- **RQ1 (comparison):** For the same pinned commit built with an identical builder image and build command, how does the artifact match rate across CI environments compare to the repeat-build match rate within a single environment?
- **RQ2 (causes):** Which differences appear only across environments, and how do they classify against the known Java cause taxonomies (Sharma et al. 2026, 6 causes; Xiong et al. 2022, 14 patterns)?
- **RQ3 (fix effort):** Using a pre-registered fix playbook, what fraction of cross-environment failures can be fixed, and what effort (time, diff size, build iterations) does each fix take?

## 3. Sample

- **Population:** Public GitHub repositories: Java + Maven + Spring Boot application producing an executable fat JAR via `spring-boot-maven-plugin`.
- **Inclusion criteria:** builds with a single documented command; active (a commit in the last 12 months); OSI-approved license; no native-code compilation step; full build under 15 minutes on a standard runner (calibrated in the pilot).
- **Size:** 25 projects target, 20 minimum after exclusions. Honest precision note: with n=25, a 95% Wilson interval on a 50% rate is roughly ±20 points. This is a descriptive study; the contribution is the controlled comparison, the cause taxonomy, and the effort data — not a population estimate. Say so in the paper.
- **Selection:** Frame enumerated Nov 16 via GitHub code search (`spring-boot-maven-plugin filename:pom.xml`; 7 pages fetched before the API rate limit stopped further fetching; GitHub reported 1,644,544 matching files and caps results at 1,000 per query). 290 unique non-fork public repos; screening order randomized with seed 20261116 (`harness/sample_frame.py`, `data/frame-candidates.json`). Screening proceeds in that order; activity (commit in last 12 months) and license are verified from each clone, since code-search results carry no pushed_at/license fields. Projects that fail to build in the reference environment for reasons unrelated to reproducibility (missing dependencies, dead links) are excluded and replaced, with the reason logged. Honest scope note: this is an enumerated convenience sample with randomized screening order, not a random draw from all Spring Boot projects — claims stay descriptive.
- **Tests:** Build with `mvn package -DskipTests`. Rationale: tests do not ship in the JAR, and flaky tests add noise unrelated to the artifact question. Documented as a scoping decision. (Decided Nov 16 — see §13.)
- **Screening progress (Nov 17):** all 290 v1 candidates screened in seed order; 3 passed — introproventures/graphql-jpa-query @ 649307fc (pilot project 1), bynour1/tp-cafe--jalila-ben-youssef @ 52e10e32, VarshaUpadhyay/ScheduleDashboard @ 831e0542. 287 excluded, mostly inactive (up to ~11 years stale), several active-but-unlicensed. The v1 frame is exhausted at a ~1% yield, so a supplement frame (v2) was enumerated Nov 17 via recency-filtered repo search (`spring-boot language:java pushed:>2025-11-16`; GitHub reported 171,171 matching repos; seed 20261117; `harness/enumerate_frame_v2.py`, `data/frame-candidates-v2.json`), with spring-boot-maven-plugin presence verified from clones at screening. Both frames are documented; claims stay descriptive. V2 screening complete Nov 17: 40 passed out of 779 (5.1% yield); full pass list in the host screening log (`~/study/screening-log.txt`). The first 3 passes in seed order (SolaceProducts/solace-spring-boot, Shitanshu686/shopping-app-backend, spring-ai-community/spring-ai-agentcore) are the next pilot candidates; builds running across E1/E2/E3.
- **Exclusions after build attempt (Nov 17):** bynour1/tp-cafe--jalila-ben-youssef @ 52e10e32 — EXCLUDED: `mvn package` fails identically in E1, E2, and E3 (spring-boot-maven-plugin 3.4.10 repackage goal cannot parse the pom's `<exclude>` configuration: "Cannot find 'version' in class org.springframework.boot.maven.Exclude"). Broken project configuration, unrelated to reproducibility; excluded and replaced per the pre-registered rule. SolaceProducts/solace-spring-boot @ 3454b5f9 — EXCLUDED: the root pom imports `com.solace.test.integration:solace-integration-test-support-bom:3.0.0`, which does not exist in Maven Central, so Maven cannot read the project (fails identically in E1, E2, and E3). Missing dependency, unrelated to reproducibility; excluded and replaced per the pre-registered rule.
- **Build system:** Maven only. Rationale: mixing Maven and Gradle adds a second treatment variable. Gradle is nearly unstudied (only 19 packages in BUILDGEN) and is the natural follow-up study, not part of this one. (Decided Nov 16 — see §13.)
- **Pilot:** 5 projects run end-to-end first (all environments, diff triage, one fix attempt). The pilot validates the harness and calibrates build times. Pilot projects stay in the final sample only if the protocol does not change after the pilot; otherwise they are replaced. Pre-register this rule before the pilot.

## 4. Environments (the treatment)

Three environments; the build itself runs inside the SAME pinned container in each:

- **E1:** GitHub Actions hosted runner (`ubuntu-latest`), build inside the pinned builder container.
- **E2:** GitLab CI on a self-hosted runner (docker executor) on the Oracle host, same pinned builder image. AMENDED Nov 16: GitLab.com shared runners require credit/debit card verification on the free tier, so E2 uses a self-hosted runner instead (no card, no minute allowance). The runner host is shared with E3, so the E2-vs-E3 comparison isolates the CI orchestrator context (GitLab-provided env vars, checkout paths, executor behavior) on identical hardware; E1 remains the fully independent environment. The orchestrator difference is the treatment; the shared machine is documented, not hidden. GitLab.com Free also requires account identity verification (phone/SMS or card) before ANY CI job runs — verified Nov 17; the phone route is the no-card path. Pull mirroring is Premium-only, so the GitLab project holds only a shim `.gitlab-ci.yml` whose jobs clone the harness from the public GitHub repo (single source of truth). The shim uses `spec:inputs` for run parameters; the `spec` block MUST be a separate YAML document (a `---` separator line between it and the jobs) or GitLab does not expose the inputs in the run-pipeline form — verified Nov 17 (the form showed "no inputs" until the separator was added).
- **E3:** Local Docker on the author's machine (or Oracle host), same pinned builder container.

**Held constant in every build:** pinned commit SHA; builder image pinned by digest (one Dockerfile: fixed JDK version, Maven version, OS base); identical build command; `SOURCE_DATE_EPOCH` set to the commit timestamp in all builds (controls the known timestamp cause, so remaining diffs are attributable to the environment); dependencies resolved from Maven Central, with resolved artifact hashes recorded per build to detect registry drift.

**Builder image distribution (Nov 16):** the image is built by a GitHub Actions workflow (`.github/workflows/build-builder-image.yml`) for linux/amd64 + linux/arm64 and published to GHCR; all three environments pull the same tag, and each build record captures the arch-native digest actually used. Each build uses a fresh per-build local Maven repository (resolution fully re-done per build; fingerprint recorded, repository then deleted for disk hygiene). Locale is fixed inside the image (C.UTF-8) and host locale/timezone vars are not passed into the container.

**What varies (the environment):** checkout path, runner user/hostname, runner-provided environment variables (`CI=true`, `GITHUB_*` / `CI_*` vars), filesystem, CPU count, locale/timezone defaults.

**Why the identical container is the key control:** if the toolchain differed between environments, a diff could be blamed on the toolchain. With the toolchain fixed, any cross-environment diff is leakage from the CI environment itself (paths, env vars, filesystem behavior). That attribution is what makes RQ1 interpretable — and it matches how real teams build (containerized builds in CI).

**Architecture difference (documented, Nov 16):** E3 (Oracle host) runs linux/aarch64 (ARM64; Docker 29.1.3, Ubuntu 24.04, 2 CPU, 11 GiB RAM, 56 GiB disk free; verified over SSH). E1 runners are AMD64; E2's self-hosted runner shares the ARM64 Oracle host with E3 (verified in E2 build records Nov 17). The same Dockerfile/tag therefore resolves to different per-architecture digests — "identical builder image" means identical Dockerfile, JDK/Maven versions, and tag, with the arch-native digest recorded per environment. Architecture is a documented environment difference, not a hidden confound; pure-Java JAR bytes should be architecture-independent, and any architecture-attributable diff is classified as such under RQ2. Emulated AMD64 builds on the ARM host (qemu) are NOT used — slow and flaky.

**Builds per project:** 2 in each environment (6 total) in phase 1, plus re-verification builds after fixes. 25 projects × 6 = 150 phase-1 builds.

**Compute / minutes — verify limits at run time:** GitHub Actions is free for public repositories on standard runners (verify current policy when the run starts). GitLab E2 uses a self-hosted runner, which consumes no shared-runner minutes (see the E2 amendment above); the free-tier shared-runner allowance is not a constraint. E3 costs only the author's machine time.

**Not using `act` or CI-workflow replay:** the AVP study's `act` replay pilot failed ~9/10 attempts. This study tests the project's build, not its CI workflow, so no workflow replay is attempted.

## 5. Measurement

- **Primary artifact:** the built fat JAR. **Identity:** SHA-256 of the JAR file (strict bitwise identity, the field standard).
- **Multi-module projects:** every produced JAR is hashed. Project-level match requires ALL artifacts to match; artifact-level match rates are also reported.
- **Within-environment match:** build 1 vs build 2 in the same environment. **Cross-environment match:** builds across E1/E2/E3 (first build per environment as canonical; all-pairs also recorded).
- **Baseline note (proof run, Nov 17):** a project can mismatch within one environment for reasons unrelated to the environment (pilot project 1: all 14 JARs differed between two E3 builds — identical sizes, order, and manifest; only zip entry timestamps differed, set to build time because the project does not configure `outputTimestamp`). RQ1's cross-vs-within comparison is what separates baseline non-reproducibility from environment effects; the fix phase (RQ3) then reveals whether environment effects remain after normalization.
- **Three-environment proof (Nov 17, project 1):** all 6 builds (2 per environment) succeeded, 14 artifacts each, identical artifact sets and sizes; match matrix 0/14 between EVERY pair (within-E1, within-E2, within-E3, and all cross-environment pairs). Toolchain identical everywhere (Temurin 17.0.15, Maven 3.9.9). E2 and E3 resolution fingerprints are byte-identical (5,326 files, same SHA-256), confirming identical dependency resolution on the shared ARM64 host; E1's resolution matched modulo the architecture-specific plugin payload (see drift check). The harness provenance file confirms E2 ran harness commit 40730071 (harness code identical to 2490ac59; later commits touched only the GitLab config).
- **Second project (Nov 17, VarshaUpadhyay/ScheduleDashboard @ 831e0542):** all 6 builds succeeded, 2 artifacts each, 0/2 between every pair (within and cross-environment), identical sizes. All six resolution fingerprints byte-identical (1,742 files) across E1/E2/E3 — zero drift, no architecture-payload difference (this project has no arch-specific plugin payload). Same within-environment baseline pattern as project 1. Entry-level check (E1 pair): 0 content differences, but TWO difference classes — zip entry timestamps AND entry ordering (same membership, different order, e.g., static assets ordered differently). Ordering is a second cause beyond timestamps; playbook step 5 applies.
- **Third project (Nov 17, Shitanshu686/shopping-app-backend @ d1b392e7):** all 6 builds succeeded, 1 artifact, 0/1 between every pair, identical sizes. E2/E3 resolution fingerprints byte-identical; E1's differs only in 4 architecture-specific protobuf/gRPC compiler binaries (linux-x86_64 vs linux-aarch_64), with 2,094 common paths and 0 same-path-different-hash — the same arch-payload pattern as project 1, not drift. Entry-level check (E1 pair): 0 content differences; only 7 of 543 entries differ, all timestamp-only (manifest + directory entries) — the timestamp cause presents narrowly here.
- **Fourth project (Nov 17, spring-ai-community/spring-ai-agentcore @ f0164a51):** all 6 builds succeeded, 11 artifacts, 11/11 between EVERY pair — fully reproducible within and across all three environments, including across CPU architectures (x86_64 E1 vs aarch64 E2/E3). All resolution fingerprints byte-identical. This is the study's positive control: the harness detects reproducibility when a project configures it, so the 0-match results elsewhere are project properties, not measurement artifacts.
- **Fifth project (Nov 17, operator-framework/josdk-spring-boot-starter @ 1090e662):** all 6 builds succeeded, 5 artifacts, 0/5 between every pair, identical sizes. All resolution fingerprints byte-identical across environments. Entry-level check (E1 pairs): 0 content differences in all 5 JARs; nearly all entries differ in timestamps only.
- **Diff analysis:** every non-matching pair gets a diffoscope report (text + HTML) plus inspection of embedded metadata (`MANIFEST.MF`, `pom.properties`, `git.properties`, Spring Boot loader entries). Pilot classification DONE Nov 17 (diffoscope 259, within-E1 pairs, 8 reports + independent zipfile cross-check; reports + CLASSIFICATION.md in the study workspace analysis/pilot-diffs/): 0 content differences in any pair; causes are zip entry timestamps (all 4 mismatching projects) plus entry ordering (ScheduleDashboard only). Codebook codes so far: TIMESTAMP, ORDERING.
- **Classification codebook:** seeded from Sharma et al.'s 6 causes and Xiong et al.'s 14 patterns, with emergent codes added as new causes appear. All diffs classified with the codebook; the codebook and raw diffoscope outputs go in the replication package so classification is auditable. A random 20% sample of diffs is re-classified after a gap, and agreement is reported (single-author mitigation for classification reliability).
- **Dependency drift check:** resolved dependency hashes recorded per build. Drift is judged by same-path-different-hash: a resolved file at the same repository path with different bytes across builds. Path-set differences caused by architecture-specific plugin payloads (verified Nov 17: a formatting plugin downloads a platform-specific Node runtime, linux-x64 vs linux-arm64) are environment-attributable, not drift. The fingerprint excludes volatile bookkeeping (`_remote.repositories`, `maven-metadata-*.xml`, `*.lastUpdated`, plugin-rewritten lockfiles) — verified Nov 17: with those excluded, two fresh resolutions minutes apart are byte-identical, and cross-environment fingerprints share 2,952 identical paths with 0 same-path-different-hash.
- **Nested jars:** Spring Boot fat JARs embed dependency JARs; a timestamp difference in an embedded JAR propagates to the fat JAR's bytes. Diff classification must recurse into embedded JARs (verified Nov 17: all 10 library JARs differed only in zip timestamps; the 4 fat JARs' only entry-content differences were their embedded library JARs).

## 6. Fix playbook and effort ledger (RQ3)

The playbook is written and frozen BEFORE phase-1 results are seen, so it cannot be fitted to the data. Steps applied in order, one at a time, rebuilding after each; stop when cross-environment match is achieved or the playbook is exhausted:

1. `SOURCE_DATE_EPOCH` — already set in all builds; if timestamp causes still appear, that is itself a finding.
2. Reproducible-build settings: `maven-archiver` / `outputTimestamp` configuration.
3. Absolute-path normalization (relative paths; strip build paths from embedded metadata).
4. Pin plugin versions (remove version ranges).
5. Archive ordering fixes (deterministic file ordering).
6. Neutralize build-time metadata (`git-commit-id` / `buildnumber` plugin config: disable or fix values).
7. Pin dependency versions (remove ranges / `LATEST`).

**Fix results (Nov 17):** Project 1 (graphql-jpa-query) FIXED by step 2 alone — a 2-line root-pom change (`project.build.outputTimestamp` = pinned commit time, fork branch `repro-step2-outputtimestamp`, commit ec198af2) took it from 0/14 to 14/14 between every pair, all three environments, 1 iteration. Fork: kdiveshr/graphql-jpa-query. Project 3 (shopping-app-backend) FIXED the same way — 2-line pom change (fork kdiveshr/shopping-app-backend, commit 20386c56), 0/1 → 1/1 between every pair, 1 iteration. Project 5 (josdk-spring-boot-starter) FIXED the same way — 2-line pom change (fork kdiveshr/josdk-spring-boot-starter, commit 2d5bc6f7), 0/5 → 5/5 between every pair, 1 iteration. Remaining pilot fix: ScheduleDashboard (TIMESTAMP + ORDERING — needs step 2 + step 5). FIXED Nov 17 by step 2 alone in 3 iterations (property ignored by the 2019-era toolchain; jar-plugin 3.3.0 pin fixed the plain JAR + ordering; boot-plugin 2.3.12.RELEASE pin fixed the fat JAR's repackage-written loader entries) — 0/2 → 2/2 between every pair, 9-line total diff (fork kdiveshr/ScheduleDashboard, branch repro-step2-outputtimestamp, head e682bf1e). ALL FOUR mismatching pilot projects are now fixed; agentcore needed no fix.

**Effort ledger (kept contemporaneously — this is RQ3's data):** per project, wall-clock time split into diagnosis / fix / verification, diff size (lines added/removed), build iterations, outcome (fixed / partially fixed / not fixed), and the exact fix diff. Fixes live on a branch in a fork and go in the replication package. Upstream pull requests are OUT of scope for the paper (optional future work). (Decided Nov 16 — see §13.)

## 7. Analysis

- **RQ1:** within-environment match rate vs cross-environment match rate (per project, then aggregate), Wilson 95% intervals, paired comparison (McNemar on project-level matched/mismatched). Descriptive emphasis; n=25 limits inference.
- **RQ2:** frequency table of causes; cross-environment-only causes highlighted; comparison against Sharma/Xiong taxonomies (which known causes appear, which new ones emerge).
- **RQ3:** fix success rate; effort distribution (median/IQR time, diff size, iterations); effort by cause.
- **Paper figures (3 max, budget-aware):** (1) match-rate comparison; (2) cause frequency; (3) effort distribution. Per-project results table summarized in the paper, full table in the replication package.

## 8. Threats to validity (pre-written, to be refined after results)

- **Construct:** SHA-256 is strict bitwise identity; semantically equivalent but byte-different artifacts count as failures. Standard in the field; note equivalence-level frameworks (Dietrich et al.) as context.
- **Internal:** single author (fix effort and classification are single-observer — mitigated by the codebook, re-classification sample, and full audit trail); dependency registry drift (mitigated by hash recording); CI platform changes mid-study (record runner image versions and dates).
- **External:** Maven + Spring Boot only; 25 public GitHub projects; results may not generalize to Gradle, other languages, or private codebases.
- **Conclusion:** small n means wide intervals; descriptive claims only, no population inference.

## 9. Replication package (IEEE DataPort)

Builder image Dockerfile + digest; build scripts; per-build SHA-256 hashes + full logs; dependency hash records; diffoscope reports; classification codebook + classifications; fix diffs; effort ledger; sample frame + selection/exclusion log; analysis scripts + figure data. Goal: one documented command re-runs any project's build in any environment.

## 10. Mapping to the venue's requirements

| Her requirement | How this design answers it |
|---|---|
| New and novel, not experience/opinion/analysis | RQ1: controlled cross-environment comparison; Benedetti et al. explicitly excluded platform causes; no controlled study found |
| Traceable data, DataPort for replication | §9 replication package; every number traceable to a hash, log, or diffoscope report |
| Solid methodology, validation, evaluation | Controlled design, pilot-first, pre-registered playbook, codebook + re-classification sample, pre-written threats |
| Company permission for company data | Not applicable — public artifacts only, no company data |
| Genuinely the author's own text | The author writes the article; AI assistance limited to structure/editing help, disclosed per venue policy |

## 11. Venue constraints (IEEE Software, verified Nov 14)

Max 4,200 words including 250 words per figure/table; abstract max 150 words; max 15 references; three actionable insights required with submission; author photo at full-submission stage. **Reference budget note:** 31 sources were scanned; at most 15 can be cited, so related work must be selective — the scan's catalogue is the selection pool. The three actionable insights should emerge from RQ3's fix findings, not be pre-written.

## 12. Timeline (spare time, elapsed — estimates)

- Weeks 1–2: harness + sample frame + pilot (5 projects).
- Weeks 3–5: full phase-1 run (150 builds, mostly automated; monitoring + diff triage).
- Weeks 6–8: fix phase (human-intensive; roughly 1–2 hours per failing project).
- Weeks 9–10: analysis + DataPort package.
- Weeks 11–14: writing (author's own text) + internal review.
- Then: submission + peer review (months, out of our control).

Total: ~3 months elapsed spare time before submission. The trade pitches already running are unaffected.

## 13. Decisions

All decided Nov 16 (user):
1. ✅ Tests skipped (`-DskipTests`).
2. ✅ Maven-only (Gradle as future work).
3. ✅ Environments E1+E2+E3; E3 (local Docker) runs on the Oracle host.
4. ✅ Fixes stay in the replication package only; no upstream PRs in scope.
5. ✅ No star/popularity threshold; any project meeting the criteria qualifies.

## 14. Study repo + status

Study repo: https://github.com/kdiveshr/reproducible-builds-ci-study (public, created Nov 16).

Status Nov 17: PILOT + FIX PHASE COMPLETE — all 5 pilot projects measured; all 4 mismatching ones FIXED by playbook step 2 (3 in 1 iteration, ScheduleDashboard in 3); agentcore was already reproducible. Diffoscope classification done (TIMESTAMP + ORDERING). Next: phase 1 — 20 more projects from the 36 remaining v2 passes, then analysis, replication package, and the user's own article writing.
