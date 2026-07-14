from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any


MANIFEST_NAMES = ("manifest.yaml", "manifest.yml")
NUMBER_RE = re.compile(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?")


def find_manifest_files(commands_dir: Path) -> list[Path]:
    manifests: list[Path] = []
    for manifest_name in MANIFEST_NAMES:
        manifests.extend(commands_dir.glob(f"*/*/{manifest_name}"))
    return sorted(manifests)


def load_manifest(manifest_file: Path) -> dict[str, Any]:
    with manifest_file.open("r", encoding="utf-8") as f:
        text = f.read()

    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        return _SimpleYamlParser(text, manifest_file).parse()

    manifest = yaml.safe_load(text)
    if not isinstance(manifest, dict):
        raise ValueError(f"{manifest_file}: expected a mapping")
    return manifest


class _SimpleYamlParser:
    def __init__(self, text: str, source: Path):
        self.source = source
        self.lines = [
            (indent, content)
            for indent, content in (
                self._normalize_line(line)
                for line in text.splitlines()
            )
            if content
        ]
        self.index = 0

    def parse(self) -> dict[str, Any]:
        parsed = self._parse_block(0)
        if self.index != len(self.lines):
            raise ValueError(f"{self.source}: could not parse full manifest")
        if not isinstance(parsed, dict):
            raise ValueError(f"{self.source}: expected a mapping")
        return parsed

    def _parse_block(self, indent: int) -> Any:
        if self.index >= len(self.lines):
            return {}

        current_indent, content = self.lines[self.index]
        if current_indent < indent:
            return {}
        if current_indent != indent:
            raise ValueError(
                f"{self.source}: unexpected indentation at line {self.index + 1}"
            )

        if content.startswith("- "):
            return self._parse_list(indent)
        return self._parse_map(indent)

    def _parse_map(self, indent: int) -> dict[str, Any]:
        result: dict[str, Any] = {}

        while self.index < len(self.lines):
            current_indent, content = self.lines[self.index]
            if current_indent < indent:
                break
            if current_indent != indent or content.startswith("- "):
                break

            key, raw_value = self._split_key_value(content)
            self.index += 1

            if raw_value == "":
                if self.index < len(self.lines) and self.lines[self.index][0] > indent:
                    result[key] = self._parse_block(self.lines[self.index][0])
                else:
                    result[key] = {}
            else:
                result[key] = self._parse_scalar(raw_value)

        return result

    def _parse_list(self, indent: int) -> list[Any]:
        result: list[Any] = []

        while self.index < len(self.lines):
            current_indent, content = self.lines[self.index]
            if current_indent < indent:
                break
            if current_indent != indent or not content.startswith("- "):
                break

            raw_value = content[2:].strip()
            self.index += 1

            if raw_value == "":
                if self.index < len(self.lines) and self.lines[self.index][0] > indent:
                    result.append(self._parse_block(self.lines[self.index][0]))
                else:
                    result.append(None)
            elif ": " in raw_value or raw_value.endswith(":"):
                key, item_value = self._split_key_value(raw_value)
                item: dict[str, Any] = {}
                item[key] = (
                    self._parse_scalar(item_value)
                    if item_value
                    else self._parse_block(self.lines[self.index][0])
                )
                while self.index < len(self.lines) and self.lines[self.index][0] > indent:
                    nested = self._parse_block(self.lines[self.index][0])
                    if not isinstance(nested, dict):
                        raise ValueError(f"{self.source}: expected mapping in list item")
                    item.update(nested)
                result.append(item)
            else:
                result.append(self._parse_scalar(raw_value))

        return result

    def _normalize_line(self, line: str) -> tuple[int, str]:
        line = line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            return 0, ""

        indent = len(line) - len(line.lstrip(" "))
        if indent % 2 != 0:
            raise ValueError(f"{self.source}: indentation must use multiples of two")
        return indent, line.strip()

    def _split_key_value(self, content: str) -> tuple[str, str]:
        if ":" not in content:
            raise ValueError(f"{self.source}: expected key/value pair: {content}")
        key, value = content.split(":", 1)
        return self._parse_key(key), value.strip()

    def _parse_key(self, key: str) -> str:
        key = key.strip()
        if not key:
            raise ValueError(f"{self.source}: empty key")
        if key[0] in ("'", '"'):
            return str(ast.literal_eval(key))
        return key

    def _parse_scalar(self, value: str) -> Any:
        if value in ("[]", "{}"):
            return json.loads(value)
        if value in ("true", "false", "null"):
            return json.loads(value)
        if value[0:1] in ("'", '"'):
            return ast.literal_eval(value)
        if value[0:1] in ("[", "{"):
            return json.loads(value)
        if NUMBER_RE.fullmatch(value):
            return float(value) if "." in value else int(value)
        return value
