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
open-source artifacts, and the full replication package will be published
with the article.

## Environments

- **E1** — GitHub Actions hosted runner, build inside the builder container.
- **E2** — GitLab CI, build inside the builder image on the project's
  self-hosted runner (tag `study-runner`). GitLab.com shared runners are not
  used (they require card verification on the free tier). Pull mirroring is
  Premium-only, so the GitLab project holds only a copy of `.gitlab-ci.yml`
  and each job clones the harness from here.
- **E3** — Local Docker on a dedicated host, same builder image.

The builder image is published to GHCR from
[`.github/workflows/build-builder-image.yml`](.github/workflows/build-builder-image.yml)
for `linux/amd64` and `linux/arm64` from one Dockerfile; each build record
captures the arch-native digest actually used.

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

## Method in brief

- Build command (identical everywhere): `mvn package -DskipTests`.
  Maven wrapper scripts are deliberately not used; the pinned Maven in the
  builder image is the toolchain. Tests are skipped: they do not ship in the
  JAR and flaky tests add noise unrelated to the artifact question.
- Two builds per environment (six per project in phase 1). Identity is
  strict bitwise identity: SHA-256 of the built fat JAR.
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

## Status

Harness v1 complete. Pilot project 1 (introproventures/graphql-jpa-query)
built twice each in E1 and E3: 0/14 artifacts matched between any two builds
— zip entry timestamps only, contents byte-identical. E2 is wired up (runner
online) and pending GitLab account identity verification. Full 5-project
pilot pending. Nothing is published from this repository yet.
