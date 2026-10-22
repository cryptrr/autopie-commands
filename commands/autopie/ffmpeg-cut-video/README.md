### FFMPEG: Cut Video

Cut a video to a specified start time and end time using FFmpeg.

#### Command

- Path: `Download`
- Command slug: `ffmpeg`
- Type: `SHARE`

```sh
ffmpeg -i "${INPUT_FILE}" -ss ${START} ${END:+-t $END} "${INPUT_FILE}-cut-${RAND}.mp4"
```

#### Extras

| Name  | Type   | Required | Default  | Flags | Options | Details    |
| ----- | ------ | -------- | -------- | ----- | ------- | ---------- |
| START | STRING | no       | 00:00:00 | -     | -       | Start time |
| END   | STRING | no       | -        | -     | -       | End time   |
