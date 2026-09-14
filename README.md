## Contribution Guidelines

Create a PR with the Commands you would like to add to the AutoPie repositories.

## Repository tooling

The manifest generators and validators require Python 3.11 or newer and use
PyYAML for complete YAML support, including multiline block scalars. Install
[uv](https://docs.astral.sh/uv/), then run the tools through the managed
environment:

```sh
uv sync
uv run python tools/validate-manifests.py
uv run python tools/build_default_commands.py
uv run python tools/build_readmes.py
uv run python tools/build_catalog.py
```

Existing manifests can be given approximate UTC catalog timestamps from their
Git history. Existing timestamp fields are preserved unless `--force` is used:

```sh
uv run python tools/backfill_catalog_dates.py
```

Use YAML block scalars for multiline commands:

```yaml
command: |-
  set -euo pipefail
  printf 'Input: %s\n' "$INPUT"
```

## Format

```json

{
  "Extract Audio": {
    #EXTRA DESCRIPTION OF THE COMMAND. CAN BE 1000 CHARS LONG. MARKDOWN SUPPORT.
    "description": "Extracts Audio from Video Files"
    #CURRENT WORKING DIR: DEFAULTS TO USER STORAGE (/storage/emualated/(0|10))
    "path": "",
    #APPLICATION TO RUN
    "exec": "ffmpeg",
    "command": "-i \"${INPUT_FILE}\" -b:a ${BITRATE} -vn \"${INPUT_FILE}.mp3\"",
    #EXTRAS ARE ARBITRARY INPUTS THAT WE CAN CREATE AND CAN BE PLACED IN COMMANDS.
    "extras": [
      {
        "default": "195K",
        "description": "A value from 56K to 320K.\nLarger means better quality.",
        "id": "715336",
        "name": "BITRATE",
        "required": false,
        "type": "STRING"
      }
    ]
  },
  "Convert To WEBP": {
    "path": "",
    "exec": "magick",
    "command": "\"${INPUT_FILE}\" -quality ${QUALITY} -define webp:method=${METHOD} \"${INPUT_FILE}.webp\"",
    #EXTRAS ARE ARBITRARY INPUTS THAT WE CAN CREATE.
    "extras": [
      #EXTRA OF TYPE STRING, CAN BE ANYTHING
      {
        "default": "99",
        "description": "Set a value from 1 to 100.",
        "id": "148663",
        "name": "QUALITY",
        "required": false,
        "type": "STRING"
      },
      {
        #EXTRA OF TYPE SELECTABLE. TAKES IN selectableOptions ARRAY.
        "default": "6",
        "description": "0 is fastest. 6 is slowest.\n6 gives the lowest file size and highest quality.",
        "id": "306994",
        "name": "METHOD",
        "required": false,
        #SELECTABLE OPTIONS: IF DEFAULT NOT SET EXPLICITLY, FIRST ITEM WILL BE THE THE DEFAULT.
        "selectableOptions": [
          "6",
          "0",
          "1",
          "2",
          "3",
          "4",
          "5"
        ],
        "type": "SELECTABLE"
      }
    ]
  }
}
```
