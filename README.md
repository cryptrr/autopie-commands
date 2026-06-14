## Contribution Guidelines

Create a PR with the Commands you would like to add to the AutoPie repositories.

## Format

```json

{
  "Extract Audio": {
    "path": "",
    "exec": "ffmpeg",
    "command": "-i \"${INPUT_FILE}\" -b:a ${BITRATE} -vn \"${INPUT_FILE}.mp3\"",
    "deleteSourceFile": false,
    "extras": [
      {
        "default": "195K",
        "defaultBoolean": true,
        "description": "A value from 56K to 320K.\nLarger means better quality.",
        "id": "715336",
        "name": "BITRATE",
        "required": false,
        "selectableOptions": [
          ""
        ],
        "type": "STRING"
      }
    ]
  },
  "Convert To WEBP": {
    "path": "",
    "exec": "magick",
    "command": "\"${INPUT_FILE}\" -quality ${QUALITY} -define webp:method=${METHOD} \"${INPUT_FILE}.webp\"",
    "deleteSourceFile": false,
    "extras": [
      {
        "default": "99",
        "defaultBoolean": true,
        "description": "Set a value from 1 to 100.",
        "id": "148663",
        "name": "QUALITY",
        "required": false,
        "selectableOptions": [
          ""
        ],
        "type": "STRING"
      },
      {
        "default": "6",
        "defaultBoolean": true,
        "description": "0 is fastest. 6 is slowest.\n6 gives the lowest file size and highest quality.",
        "id": "306994",
        "name": "METHOD",
        "required": false,
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
