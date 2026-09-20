# AutoPie Commands

This repository is the community command catalog for AutoPie. Each command is a
self-contained YAML recipe with documentation, a changelog, and a compatibility
installer for older AutoPie clients.

This guide is the authoring reference for humans and coding agents. Treat the
current manifests and `tools/validate-manifests.py` as the source of truth. The
JSON files are generated artifacts or legacy import data; author new recipes as
YAML.

## Contents

- [Repository layout](#repository-layout)
- [Hosted repository](#hosted-repository)
- [Quick start](#quick-start)
- [Complete single-stage example](#complete-single-stage-example)
- [Manifest reference](#manifest-reference)
- [Runtime](#runtime)
- [Extras](#extras-user-configurable-inputs)
- [Multi-stage commands](#multi-stage-commands)
- [Dependencies and compatibility installation](#dependencies-and-compatibility-installation)
- [Documentation and client compatibility](#documentation-and-client-compatibility)
- [YAML and command conventions](#yaml-and-command-conventions)
- [Repository tooling](#repository-tooling)
- [Author checklist](#author-checklist)
- [Contributing](#contributing)

## Repository layout

```text
commands/
  <namespace>/
    <command-slug>/
      manifest.yaml
      README.md
      CHANGELOG.md
      install.sh
catalog.json
default-commands.json
schema/
tools/
```

For example, `autopie.remove-audio` lives in
`commands/autopie/remove-audio/`.

## Hosted repository

The `main` and `dev` channels are published to GitHub Pages with the repository
layout preserved beneath the channel name:

```text
https://cryptrr.github.io/autopie-commands/main/catalog.json
https://cryptrr.github.io/autopie-commands/main/commands/<namespace>/<command-slug>/
https://cryptrr.github.io/autopie-commands/dev/catalog.json
https://cryptrr.github.io/autopie-commands/dev/commands/<namespace>/<command-slug>/
```

Every deployment reads the current head of both branches and publishes both
channels together. The Pages artifact contains `catalog.json` and `commands/`
from each branch without changing their paths or contents.

The path and identity fields must agree:

- `namespace` equals the namespace directory.
- The command slug equals the command directory name.
- `id` is `<namespace>.<command-slug>`.
- Each side of the ID starts with a lowercase letter and otherwise uses
  lowercase letters, numbers, `_`, or `-`.

## Quick start

1. Copy a command with a similar runtime type.
2. Rename its directory and update its identity and metadata.
3. Write the runtime command and user-configurable extras.
4. Declare dependencies and provide the matching `install.sh` fallback.
5. Update the changelog; the command README is generated from the manifest.
6. Validate and regenerate repository artifacts.
7. Review the complete diff before opening a pull request.

Useful examples:

- Simple shared-file command:
  [`remove-audio`](commands/autopie/remove-audio/manifest.yaml)
- Both `pkg` and `pip` dependencies:
  [`yt-dlp-download`](commands/autopie/yt-dlp-download/manifest.yaml)
- Multi-stage command:
  [`smart-ytdlp-downloader`](commands/autopie/smart-ytdlp-downloader/manifest.yaml)
- Conditional inputs:
  [`compress-7zip`](commands/autopie/compress-7zip/manifest.yaml)
- Scheduled monitor:
  [`health-check-widget`](commands/autopie/health-check-widget/manifest.yaml)
- Embedded Python:
  [`epub-to-text`](commands/autopie/epub-to-text/manifest.yaml)

## Complete single-stage example

```yaml
schemaVersion: "2026.6.1"
addedAt: "2026-09-19T08:00:00Z"
updatedAt: "2026-09-19T08:00:00Z"
version: "1.0.0"
id: "autopie.grayscale-video"
namespace: "autopie"
name: "Grayscale Video"
commandSlug: "ffmpeg"
summary: "Create a grayscale copy of a shared video."
kind: "APP"
tags: ["ffmpeg", "video"]
runtime:
  type: "SHARE"
  path: ""
  flags: ["--show-loading-screen-small"]
  command: |-
    set -eu

    output="${INPUT_FILE%.*}-gray-${RAND}.mp4"
    ffmpeg -i "$INPUT_FILE" -vf format=gray -crf "$CRF" "$output"
    printf 'Created: %s\n' "$output"
  extras:
    - id: "crf"
      name: "CRF"
      type: "SLIDER"
      default: "0,23,51"
      description: "Video quality. Lower values retain more quality."
      required: true
      flags: ["--int"]
install:
  dependencies:
    pkg: ["ffmpeg"]
  primaryPackage: "ffmpeg"
  extraPackages: []
  installerVersion: 1
  script: "install.sh"
  sha256: "..."
docs:
  readme: "README.md"
  changelog: "CHANGELOG.md"
compatibility:
  autopieMinVersion: "0.x"
  autopieMaxVersion: "0.x"
status: "stable"
maintainers: ["your-name"]
```

Matching `install.sh`:

```sh
#!/usr/bin/env sh
set -eu

pkg install -y ffmpeg
```

Do not add `uninstall.sh`. Dependencies are shared by commands in the same
Termux environment and must not be removed when one command is removed.

## Manifest reference

Every current manifest uses these top-level sections in this order:

```text
schemaVersion
addedAt
updatedAt
version
id
namespace
name
commandSlug
summary
kind
tags
runtime
install
docs
compatibility
status
maintainers
```

The order is not required by YAML, but keeping it makes recipes predictable to
review and edit.

### Identity and release metadata

| Field | Meaning |
| --- | --- |
| `schemaVersion` | Manifest format version. Use the version used by current recipes, presently `2026.6.1`. |
| `addedAt` | UTC creation timestamp in `YYYY-MM-DDTHH:MM:SSZ` format. Never change it after the command is added. |
| `updatedAt` | UTC timestamp of the latest recipe release. It cannot be earlier than `addedAt`. |
| `version` | Quoted semantic version such as `"1.0.0"`. |
| `id` | Unique `<namespace>.<command-slug>` identifier matching the directory path. |
| `namespace` | Publisher/collection namespace, normally `autopie` here. |
| `name` | Human-readable name shown in AutoPie. |
| `commandSlug` | Primary executable identifier, such as `ffmpeg`, `magick`, or `yt-dlp`. Use `""` for a script without one primary executable. |
| `summary` | One sentence describing the input, action, and result. |
| `kind` | `APP` for user-run commands or `MONITOR` for scheduled monitors. |
| `tags` | Short lowercase discovery terms. Include the main tool and domain. |
| `status` | Release state. Current catalog recipes use `stable`. |
| `maintainers` | Repository usernames responsible for the recipe. |

For a new recipe, `addedAt` and `updatedAt` should match. Preserve `addedAt` and
advance `updatedAt` for later releases.

## Runtime

### Runtime types

`runtime.type` determines how AutoPie invokes a recipe.

| Type | Use it for | Typical input |
| --- | --- | --- |
| `SHARE` | Android share-sheet actions on files, folders, text, or URLs. | `INPUT`, `INPUT_FILE`, `INPUT_FILES`, `INPUT_FILES_ARR`, or `INPUT_URL` |
| `MANUAL` | Commands launched directly and configured through extras. | Extra variables |
| `CRON` | Scheduled commands, normally paired with `kind: "MONITOR"`. | Saved configuration extras |

A single-stage runtime looks like this:

```yaml
runtime:
  type: "SHARE"
  path: "Download"
  flags: ["--show-loading-screen-small"]
  command: |-
    # command body
  extras:
    # optional input definitions
```

### Working directory

`runtime.path` is the command's working directory. An empty string uses
AutoPie's default storage location. A relative path such as `"Download"` selects
a directory under shared storage. Existing recipes also use absolute Android
storage paths when required.

Always quote paths in command code. Shared names can contain spaces, Unicode,
quotes, and shell metacharacters.

### Command body

`runtime.command` is the program or script AutoPie executes. Use a YAML block
scalar for anything longer than a simple line:

```yaml
command: |-
  set -euo pipefail
  printf 'Input: %s\n' "$INPUT"
```

Shell is the normal command language. Put `#@PYTHON` first when AutoPie should
execute the body as Python:

```yaml
command: |-
  #@PYTHON
  import os

  print(os.environ["INPUT_FILE"])
```

Existing recipes use `#@OPEN_LOGS` when the client should open the command log.
Keep interpreter/client directives at the beginning of the command.

Current runtime flags are:

- `--show-loading-screen-small`: compact running/loading UI.
- `--show-loading-screen`: full running/loading UI.

Only use flags supported by the minimum target client.

### Scheduled commands

CRON recipes add `cronInterval`:

```yaml
kind: "MONITOR"
runtime:
  type: "CRON"
  cronInterval: "15m"
  path: ""
  command: |-
    # scheduled health check
```

Use duration syntax accepted by AutoPie. Current monitors use `15m`.

### Runtime environment

AutoPie exposes built-in variables according to the invocation:

- `INPUT`: generic shared input, including text or a file/folder path.
- `INPUT_FILE`: one shared file.
- `INPUT_FILES` and `INPUT_FILES_ARR`: multiple shared files. Prefer the array
  form for shell iteration so spaces remain intact.
- `INPUT_URL`: a shared URL.
- `RAND`: a collision-resistant suffix for output names.
- Standard environment values such as `HOME`.

Extras become environment variables using their `name`; an extra named
`QUALITY` is available as `$QUALITY` or `${QUALITY}`.

Validate required input in the command and fail with an actionable message.
Avoid overwriting source files unless destructive behavior is the command's
explicit purpose.

Commands may print normal progress and results. Existing recipes also emit
structured AutoPie directives:

```sh
printf '#@AUTOPIE {"type":"output","value":"%s"}\n' "$OUTPUT"
```

Python commands should use a JSON encoder:

```python
print("#@AUTOPIE " + json.dumps({
    "type": "notification",
    "title": "Check complete",
    "body": "The service is healthy",
}))
```

Use a JSON encoder whenever values can contain quotes or newlines.

## Extras: user-configurable inputs

`extras` defines form controls injected into the command environment. Extras can
belong to a single-stage `runtime` or an individual multi-stage step.

```yaml
extras:
  - id: "output_format"
    name: "OUTPUT_FORMAT"
    type: "SELECTABLE"
    default: "mp4"
    description: "Output container."
    required: true
    selectableOptions:
      "MP4 — widest compatibility": "mp4"
      "Matroska — flexible container": "mkv"
```

Do not casually change an existing extra's `id`; clients may associate saved
configuration with it. Prefer descriptive string IDs and uppercase shell-safe
names.

### Extra fields

| Field | Meaning |
| --- | --- |
| `id` | Stable identifier used by AutoPie. |
| `name` | Environment variable exposed to the command. |
| `type` | UI/input type. |
| `default` | Default string value for most types. |
| `defaultBoolean` | Boolean default for `BOOLEAN` and `FLAG`. |
| `description` | Help text explaining meaning, constraints, and risks. |
| `required` | Whether the user must provide a value. |
| `flags` | Additional client-side field behavior. |
| `selectableOptions` | List or label-to-value mapping. |
| `visibleWhen` | Condition controlling field visibility. |

### Extra types

Current manifests and conversion tooling recognize:

- `STRING`: free-form text.
- `BOOLEAN`: boolean control using `defaultBoolean`.
- `FLAG`: boolean-style feature toggle.
- `SLIDER`: numeric range. Current recipes encode `min,current,max` in
  `default`, for example `"0,50,100"`.
- `SELECTABLE`: single-choice list or label-to-value mapping.
- `SELECTABLE_FLAT`: compact/flat selectable presentation.
- `MULTI_SELECTABLE`: multiple-choice selectable data supported by conversion
  tooling, though no current recipe uses it.

Use a list when labels and values are identical:

```yaml
selectableOptions: ["720x", "1080x", "2160x"]
```

Use a mapping when display labels differ from command values:

```yaml
selectableOptions:
  "Best quality": "best"
  "Audio only": "audio"
```

### Extra flags

| Flag | Intended behavior |
| --- | --- |
| `--internal-config` | Treat the value as saved command configuration. |
| `--secret` | Treat the value as sensitive. |
| `--password` | Present a password-oriented input. |
| `--large` | Present a larger text input. |
| `--int` | Parse or present the value as an integer. |
| `--folder-picker` | Let the user select a folder. |
| `--realtime` | Apply or expose changes in real time. |

Only use established flags whose client behavior fits the input. Never print a
secret or place it in an output filename.

### Conditional inputs

Show a field only when another extra has a value:

```yaml
visibleWhen:
  extraId: "enable_encryption"
  equals: true
```

Combine conditions with `all`:

```yaml
visibleWhen:
  all:
    - extraId: "enable_encryption"
      equals: true
    - extraId: "format"
      equals: "7z"
```

Conditions reference the other extra's `id`, not its environment name.

## Multi-stage commands

Use multiple stages when an earlier action must inspect or prepare data before
AutoPie can present later choices.

```yaml
runtime:
  multiStage: true
  type: "SHARE"
  flags: ["--show-loading-screen-small"]
  steps:
    - id: "inspect"
      path: "Download"
      command: |-
        export FORMAT_OPTIONS="MP4=mp4,Matroska=mkv"
        export FORMAT_DEFAULT="mp4"
      extras:
        - id: "source_url"
          name: "SOURCE_URL"
          type: "STRING"
          default: "$$INPUT_URL"
          description: "URL to inspect."
          required: true

    - id: "run"
      path: "Download"
      commandSlug: "example-tool"
      command: |-
        example-tool --format "$FORMAT" "$SOURCE_URL"
      extras:
        - id: "format"
          name: "FORMAT"
          type: "SELECTABLE"
          default: "$$FORMAT_DEFAULT"
          description: "Format discovered by the previous step."
          selectableOptions:
            "Available formats": "$$FORMAT_OPTIONS"
```

Rules:

- Put `type` and runtime-level flags on `runtime`.
- Replace runtime-level `command`, `path`, and `extras` with `steps`.
- Give meaningful steps stable IDs.
- Each step can define `path`, `commandSlug`, `command`, and `extras`.
- Export values required by later steps.
- `$$VARIABLE` references a value resolved by AutoPie, often built-in input or
  an earlier exported value.
- Current dynamic selectables encode options as comma-separated `label=value`
  pairs. Remove commas, equals signs, and newlines from generated labels.

Prefer one stage unless the staged UI materially improves the workflow.

## Dependencies and compatibility installation

`install.dependencies` is the modern dependency source of truth. Supported
package managers are `pkg` and `pip`:

```yaml
install:
  dependencies:
    pkg: ["ffmpeg", "python"]
    pip: ["yt-dlp"]
  primaryPackage: "yt-dlp"
  extraPackages: ["ffmpeg", "python"]
  installerVersion: 1
  script: "install.sh"
  sha256: "..."
```

Rules:

- Declare unversioned package names. Commands share one Termux environment, so a
  recipe cannot safely own a separate global package version.
- Omit `pkg` or `pip` when it has no dependencies; do not write empty arrays.
- Omit `dependencies` entirely when there are no dependencies.
- Do not install packages from the runtime command.
- Do not add dependency removal or `uninstall.sh`.

`primaryPackage` and `extraPackages` are compatibility/discovery metadata.
Choose the principal tool as `primaryPackage` and list other direct packages in
`extraPackages`. Modern clients use `dependencies` operationally.

`installerVersion` identifies compatibility installer behavior. Follow a
comparable recipe. `sha256` is optional in the current corpus; most recipes use
the repository's `"..."` placeholder until release tooling produces integrity
metadata.

### Required `install.sh`

Every command currently needs `install.script: "install.sh"` and that file.
Older AutoPie clients execute the script instead of reading dependencies.

The script must match the declarative dependencies:

```sh
#!/usr/bin/env sh
set -eu

pip install yt-dlp
pkg install -y ffmpeg
```

Keep it deterministic and non-interactive:

- Use `pkg install -y ...` for Termux packages.
- Use `pip install ...` for Python packages.
- Do not add `-U` or force upgrades.
- Do not perform unrelated setup or destructive cleanup.
- With no dependencies, use a harmless fallback such as
  `echo "No dependencies to install"`.

Whenever dependencies change, update the manifest and script together.

## Documentation and client compatibility

```yaml
docs:
  readme: "README.md"
  changelog: "CHANGELOG.md"
compatibility:
  autopieMinVersion: "0.x"
  autopieMaxVersion: "0.x"
```

- The command README is its generated runtime and extras reference.
- The changelog records user-visible changes by recipe version.
- Compatibility fields define the supported client range. Change them only when
  client feature requirements are known.

`tools/build_readmes.py` regenerates every command README. Do not keep unique
hand-written content there unless the generator is changed to preserve it.

## YAML and command conventions

- Quote schema versions, recipe versions, IDs, timestamps, and values YAML might
  otherwise coerce.
- Use `|-` for multiline shell or Python.
- Indent YAML with spaces, never tabs.
- Quote shell variables unless splitting is intentional.
- Use `set -eu` for portable shell, or `set -euo pipefail` for code deliberately
  targeting a shell with `pipefail` and arrays.
- Validate user values before embedding them in remote commands, filenames,
  regexes, or JSON.
- Use unique outputs, commonly with `$RAND`, and avoid overwriting inputs.
- Put persistent state under an AutoPie-specific location such as
  `$HOME/.cache/autopie/<command>`.
- Add timeouts to network operations and report actionable errors.
- Check required external commands when failure would otherwise be unclear.
- Never log secrets.

## Repository tooling

Tools require Python 3.11 or newer and PyYAML. Install
[`uv`](https://docs.astral.sh/uv/), then prepare the environment:

```sh
uv sync
```

Validate manifests:

```sh
uv run python tools/validate-manifests.py
```

The validator checks:

- IDs match namespace and directory slug and remain unique.
- Timestamps use UTC format and are chronologically valid.
- Referenced command READMEs exist.
- Dependency mappings use supported managers and non-empty arrays.
- Every manifest references an existing compatibility installer.

Regenerate artifacts:

```sh
uv run python tools/build_default_commands.py
uv run python tools/build_readmes.py
uv run python tools/build_catalog.py
```

Outputs:

- `default-commands.json`: client-compatible command representation.
- Command `README.md` files: rendered runtime and extras references.
- `catalog.json`: searchable catalog metadata.

`build_catalog.py` changes `generatedAt`, so a catalog diff is expected. Review
all generated changes and validate again afterward.

For a manually created command, the date tool can add missing timestamps. It
preserves existing timestamps unless `--force` is used:

```sh
uv run python tools/backfill_catalog_dates.py
```

`tools/build_manifests_from_default.py` is a bulk legacy-import utility that can
rewrite command directories. It is not part of normal recipe authoring.

## Author checklist

Before submitting, verify:

- The directory is `commands/<namespace>/<slug>/`.
- `id`, `namespace`, and the path agree.
- Summary, tags, kind, and runtime type describe the behavior accurately.
- The command consumes the correct built-in input variable.
- Every extra has a stable ID, shell-safe name, suitable type, and useful help.
- Secrets use suitable flags and are never printed.
- Multi-stage exports and `$$` references agree.
- Dependencies contain every external package and no empty arrays.
- `install.sh` installs the same dependencies for older clients.
- There is no dependency-removal script.
- Dates and recipe version are correct.
- README and changelog files exist.
- Validation passes and generated artifacts are current.
- The diff contains no credentials, local paths, temporary output, or unrelated
  changes.

## Contributing

Open a focused pull request containing the recipe directory and required
generated artifacts. Explain how the command was tested in AutoPie/Termux and
call out any Android, network, remote-host, or service permissions it needs.
