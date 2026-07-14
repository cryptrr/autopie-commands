# FFMPEG: Convert to HEVC

AutoPie command for FFMPEG: Convert to HEVC

## Command

- Path: `default`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -c:v libx264 -crf 24 -preset medium "${INPUT_FILE}-x265.mp4"
```

## Extras

No extras.
