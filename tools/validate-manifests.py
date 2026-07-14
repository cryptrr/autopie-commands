from pathlib import Path
import re

from manifest_io import find_manifest_files, load_manifest

ID_RE = re.compile(r"^[a-z][a-z0-9_-]*\.[a-z][a-z0-9_-]*$")

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
