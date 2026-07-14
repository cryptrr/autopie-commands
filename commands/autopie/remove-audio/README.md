# Remove Audio

AutoPie command for Remove Audio

## Command

- Path: `default`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -an -c:v copy "${INPUT_FILE}-noaud.mp4"
```

## Extras

No extras.
