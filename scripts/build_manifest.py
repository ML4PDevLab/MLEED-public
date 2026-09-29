#!/usr/bin/env python3
"""Build or verify the explicit public-package inventory and SHA-256 checksums."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "metadata" / "release_manifest.json"
CHECKSUMS = ROOT / "SHA256SUMS"
PUBLIC_FILES = [
    ".gitattributes", ".gitignore", ".github/workflows/validate-data.yml",
    "README.md", "CHANGELOG.md", "requirements.txt",
    "data/mleed_country_month_2012_2025.csv",
    "docs/data_dictionary.md", "docs/repository_scope.md", "docs/reuse.md",
    "metadata/schema.json", "metadata/snapshot.json",
    "scripts/build_overview.py", "scripts/build_manifest.py",
    "scripts/export_long.py", "scripts/test_validation.py",
    "scripts/verify_evaluation.py", "validation/README.md",
    "validation/provenance.json", "validation/human_audit_summary.csv",
    "outputs/evaluation_verification.json",
    "outputs/data_quality_summary.json", "outputs/event_distribution.csv",
    "outputs/country_coverage.csv", "outputs/year_coverage.csv",
    "outputs/indicator_diagnostics.csv", "figures/event_distribution.png",
]
for mode in ["primary", "primary_or_secondary"]:
    for kind in ["classification_report", "confusion_matrix_raw", "confusion_matrix_normalized"]:
        PUBLIC_FILES.append(f"validation/classification/{kind}_{mode}_BINARY_THEN_EVENTS.csv")


def file_record(relative: str) -> dict:
    path = ROOT / relative
    return {"path": relative, "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify without modifying files")
    args = parser.parse_args()
    snapshot = json.loads((ROOT / "metadata/snapshot.json").read_text())
    manifest = {
        "manifest_version": 1,
        "snapshot_id": snapshot["snapshot_id"],
        "package_status": snapshot["status"],
        "scope": "Explicit public files only. The manifest and SHA256SUMS exclude themselves to avoid recursive hashes.",
        "files": [file_record(path) for path in sorted(PUBLIC_FILES)],
    }
    encoded = json.dumps(manifest, indent=2) + "\n"
    sums = "".join(f"{item['sha256']}  {item['path']}\n" for item in manifest["files"])
    if args.check:
        if MANIFEST.read_text() != encoded or CHECKSUMS.read_text() != sums:
            raise SystemExit("Manifest/checksums differ from current files; inspect changes before rebuilding.")
        print(f"Verified {len(PUBLIC_FILES)} public files and their sizes/checksums.")
    else:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(encoded, encoding="utf-8")
        CHECKSUMS.write_text(sums, encoding="utf-8")
        print(f"Wrote manifest and checksums for {len(PUBLIC_FILES)} public files.")


if __name__ == "__main__":
    main()
