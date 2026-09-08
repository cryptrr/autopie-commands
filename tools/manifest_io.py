from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "PyYAML is required for manifest tooling. Run `uv sync`, then execute "
        "tools with `uv run python`."
    ) from exc


MANIFEST_NAMES = ("manifest.yaml", "manifest.yml")


def find_manifest_files(commands_dir: Path) -> list[Path]:
    manifests: list[Path] = []
    for manifest_name in MANIFEST_NAMES:
        manifests.extend(commands_dir.glob(f"*/*/{manifest_name}"))
    return sorted(manifests)


def load_manifest(manifest_file: Path) -> dict[str, Any]:
    with manifest_file.open("r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    if not isinstance(manifest, dict):
        raise ValueError(f"{manifest_file}: expected a mapping")
    return manifest
