# Cross-environment reproducibility of Spring Boot application builds

An empirical study: does the CI environment itself change the built artifact,
when the source, toolchain, and build command are held constant?

Every large reproducibility measurement so far builds everything on one
machine, on a single CI platform, or confounds environment change with the
passage of time. This study runs a controlled same-source, multi-environment,
hash-compared rebuild experiment: the same pinned commit, built twice in each
of three CI environments, inside the same pinned builder container, with
`SOURCE_DATE_EPOCH` fixed to the commit timestamp in all builds. Any
cross-environment difference is then leakage from the CI environment itself.

Study design: [docs/study-design.md](docs/study-design.md). The study is
intended to support an article for IEEE Software; all inputs are public
open-source artifacts, and the full replication package accompanies the article (assembled November 2026).

## Environments

- **E1** — GitHub Actions hosted runner (AMD64), build inside the builder
  container.
- **E2** — GitLab CI, build inside the builder image on the project's
  self-hosted runner (tag `study-runner`, ARM64). GitLab.com shared runners
  are not used (they require card verification on the free tier). Pull
  mirroring is Premium-only, so the GitLab project holds only a copy of
  `.gitlab-ci.yml` and each job clones the harness from here.
- **E3** — Local Docker on a dedicated ARM64 host, same builder image.

The builder image is published to GHCR from
[`.github/workflows/build-builder-image.yml`](.github/workflows/build-builder-image.yml)
for `linux/amd64` and `linux/arm64` from one Dockerfile. E1 and E3 build
records capture the image's manifest-list digest; E2 records list the digest
as unknown, because the GitLab runner's job-image digest is not visible
inside the job.

## Layout

- `harness/builder/Dockerfile` — the builder image (pinned JDK + Maven).
- `harness/build.sh` — one instrumented build (runs inside the container).
- `harness/run-build.sh` — clone a pinned commit, run two builds.
- `harness/run-in-container.sh` — host-side wrapper (E1/E3): run the builds
  inside the container with the work root mounted at the same path.
- `harness/run-local.sh` — convenience wrapper for E3.
- `harness/record.py` — writes `build-record.json` per build.
- `harness/sample_frame.py` — sample-frame enumeration (seeded, auditable).
- `.github/workflows/study-build.yml` — E1 pipeline (manual dispatch).
- `.gitlab-ci.yml` — E2 pipeline definition, copied into the GitLab project
  (manual run; `repo_url`/`commit_sha` inputs).
- `docs/study-design.md` — full study design.
- `sources.md` — every sampled project: repository link, pinned commit
  built, and fix fork/branch/commit.
- `analysis/` — diffoscope reports, entry-level classifications, the
  classification summary, and the analysis scripts + results.
- `fixes/` — the RQ3 effort ledger (diagnosis/fix/verification time, diff
  size, iterations, outcome per project).

## Method in brief

- Build command (identical everywhere): `mvn package -DskipTests`.
  Maven wrapper scripts are deliberately not used; the pinned Maven in the
  builder image is the toolchain. Tests are skipped: they do not ship in the
  JAR and flaky tests add noise unrelated to the artifact question.
- Two builds per environment (six per project). Identity is strict bitwise
  identity: SHA-256 of every produced JAR; a project matches only if all of
  its artifacts match.
- Each build uses a fresh per-build local Maven repository, so dependency
  resolution is fully re-done per build; a fingerprint of everything resolved
  is recorded to detect registry drift.
- Non-matching pairs get diffoscope reports, classified against the Sharma et
  al. / Xiong et al. Java cause taxonomies. A pre-registered fix playbook and
  effort ledger cover the fix phase (see the design doc).

## Running one project

E1 (GitHub Actions): run the `study-build` workflow with the repo URL and
commit SHA. E2 (GitLab CI): start a manual pipeline with the `repo_url` and
`commit_sha` inputs. E3 (local Docker):

```sh
bash harness/run-local.sh <repo-url> <commit-sha> [work-root] [image]
```

Outputs land under `out/<repo-slug>/<env>/build-{1,2}/`: build logs, artifact
hashes, the resolution fingerprint, a sanitized environment snapshot, and
`build-record.json`.

## Status and results

Measurement, classification, fix phase, and analysis are complete
(November 2026).

- **Sample:** 25 public Spring Boot (Maven) projects, 150 builds.
  1 of 25 projects (4.0%, Wilson 95% CI 0.7–19.5%) was byte-identical
  across all six builds as-is. Zero genuine dependency drift in all 25.
- **Causes:** zip entry timestamps dominate (persisting despite
  `SOURCE_DATE_EPOCH`); entry ordering and build-time metadata embedded as
  file content appear in a minority of projects. Two causes found here did
  not fit the published taxonomies and are reported as new codes: ambient CI
  context leaking into artifacts, and build-time metadata embedded as file
  content.
- **Fixes:** 23 of the 24 mismatching projects became fully byte-identical
  across all six builds after playbook fixes — 20 from the two-line
  `outputTimestamp` change alone. The remaining project (boot-ui) is fixed
  within every environment, with disclosed cross-environment residuals.
- **Cross- vs within-environment:** excluding the one scale outlier, the
  within-environment and cross-environment match rates are identical
  (13/97 artifacts each); the entire raw cross-environment effect is
  attributable to a disclosed harness artifact (see the design doc).

Full numbers, the classification codebook, threats to validity, and the
replication-package specification are in the design doc; per-build hashes,
logs, and diffoscope reports are in the replication package.
