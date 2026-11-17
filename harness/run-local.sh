#!/usr/bin/env bash
# run-local.sh — convenience wrapper for the E3 (local Docker) environment.
# Runs on the Docker host. The work root must contain a checkout of this
# repository (so that harness/ is present inside the container mount).
#
# Usage: run-local.sh <repo-url> <commit-sha> [work-root] [image]
# Defaults: work-root $HOME/study, image ghcr.io/kdiveshr/reproducible-builds-ci-study-builder:latest
set -euo pipefail

REPO_URL="$1"
COMMIT_SHA="$2"
WORK_ROOT="${3:-$HOME/study}"
IMAGE="${4:-ghcr.io/kdiveshr/reproducible-builds-ci-study-builder:latest}"
HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$HARNESS_DIR/run-in-container.sh" "$IMAGE" "$WORK_ROOT" "$REPO_URL" "$COMMIT_SHA" E3
