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
- **Tests:** Build with `mvn package -DskipTests`. Rationale: tests do not ship in the JAR, and flaky tests add noise unrelated to the artifact question. Documented as a scoping decision. **[Decision 1 for the user: confirm.]**
- **Build system:** Maven only. Rationale: mixing Maven and Gradle adds a second treatment variable. Gradle is nearly unstudied (only 19 packages in BUILDGEN) and is the natural follow-up study, not part of this one. **[Decision 2 for the user: confirm Maven-only.]**
- **Pilot:** 5 projects run end-to-end first (all environments, diff triage, one fix attempt). The pilot validates the harness and calibrates build times. Pilot projects stay in the final sample only if the protocol does not change after the pilot; otherwise they are replaced. Pre-register this rule before the pilot.

## 4. Environments (the treatment)

Three environments; the build itself runs inside the SAME pinned container in each:

- **E1:** GitHub Actions hosted runner (`ubuntu-latest`), build inside the pinned builder container.
- **E2:** GitLab CI shared runner (docker executor), same pinned builder container.
- **E3:** Local Docker on the author's machine (or Oracle host), same pinned builder container.

**Held constant in every build:** pinned commit SHA; builder image pinned by digest (one Dockerfile: fixed JDK version, Maven version, OS base); identical build command; `SOURCE_DATE_EPOCH` set to the commit timestamp in all builds (controls the known timestamp cause, so remaining diffs are attributable to the environment); dependencies resolved from Maven Central, with resolved artifact hashes recorded per build to detect registry drift.

**What varies (the environment):** checkout path, runner user/hostname, runner-provided environment variables (`CI=true`, `GITHUB_*` / `CI_*` vars), filesystem, CPU count, locale/timezone defaults.

**Why the identical container is the key control:** if the toolchain differed between environments, a diff could be blamed on the toolchain. With the toolchain fixed, any cross-environment diff is leakage from the CI environment itself (paths, env vars, filesystem behavior). That attribution is what makes RQ1 interpretable — and it matches how real teams build (containerized builds in CI).

**Architecture difference (documented, Nov 16):** E3 (Oracle host) runs linux/aarch64 (ARM64; Docker 29.1.3, Ubuntu 24.04, 2 CPU, 11 GiB RAM, 56 GiB disk free; verified over SSH). E1/E2 runners are AMD64. The same Dockerfile/tag therefore resolves to different per-architecture digests — "identical builder image" means identical Dockerfile, JDK/Maven versions, and tag, with the arch-native digest recorded per environment. Architecture is a documented environment difference, not a hidden confound; pure-Java JAR bytes should be architecture-independent, and any architecture-attributable diff is classified as such under RQ2. Emulated AMD64 builds on the ARM host (qemu) are NOT used — slow and flaky.

**Builds per project:** 2 in each environment (6 total) in phase 1, plus re-verification builds after fixes. 25 projects × 6 = 150 phase-1 builds.

**Compute / minutes — verify limits at run time:** GitHub Actions is free for public repositories on standard runners (verify current policy when the run starts). GitLab.com's free tier has a monthly shared-runner minute allowance (verify current allowance; if 50 builds exceed it, spread E2 across calendar months). E3 costs only the author's machine time. **[Decision 3 for the user: confirm E1+E2+E3, and where E3 runs.]**

**Not using `act` or CI-workflow replay:** the AVP study's `act` replay pilot failed ~9/10 attempts. This study tests the project's build, not its CI workflow, so no workflow replay is attempted.

## 5. Measurement

- **Primary artifact:** the built fat JAR. **Identity:** SHA-256 of the JAR file (strict bitwise identity, the field standard).
- **Within-environment match:** build 1 vs build 2 in the same environment. **Cross-environment match:** builds across E1/E2/E3 (first build per environment as canonical; all-pairs also recorded).
- **Diff analysis:** every non-matching pair gets a diffoscope report (text + HTML) plus inspection of embedded metadata (`MANIFEST.MF`, `pom.properties`, `git.properties`, Spring Boot loader entries).
- **Classification codebook:** seeded from Sharma et al.'s 6 causes and Xiong et al.'s 14 patterns, with emergent codes added as new causes appear. All diffs classified with the codebook; the codebook and raw diffoscope outputs go in the replication package so classification is auditable. A random 20% sample of diffs is re-classified after a gap, and agreement is reported (single-author mitigation for classification reliability).
- **Dependency drift check:** resolved dependency hashes recorded per build. If a cross-environment diff coincides with a dependency hash change, it is flagged as registry drift, not an environment effect.

## 6. Fix playbook and effort ledger (RQ3)

The playbook is written and frozen BEFORE phase-1 results are seen, so it cannot be fitted to the data. Steps applied in order, one at a time, rebuilding after each; stop when cross-environment match is achieved or the playbook is exhausted:

1. `SOURCE_DATE_EPOCH` — already set in all builds; if timestamp causes still appear, that is itself a finding.
2. Reproducible-build settings: `maven-archiver` / `outputTimestamp` configuration.
3. Absolute-path normalization (relative paths; strip build paths from embedded metadata).
4. Pin plugin versions (remove version ranges).
5. Archive ordering fixes (deterministic file ordering).
6. Neutralize build-time metadata (`git-commit-id` / `buildnumber` plugin config: disable or fix values).
7. Pin dependency versions (remove ranges / `LATEST`).

**Effort ledger (kept contemporaneously — this is RQ3's data):** per project, wall-clock time split into diagnosis / fix / verification, diff size (lines added/removed), build iterations, outcome (fixed / partially fixed / not fixed), and the exact fix diff. Fixes live on a branch in a fork and go in the replication package. Upstream pull requests are OUT of scope for the paper (optional future work). **[Decision 4 for the user: confirm fixes stay in the replication package, no upstream PRs in scope.]**

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

## 14. Study repo + next step

Study repo: https://github.com/kdiveshr/reproducible-builds-ci-study (public, created Nov 16).

Next: build the harness — builder image Dockerfile, build-and-hash script — and start screening/pilot on 5 projects. (Sample-frame enumeration is done: §3.)
