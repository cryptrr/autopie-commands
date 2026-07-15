### Combine Gifs Vertically

AutoPie command for Combine Gifs Vertically

#### Command

- Path: `default`
- Command slug: `magick`

```sh
magick "${INPUT_FILES_ARR[@]}" -resize ${QUALITY}x -append "${INPUT_FILE}.vert.gif"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| QUALITY | SELECTABLE | no | 720x | - | 720x, 480x, 1080x | - |
