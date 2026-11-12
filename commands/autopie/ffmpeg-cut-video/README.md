### FFMPEG: Cut Video

Cut a video to a specified start time and end time using FFmpeg.

#### Command

- Path: `Download`
- Command slug: `ffmpeg`
- Type: `SHARE`

```sh
ffmpeg -ss "${START:-00:00:00}" ${END:+-to "$END"} -i "${INPUT_FILE}" -c:v libx264 -c:a aac "${INPUT_FILE}-cut-${RAND}.mp4"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| START | STRING | no | 00:00:00 | - | - | Start time |
| END | STRING | no | - | - | - | End time  |
