## Contribution Guidelines

Create a PR with the Commands you would like to add to the AutoPie repositories.

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
    #EXTRAS ARE ARBITRARY INPUTS THAT WE CAN CREATE.
    "extras": [
      #EXTRA OF TYPE STRING, CAN BE ANYTHING
      {
        "default": "99",
        "defaultBoolean": false,
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
        #EXTRA OF TYPE SELECTABLE. TAKES IN selectableOptions ARRAY.
        "default": "6",
        "defaultBoolean": true,
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
