### Resize Video

AutoPie command for Resize Video

#### Command

- Path: `default`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -vf "scale=${HEIGHT}:${WIDTH}" -c:a copy "${INPUT_FILE}-resized-${RAND}.mp4"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| HEIGHT | STRING | no | 1280 | - | - | Height in pixels |
| WIDTH | STRING | no | 720 | - | - | Width in pixels. |
