#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path
import re
import subprocess

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = REPO_ROOT / "commands"
TIMESTAMP_FIELDS = ("addedAt", "updatedAt")


def find_manifest_files() -> list[Path]:
    return sorted(
        [
            *COMMANDS_DIR.glob("*/*/manifest.yaml"),
            *COMMANDS_DIR.glob("*/*/manifest.yml"),
        ]
    )


def utc_timestamp(value: str | None = None) -> str:
    timestamp = datetime.now(UTC) if value is None else datetime.fromisoformat(value)
    return (
        timestamp.astimezone(UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def manifest_history(manifest_file: Path) -> tuple[str, str]:
    relative_path = manifest_file.relative_to(REPO_ROOT)
    result = subprocess.run(
        [
            "git",
            "-C",
            str(REPO_ROOT),
            "log",
            "--follow",
            "--format=%cI",
            "--",
            str(relative_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    dates = [line for line in result.stdout.splitlines() if line]

    if not dates:
        now = utc_timestamp()
        return now, now

    # git log returns newest first. These dates are approximate when a command
    # was renamed or migrated from an older manifest format.
    return utc_timestamp(dates[-1]), utc_timestamp(dates[0])


def set_timestamp_fields(
    manifest_file: Path,
    added_at: str,
    updated_at: str,
    *,
    force: bool,
) -> bool:
    text = manifest_file.read_text(encoding="utf-8")
    values = {"addedAt": added_at, "updatedAt": updated_at}
    missing: list[str] = []

    for field in TIMESTAMP_FIELDS:
        pattern = re.compile(rf"^{field}:.*$", re.MULTILINE)
        replacement = f'{field}: "{values[field]}"'
        if pattern.search(text):
            if force:
                text = pattern.sub(replacement, text, count=1)
        else:
            missing.append(replacement)

    if missing:
        schema_version = re.compile(r"^schemaVersion:.*$", re.MULTILINE)
        if not schema_version.search(text):
            raise ValueError(f"{manifest_file}: missing schemaVersion")
        insertion = "\n".join(missing)
        text = schema_version.sub(
            lambda match: f"{match.group(0)}\n{insertion}",
            text,
            count=1,
        )

    original = manifest_file.read_text(encoding="utf-8")
    if text == original:
        return False

    manifest_file.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Backfill approximate addedAt and updatedAt UTC timestamps in "
            "command manifests from Git history."
        )
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace timestamps that are already present",
    )
    args = parser.parse_args()

    changed = 0
    manifests = find_manifest_files()
    for manifest_file in manifests:
        added_at, updated_at = manifest_history(manifest_file)
        if set_timestamp_fields(
            manifest_file,
            added_at,
            updated_at,
            force=args.force,
        ):
            changed += 1
            print(
                f"Updated {manifest_file.relative_to(REPO_ROOT)}: "
                f"addedAt={added_at}, updatedAt={updated_at}"
            )

    print(f"Updated {changed} of {len(manifests)} manifests.")


if __name__ == "__main__":
    main()
