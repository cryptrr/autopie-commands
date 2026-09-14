### Extract Audio from URL

Extract an MP3 audio track from a media URL with a custom bitrate and filename.

#### Command

- Path: `Mp3`
- Command slug: `ffmpeg`
- Type: `SHARE`

```sh
ffmpeg -i "${INPUT_URL}" -b:a ${BITRATE} -vn "${FILE_NAME:-$FILENAME}.mp3"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| BITRATE | STRING | yes | 195K | - | - | A value from 56K to 320K.<br>Larger means better quality. |
| FILE_NAME | STRING | yes | - | - | - | Set a custom filename for this file. |
