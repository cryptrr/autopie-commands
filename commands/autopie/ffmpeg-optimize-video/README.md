### FFMPEG: Optimize Video

AutoPie command for FFMPEG: Optimize Video

#### Command

- Path: `/storage/emulated/0/`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -c:v libx264 -preset slow -crf 23 -c:a aac -b:a 128k -movflags +faststart "${INPUT_FILE}-optim.mp4"
```

#### Extras

No extras.
