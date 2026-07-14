#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from manifest_io import find_manifest_files, load_manifest


COMMANDS_DIR = Path("commands")


def scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def table_cell(value: Any) -> str:
    text = scalar(value).replace("\n", "<br>")
    return text.replace("|", "\\|") or "-"


def command_text(block: dict[str, Any]) -> str:
    command = block.get("command", "")
    args = block.get("args", [])
    if args:
        return " ".join([command, *(str(arg) for arg in args)]).strip()
    return command


def option_summary(options: Any) -> str:
    if isinstance(options, dict):
        values = [
            label if label == value else f"{label}={value}"
            for label, value in options.items()
        ]
    elif isinstance(options, list):
        values = [str(option) for option in options]
    else:
        return "-"

    return ", ".join(values[:8]) + (", ..." if len(values) > 8 else "")


def extra_rows(block: dict[str, Any], step_name: str | None = None) -> list[str]:
    rows: list[str] = []
    for extra in block.get("extras", []):
        fields = []
        if step_name is not None:
            fields.append(step_name)
        fields.extend(
            [
                extra.get("name", ""),
                extra.get("type", ""),
                "yes" if extra.get("required") else "no",
                extra.get("default", extra.get("defaultBoolean", "")),
                ", ".join(extra.get("flags", [])),
                option_summary(extra.get("selectableOptions")),
                extra.get("description", ""),
            ]
        )
        rows.append("| " + " | ".join(table_cell(field) for field in fields) + " |")
    return rows


def command_block_markdown(
    block: dict[str, Any],
    fallback_command_slug: str = "",
) -> list[str]:
    path = block.get("path", "")
    command_slug = block.get("commandSlug", block.get("exec", fallback_command_slug))

    lines = [
        f"- Path: `{path or 'default'}`",
        f"- Command slug: `{command_slug}`",
        "",
        "```sh",
        command_text(block),
        "```",
    ]

    if block.get("flags"):
        lines.extend(["", f"- Flags: `{', '.join(block['flags'])}`"])

    return lines


def build_readme(manifest: dict[str, Any]) -> str:
    name = manifest["name"]
    summary = manifest.get("summary", "")
    runtime = manifest.get("runtime", {})
    lines = [f"# {name}", ""]

    if summary:
        lines.extend([summary, ""])

    if runtime.get("multiStage"):
        steps = runtime.get("steps", [])
        lines.extend(["## Steps", ""])
        for index, step in enumerate(steps, 1):
            lines.extend([f"### Step {index}", ""])
            lines.extend(command_block_markdown(step, manifest.get("commandSlug", "")))
            lines.append("")

        rows: list[str] = []
        for index, step in enumerate(steps, 1):
            rows.extend(extra_rows(step, f"Step {index}"))

        lines.extend(["## Extras", ""])
        if rows:
            lines.extend(
                [
                    "| Step | Name | Type | Required | Default | Flags | Options | Details |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- |",
                    *rows,
                ]
            )
        else:
            lines.append("No extras.")
    else:
        lines.extend(["## Command", ""])
        lines.extend(command_block_markdown(runtime, manifest.get("commandSlug", "")))
        lines.extend(["", "## Extras", ""])

        rows = extra_rows(runtime)
        if rows:
            lines.extend(
                [
                    "| Name | Type | Required | Default | Flags | Options | Details |",
                    "| --- | --- | --- | --- | --- | --- | --- |",
                    *rows,
                ]
            )
        else:
            lines.append("No extras.")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    manifests = find_manifest_files(COMMANDS_DIR)
    for manifest_file in manifests:
        manifest = load_manifest(manifest_file)
        readme_file = manifest_file.parent / manifest["docs"]["readme"]
        readme_file.write_text(build_readme(manifest), encoding="utf-8")

    print(f"Updated {len(manifests)} README file(s).")


if __name__ == "__main__":
    main()
