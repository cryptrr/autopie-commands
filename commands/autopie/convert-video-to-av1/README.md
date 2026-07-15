### Convert video to AV1

AutoPie command for Convert video to AV1

#### Command

- Path: `default`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -c:v libaom-av1 -crf 18 -b:v 0 "${INPUT_FILE}.mkv"
```

#### Extras

No extras.
