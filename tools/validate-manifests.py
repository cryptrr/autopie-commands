from pathlib import Path
from datetime import UTC, datetime
import re

from manifest_io import find_manifest_files, load_manifest

ID_RE = re.compile(r"^[a-z][a-z0-9_-]*\.[a-z][a-z0-9_-]*$")
UTC_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

seen_ids = set()

for manifest_file in find_manifest_files(Path("commands")):
    manifest = load_manifest(manifest_file)
    command_dir = manifest_file.parent

    namespace = command_dir.parent.name
    slug = command_dir.name

    expected_id = f"{namespace}.{slug}"

    if manifest["id"] != expected_id:
        raise Exception(
            f"{manifest_file}: expected id '{expected_id}'"
        )

    if manifest["id"] in seen_ids:
        raise Exception(
            f"Duplicate id: {manifest['id']}"
        )

    seen_ids.add(manifest["id"])

    timestamps = {}
    for field in ("addedAt", "updatedAt"):
        value = manifest.get(field)
        if not isinstance(value, str) or not UTC_TIMESTAMP_RE.fullmatch(value):
            raise Exception(
                f"{manifest_file}: {field} must be a UTC timestamp "
                "formatted as YYYY-MM-DDTHH:MM:SSZ"
            )
        timestamps[field] = datetime.fromisoformat(value).astimezone(UTC)

    if timestamps["updatedAt"] < timestamps["addedAt"]:
        raise Exception(
            f"{manifest_file}: updatedAt must not be earlier than addedAt"
        )

    readme = command_dir / manifest["docs"]["readme"]
    if not readme.exists():
        raise Exception(
            f"Missing README: {readme}"
        )

    install_script = command_dir / manifest["install"]["script"]
    if not install_script.exists():
        raise Exception(
            f"Missing install script: {install_script}"
        )
