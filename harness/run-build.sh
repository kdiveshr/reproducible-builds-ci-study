#!/usr/bin/env bash
# run-build.sh — clone a target repo at a pinned commit and run two
# instrumented builds of it (the within-environment repeat pair).
#
# Runs INSIDE the builder container in all environments. In GitHub Actions
# and local Docker it is invoked through harness/run-in-container.sh; in
# GitLab CI the job already runs inside the builder image, so the pipeline
# calls this script directly.
#
# Usage: run-build.sh <repo-url> <commit-sha> <env-name> <work-root> <out-root>
# Output: <out-root>/<slug>/<env-name>/build-{1,2}/ + run-manifest.json
# Exit code: 0 only if both builds succeeded.
set -euo pipefail

REPO_URL="$1"
COMMIT_SHA="$2"
ENV_NAME="$3"
WORK_ROOT="$4"
OUT_ROOT="$5"

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export HARNESS_DIR REPO_URL

SLUG=$(echo "$REPO_URL" | sed -E 's#.*github.com/##; s#\.git$##; s#[^A-Za-z0-9._-]+#_#g')
SHORT_SHA="${COMMIT_SHA:0:12}"
TARGET_DIR="$WORK_ROOT/$SLUG-$SHORT_SHA"
RUN_OUT="$OUT_ROOT/$SLUG/$ENV_NAME"
mkdir -p "$WORK_ROOT" "$RUN_OUT"

if [ -d "$TARGET_DIR" ]; then rm -rf "$TARGET_DIR"; fi
git clone --quiet "$REPO_URL" "$TARGET_DIR"
(cd "$TARGET_DIR" && git checkout --quiet "$COMMIT_SHA")

FAIL=0
STATUS1="failed"
STATUS2="failed"
if (cd "$TARGET_DIR" && bash "$HARNESS_DIR/build.sh" "$ENV_NAME" 1 "$RUN_OUT/build-1"); then
  STATUS1="success"
else
  FAIL=1
fi
if (cd "$TARGET_DIR" && bash "$HARNESS_DIR/build.sh" "$ENV_NAME" 2 "$RUN_OUT/build-2"); then
  STATUS2="success"
else
  FAIL=1
fi

printf '{\n  "repo_url": "%s",\n  "commit_sha": "%s",\n  "environment": "%s",\n  "build_1": "%s",\n  "build_2": "%s"\n}\n' \
  "$REPO_URL" "$COMMIT_SHA" "$ENV_NAME" "$STATUS1" "$STATUS2" > "$RUN_OUT/run-manifest.json"

exit "$FAIL"
