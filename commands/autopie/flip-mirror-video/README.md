### Flip/Mirror Video

Mirror a video horizontally while preserving it as an MP4.

#### Command

- Path: `default`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -vf "hflip" "${INPUT_FILE}-mirrored.mp4"
```

#### Extras

No extras.
