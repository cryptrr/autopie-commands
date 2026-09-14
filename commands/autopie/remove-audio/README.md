### Remove Audio

Remove all audio streams from a video without re-encoding the video.

#### Command

- Path: `default`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -an -c:v copy "${INPUT_FILE}-noaud.mp4"
```

#### Extras

No extras.
