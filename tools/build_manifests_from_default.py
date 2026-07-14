#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


DEFAULT_FILE = Path("default.json")
COMMANDS_DIR = Path("commands/autopie")
NAMESPACE = "autopie"
SCHEMA_VERSION = "2026.6.1"
VERSION = "1.0.0"
INSTALLER_VERSION = 1
MAINTAINERS = ["cryptrr"]
SELECTABLE_TYPES = {"SELECTABLE", "MULTI_SELECTABLE"}

EXISTING_TARGETS = {
    "Extract Audio from File": "extract-audio",
    "Change Volume on Mac - AutoFetch": "change-volume-on-mac-autofetch",
    "wCurl Download": "wcurl",
}

PACKAGE_MAP = {
    "7z": ["p7zip"],
    "am": ["yt-dlp"],
    "exiftool": ["exiftool"],
    "ffmpeg": ["ffmpeg"],
    "gallery-dl": ["gallery-dl"],
    "httpx": ["httpx"],
    "magick": ["imagemagick"],
    "mediainfo": ["mediainfo"],
    "openssh": ["openssh", "sshpass"],
    "rsync": ["rsync"],
    "wcurl": ["wcurl"],
    "yt-dlp": ["yt-dlp"],
}

COMMAND_PACKAGE_HINTS = (
    ("#@PYTHON", ["python"]),
    ("mediainfo", ["mediainfo"]),
    ("sha256sum", ["coreutils"]),
    ("touch ", ["coreutils"]),
)


def json_scalar(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True)


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "command"


def packages_for(block: dict[str, Any]) -> list[str]:
    command_slug = block.get("exec", "")
    command = block.get("command", "")

    packages = PACKAGE_MAP.get(command_slug)
    if packages is not None:
        return packages

    for marker, hinted_packages in COMMAND_PACKAGE_HINTS:
        if marker in command:
            return hinted_packages

    return [command_slug] if command_slug else ["coreutils"]


def packages_for_command(command: dict[str, Any]) -> list[str]:
    blocks = command.get("steps", []) if command.get("multiStage") else [command]
    packages: list[str] = []

    for block in blocks:
        for package in packages_for(block):
            if package and package not in packages:
                packages.append(package)

    return packages or ["coreutils"]


def emit_extra(lines: list[str], indent: int, extra: dict[str, Any]) -> None:
    prefix = " " * indent
    child = " " * (indent + 2)
    extra_type = extra.get("type")

    ordered_keys = (
        "id",
        "name",
        "type",
        "default",
        "description",
        "required",
        "flags",
    )

    first_key = True
    for key in ordered_keys:
        if key not in extra:
            continue

        key_prefix = prefix + "- " if first_key else child
        lines.append(f"{key_prefix}{key}: {json_scalar(extra[key])}")
        first_key = False

    if extra_type == "BOOLEAN":
        default_boolean = extra.get("defaultBoolean", extra.get("default", False))
        key_prefix = prefix + "- " if first_key else child
        lines.append(f"{key_prefix}defaultBoolean: {json_scalar(bool(default_boolean))}")
        first_key = False

    if extra_type in SELECTABLE_TYPES and "selectableOptions" in extra:
        key_prefix = prefix + "- " if first_key else child
        lines.append(
            f"{key_prefix}selectableOptions: "
            f"{json_scalar(extra['selectableOptions'])}"
        )


def emit_extras(lines: list[str], indent: int, extras: list[dict[str, Any]]) -> None:
    if not extras:
        return

    lines.append(f"{' ' * indent}extras:")
    for extra in extras:
        emit_extra(lines, indent + 2, extra)


def emit_runtime_block(
    lines: list[str],
    indent: int,
    block: dict[str, Any],
    include_command_slug: bool,
) -> None:
    prefix = " " * indent
    lines.append(f"{prefix}path: {json_scalar(block.get('path', ''))}")

    if include_command_slug:
        lines.append(f"{prefix}commandSlug: {json_scalar(block.get('exec', ''))}")

    lines.append(f"{prefix}command: {json_scalar(block.get('command', ''))}")

    if "flags" in block:
        lines.append(f"{prefix}flags: {json_scalar(block['flags'])}")

    if "deleteSourceFile" in block:
        lines.append(f"{prefix}deleteSourceFile: {json_scalar(block['deleteSourceFile'])}")

    emit_extras(lines, indent, block.get("extras", []))


