#!/usr/bin/env python3
"""Write build-record.json for one instrumented build.

Reads the artifacts/fingerprint files build.sh produced in OUT_DIR and
combines them with the build parameters passed as arguments. Every number in
the study traces back to one of these records plus its logs.
"""
import argparse
import hashlib
import json
import os
import platform
import socket


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--env-name", required=True)
    ap.add_argument("--build-index", required=True, type=int)
    ap.add_argument("--repo-url", required=True)
    ap.add_argument("--commit-sha", required=True)
    ap.add_argument("--commit-ts", required=True)
    ap.add_argument("--builder-image", default="unknown")
    ap.add_argument("--builder-digest", default="unknown")
    ap.add_argument("--checkout-path", required=True)
    ap.add_argument("--java-version", required=True)
    ap.add_argument("--maven-version", required=True)
    ap.add_argument("--started-at", required=True)
    ap.add_argument("--finished-at", required=True)
    ap.add_argument("--exit-code", required=True, type=int)
    args = ap.parse_args()

    artifacts = []
    art_path = os.path.join(args.out_dir, "artifacts.txt")
    if os.path.exists(art_path):
        for line in open(art_path):
            parts = line.rstrip("\n").split("  ")
            if len(parts) == 3:
                artifacts.append(
                    {"sha256": parts[0], "path": parts[1], "size_bytes": int(parts[2])}
                )

    fp_path = os.path.join(args.out_dir, "resolution-fingerprint.txt")
    fp_sha = sha256_file(fp_path) if os.path.exists(fp_path) else None
    fp_count = sum(1 for _ in open(fp_path)) if os.path.exists(fp_path) else 0

    try:
        cpu_count = os.cpu_count()
    except Exception:
        cpu_count = None

    record = {
        "schema_version": 1,
        "project": {
            "repo_url": args.repo_url,
            "commit_sha": args.commit_sha,
            "commit_timestamp": int(args.commit_ts),
            "source_date_epoch": int(args.commit_ts),
        },
        "environment": {
            "name": args.env_name,
            "builder_image": args.builder_image,
            "builder_digest": args.builder_digest,
            "checkout_path": args.checkout_path,
            "hostname": socket.gethostname(),
            "os": platform.platform(),
            "arch": platform.machine(),
            "cpu_count": cpu_count,
            "java_version": args.java_version,
            "maven_version": args.maven_version,
        },
        "build": {
            "index": args.build_index,
            "started_at_utc": args.started_at,
            "finished_at_utc": args.finished_at,
            "exit_code": args.exit_code,
            "status": "success" if args.exit_code == 0 else "failed",
        },
        "artifacts": artifacts,
        "resolution": {
            "fingerprint_sha256": fp_sha,
            "files_count": fp_count,
            "exclusions": ["*.lastUpdated", "maven-metadata-*.xml"],
        },
        "logs": [
            "clean.log",
            "build.log",
            "env-snapshot.txt",
            "artifacts.txt",
            "resolution-fingerprint.txt",
        ],
    }
    with open(os.path.join(args.out_dir, "build-record.json"), "w") as f:
        json.dump(record, f, indent=2, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
