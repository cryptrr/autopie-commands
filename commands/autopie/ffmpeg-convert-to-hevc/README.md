### FFMPEG: Convert to HEVC

Transcode a video to an H.264 MP4 at CRF 24 using FFmpeg.

#### Command

- Path: `default`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -c:v libx264 -crf 24 -preset medium "${INPUT_FILE}-x265.mp4"
```

#### Extras

No extras.
