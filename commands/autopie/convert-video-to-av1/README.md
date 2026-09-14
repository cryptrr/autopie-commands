### Convert video to AV1

Transcode a video to AV1 in an MKV container using high-quality settings.

#### Command

- Path: `default`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -c:v libaom-av1 -crf 18 -b:v 0 "${INPUT_FILE}.mkv"
```

#### Extras

No extras.
