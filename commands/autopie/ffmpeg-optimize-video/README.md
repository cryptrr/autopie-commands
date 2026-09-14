### FFMPEG: Optimize Video

Compress a video to H.264 and AAC MP4 with fast-start playback enabled.

#### Command

- Path: `/storage/emulated/0/`
- Command slug: `ffmpeg`
- Type: `SHARE`

```sh
ffmpeg -i "${INPUT_FILE}" -c:v libx264 -preset slow -crf 23 -c:a aac -b:a 128k -movflags +faststart "${INPUT_FILE}-optim.mp4"
```

#### Extras

No extras.