def emit_runtime_step(lines: list[str], indent: int, block: dict[str, Any]) -> None:
    prefix = " " * indent
    child = " " * (indent + 2)

    lines.append(f"{prefix}- path: {json_scalar(block.get('path', ''))}")
    lines.append(f"{child}commandSlug: {json_scalar(block.get('exec', ''))}")
    lines.append(f"{child}command: {json_scalar(block.get('command', ''))}")

    if "flags" in block:
        lines.append(f"{child}flags: {json_scalar(block['flags'])}")

    if "deleteSourceFile" in block:
        lines.append(f"{child}deleteSourceFile: {json_scalar(block['deleteSourceFile'])}")

    emit_extras(lines, indent + 2, block.get("extras", []))


def manifest_text(name: str, slug: str, command: dict[str, Any]) -> str:
    packages = packages_for_command(command)
    primary_package = packages[0]
    extra_packages = packages[1:]
    top_level_command_slug = (
        slug if command.get("multiStage") else command.get("exec", "")
    )

    lines = [
        f"schemaVersion: {json_scalar(SCHEMA_VERSION)}",
        f"version: {json_scalar(VERSION)}",
        f"id: {json_scalar(f'{NAMESPACE}.{slug}')}",
        f"namespace: {json_scalar(NAMESPACE)}",
        f"name: {json_scalar(name)}",
        f"commandSlug: {json_scalar(top_level_command_slug)}",
        f"summary: {json_scalar(f'AutoPie command for {name}')}",
        'type: "PACKAGE"',
        f"tags: {json_scalar([primary_package])}",
        "runtime:",
    ]

    if command.get("multiStage"):
        lines.append("  multiStage: true")
        lines.append("  steps:")
        for step in command.get("steps", []):
            emit_runtime_step(lines, 4, step)
    else:
        emit_runtime_block(lines, 2, command, include_command_slug=False)

    lines.extend(
        [
            "install:",
            f"  primaryPackage: {json_scalar(primary_package)}",
            f"  extraPackages: {json_scalar(extra_packages)}",
            f"  installerVersion: {INSTALLER_VERSION}",
            '  script: "install.sh"',
            '  sha256: "..."',
            "uninstall:",
            '  script: "uninstall.sh"',
            "docs:",
            '  readme: "README.md"',
            '  changelog: "CHANGELOG.md"',
            "compatibility:",
            '  autopieMinVersion: "0.x"',
            '  autopieMaxVersion: "0.x"',
            "status: \"stable\"",
            f"maintainers: {json_scalar(MAINTAINERS)}",
            "",
        ]
    )

    return "\n".join(lines)


def install_script_text(packages: list[str]) -> str:
    return (
        "#!/usr/bin/env sh\n"
        "set -eu\n"
        "\n"
        f"pkg install -y {' '.join(packages)}\n"
    )


def readme_text(name: str, command: dict[str, Any]) -> str:
    if command.get("multiStage"):
        details = "Multistage AutoPie command imported from `default.json`."
    else:
        details = "AutoPie command imported from `default.json`."

    return f"# {name}\n\n{details}\n"


def changelog_text() -> str:
    return "# Changelog\n\n## 1.0.0\n\n- Initial manifest import from `default.json`.\n"


def uninstall_script_text() -> str:
    return "#!/usr/bin/env sh\nset -eu\n\n# No uninstall actions are required.\n"


def main() -> None:
    with DEFAULT_FILE.open("r", encoding="utf-8") as f:
        commands: dict[str, dict[str, Any]] = json.load(f)

    used_slugs: set[str] = set()

    for name, command in commands.items():
        base_slug = EXISTING_TARGETS.get(name, slugify(name))
        slug = base_slug
        counter = 2
        while slug in used_slugs:
            slug = f"{base_slug}-{counter}"
            counter += 1

        used_slugs.add(slug)
        command_dir = COMMANDS_DIR / slug
        command_dir.mkdir(parents=True, exist_ok=True)

        packages = packages_for_command(command)
        (command_dir / "manifest.yaml").write_text(
            manifest_text(name, slug, command),
            encoding="utf-8",
        )
        (command_dir / "README.md").write_text(
            readme_text(name, command),
            encoding="utf-8",
        )
        (command_dir / "CHANGELOG.md").write_text(
            changelog_text(),
            encoding="utf-8",
        )
        (command_dir / "install.sh").write_text(
            install_script_text(packages),
            encoding="utf-8",
        )
        (command_dir / "uninstall.sh").write_text(
            uninstall_script_text(),
            encoding="utf-8",
        )

    print(f"Generated {len(commands)} command manifest(s) in {COMMANDS_DIR}.")


if __name__ == "__main__":
    main()
