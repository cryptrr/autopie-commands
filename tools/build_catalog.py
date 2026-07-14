#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import json

from manifest_io import find_manifest_files, load_manifest

CATALOG_SCHEMA_VERSION = "2026.6.1"
CATALOG_SCHEMA_PATH = (
    "schema/2026.6.1/catalog.schema.json"
)

COMMANDS_DIR = Path("commands")
OUTPUT_FILE = Path("catalog.json")


def build_catalog() -> dict:
    catalog = {
        "$schema": CATALOG_SCHEMA_PATH,
        "schemaVersion": CATALOG_SCHEMA_VERSION,
        "generatedAt": datetime.now(UTC)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
        "commands": {}
    }

    manifests = find_manifest_files(COMMANDS_DIR)

    for manifest_file in manifests:
        manifest = load_manifest(manifest_file)

        command_id = manifest["id"]

        catalog["commands"][command_id] = {
            "version": manifest["version"],
            "name": manifest["name"],
            "summary": manifest["summary"],
            "namespace": manifest["namespace"],
            "status": manifest["status"],
            "tags": manifest.get("tags", [])
        }

    return catalog


def main():
    catalog = build_catalog()

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            catalog,
            f,
            indent=2,
            sort_keys=True,
            ensure_ascii=False
        )
        f.write("\n")

    print(
        f"Generated {OUTPUT_FILE} "
        f"with {len(catalog['commands'])} commands."
    )

    
if __name__ == "__main__":
    main()
