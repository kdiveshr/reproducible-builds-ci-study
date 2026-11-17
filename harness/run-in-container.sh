#!/usr/bin/env bash
# run-in-container.sh — run the study builds inside the builder container.
#
# Runs on the HOST (GitHub Actions runner or local Docker host). The work
# root is mounted at the SAME path inside the container, so the build sees
# the environment's natural checkout path — the checkout path is part of the
# environment treatment, and mounting at a fixed path would hide it.
#
# Only an allowlist of CI variables is passed into the container (no secrets:
# never GITHUB_TOKEN / CI_JOB_TOKEN or anything secret-bearing). The
# container's own locale/timezone defaults apply; host locale vars are not
# passed through.
#
# Usage: run-in-container.sh <image> <work-root> <repo-url> <commit-sha> <env-name>
set -euo pipefail

IMAGE="$1"
WORK_ROOT="$2"
REPO_URL="$3"
COMMIT_SHA="$4"
ENV_NAME="$5"

WORK_ROOT="$(cd "$WORK_ROOT" && pwd)"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker pull "$IMAGE"
fi
BUILDER_DIGEST=$(docker image inspect --format '{{index .RepoDigests 0}}' "$IMAGE" 2>/dev/null || true)
if [ -z "$BUILDER_DIGEST" ] || [ "$BUILDER_DIGEST" = "<no value>" ]; then
  # Locally built image with no registry digest: record the image ID instead.
  BUILDER_DIGEST="local:$(docker image inspect --format '{{.Id}}' "$IMAGE")"
fi

ENVS=(-e "BUILDER_DIGEST=$BUILDER_DIGEST" -e "BUILDER_IMAGE=$IMAGE")
for v in CI GITHUB_REPOSITORY GITHUB_SHA GITHUB_REF GITHUB_RUN_ID GITHUB_RUN_NUMBER GITHUB_WORKSPACE GITHUB_ACTOR RUNNER_OS RUNNER_ARCH; do
  if [ -n "${!v:-}" ]; then ENVS+=(-e "$v=${!v}"); fi
done

docker run --rm \
  -v "$WORK_ROOT:$WORK_ROOT" \
  -w "$WORK_ROOT" \
  "${ENVS[@]}" \
  "$IMAGE" \
  bash harness/run-build.sh "$REPO_URL" "$COMMIT_SHA" "$ENV_NAME" "$WORK_ROOT/work" "$WORK_ROOT/out"
