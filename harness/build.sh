#!/usr/bin/env bash
# build.sh — run ONE instrumented build of the target project.
#
# Runs INSIDE the builder container, with CWD = the target project's checkout
# at the pinned commit. The build command is identical in every environment:
#   mvn package -DskipTests
# with SOURCE_DATE_EPOCH set to the commit timestamp and a fresh per-build
# local Maven repository, so dependency resolution is fully re-done per build.
#
# Maven wrapper scripts (mvnw) are deliberately NOT used: the pinned Maven in
# the builder image is the toolchain for every build.
#
# Usage: build.sh <env-name> <build-index> <out-dir>
# Writes into <out-dir>: clean.log, build.log, env-snapshot.txt,
# artifacts.txt, resolution-fingerprint.txt, build-record.json, artifacts/.
# Exits with the Maven build's exit code (the record is written either way).
set -uo pipefail

ENV_NAME="$1"
BUILD_INDEX="$2"
OUT_DIR="$3"
HARNESS_DIR="${HARNESS_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
REPO_URL="${REPO_URL:-unknown}"
BUILDER_IMAGE="${BUILDER_IMAGE:-unknown}"
BUILDER_DIGEST="${BUILDER_DIGEST:-unknown}"

mkdir -p "$OUT_DIR" "$OUT_DIR/artifacts"
STARTED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)

COMMIT_SHA=$(git rev-parse HEAD)
COMMIT_TS=$(git log -1 --format=%ct)
export SOURCE_DATE_EPOCH="$COMMIT_TS"

JAVA_VERSION=$(java -version 2>&1 | head -3 | tr '\n' ';')
MAVEN_VERSION=$(mvn -version 2>&1 | head -2 | tr '\n' ';')

# Sanitized environment snapshot: variable names + values, minus anything
# whose name looks secret-bearing (tokens, passwords, keys, credentials).
ENV_SNAPSHOT_FILE="$OUT_DIR/env-snapshot.txt"
env | LC_ALL=C sort \
  | grep -viE '^[A-Za-z0-9_]*(TOKEN|SECRET|PASSWORD|PASSWD|PRIVATE|CREDENTIAL)[A-Za-z0-9_]*=' \
  | grep -viE '^[A-Za-z0-9_]*KEY=' \
  > "$ENV_SNAPSHOT_FILE" || true

# Fresh per-build local repository: resolution is re-done from Maven Central
# on every build, so the resolution fingerprint detects registry drift.
M2_DIR="$OUT_DIR/m2-repo"
mkdir -p "$M2_DIR"

mvn -B clean >"$OUT_DIR/clean.log" 2>&1 || true
set +e
mvn -B package -DskipTests -Dmaven.repo.local="$M2_DIR" >"$OUT_DIR/build.log" 2>&1
BUILD_EXIT=$?
set -e
FINISHED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Artifacts: every built JAR except .original / sources / javadoc / tests jars.
ARTIFACTS_FILE="$OUT_DIR/artifacts.txt"
: > "$ARTIFACTS_FILE"
while IFS= read -r jar; do
  rel="${jar#./}"
  sha=$(sha256sum "$jar" | awk '{print $1}')
  size=$(stat -c%s "$jar")
  echo "$sha  $rel  $size" >> "$ARTIFACTS_FILE"
  flat_name=$(echo "$rel" | tr '/' '_')
  cp "$jar" "$OUT_DIR/artifacts/$flat_name"
done < <(find . -path '*/target/*.jar' ! -name '*.original' ! -name '*-sources.jar' ! -name '*-javadoc.jar' ! -name '*-tests.jar' | LC_ALL=C sort)

# Resolution fingerprint: every file in the fresh per-build local repository,
# except volatile metadata (download-failure markers, remote metadata files
# that carry fetch timestamps).
FINGERPRINT_FILE="$OUT_DIR/resolution-fingerprint.txt"
(cd "$M2_DIR" && find . -type f ! -name '*.lastUpdated' ! -name 'maven-metadata-*.xml' | LC_ALL=C sort | xargs -r sha256sum) > "$FINGERPRINT_FILE"

python3 "$HARNESS_DIR/record.py" \
  --out-dir "$OUT_DIR" \
  --env-name "$ENV_NAME" \
  --build-index "$BUILD_INDEX" \
  --repo-url "$REPO_URL" \
  --commit-sha "$COMMIT_SHA" \
  --commit-ts "$COMMIT_TS" \
  --builder-image "$BUILDER_IMAGE" \
  --builder-digest "$BUILDER_DIGEST" \
  --checkout-path "$PWD" \
  --java-version "$JAVA_VERSION" \
  --maven-version "$MAVEN_VERSION" \
  --started-at "$STARTED_AT" \
  --finished-at "$FINISHED_AT" \
  --exit-code "$BUILD_EXIT"

exit "$BUILD_EXIT"
