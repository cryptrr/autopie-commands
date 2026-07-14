# Extract Audio from URL

AutoPie command for Extract Audio from URL

## Command

- Path: `Mp3`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_URL}" -b:a ${BITRATE} -vn "${FILE_NAME:-$FILENAME}.mp3"
```

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| BITRATE | STRING | yes | 195K | - | - | A value from 56K to 320K.<br>Larger means better quality. |
| FILE_NAME | STRING | yes | - | - | - | Set a custom filename for this file. |
