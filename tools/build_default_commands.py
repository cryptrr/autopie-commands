#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from manifest_io import find_manifest_files, load_manifest


COMMANDS_DIR = Path("commands")
OUTPUT_FILE = Path("default-commands.json")
SELECTABLE_TYPES = {"SELECTABLE", "MULTI_SELECTABLE"}


def parse_default_boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def convert_extra(extra: dict[str, Any]) -> dict[str, Any]:
    extra_type = extra.get("type")
    converted: dict[str, Any] = {}

    for key in (
        "default",
        "description",
        "id",
        "name",
        "required",
        "flags",
        "type",
    ):
        if key in extra:
            converted[key] = extra[key]

    if extra_type in SELECTABLE_TYPES and "selectableOptions" in extra:
        converted["selectableOptions"] = extra["selectableOptions"]

    if extra_type == "BOOLEAN":
        converted["defaultBoolean"] = parse_default_boolean(
            extra.get("defaultBoolean", extra.get("default", False))
        )

    return converted


def build_command(block: dict[str, Any]) -> str:
    command = block.get("command", "")
    args = block.get("args", [])

    if not args:
        return command

    return " ".join([command, *(str(arg) for arg in args)]).strip()


def convert_runtime_block(block: dict[str, Any], fallback_exec: str | None) -> dict[str, Any]:
    converted: dict[str, Any] = {
        "path": block.get("path", ""),
        "exec": block.get("commandSlug", block.get("exec", fallback_exec or "")),
        "command": build_command(block),
    }

    if "flags" in block:
        converted["flags"] = block["flags"]

    if "deleteSourceFile" in block:
        converted["deleteSourceFile"] = block["deleteSourceFile"]

    extras = block.get("extras")
    if extras:
        converted["extras"] = [convert_extra(extra) for extra in extras]

    return converted


def convert_manifest(manifest: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    name = manifest["name"]
    command_id = manifest["id"]
    runtime = manifest.get("runtime", {})
    fallback_exec = manifest.get("commandSlug")

    if runtime.get("multiStage"):
        converted: dict[str, Any] = {
            "id": command_id,
            "multiStage": True,
            "steps": [
                convert_runtime_block(step, fallback_exec)
                for step in runtime.get("steps", [])
            ],
        }
        return name, converted

    converted = convert_runtime_block(runtime, fallback_exec)
    converted["id"] = command_id
    return name, converted


def build_default_commands() -> dict[str, Any]:
    commands: dict[str, Any] = {}

    for manifest_file in find_manifest_files(COMMANDS_DIR):
        manifest = load_manifest(manifest_file)
        name, command = convert_manifest(manifest)
        commands[name] = command

    return commands


def main() -> None:
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            build_default_commands(),
            f,
            indent=2,
            ensure_ascii=False,
        )
        f.write("\n")

    print(f"Generated {OUTPUT_FILE}.")


if __name__ == "__main__":
    main()
