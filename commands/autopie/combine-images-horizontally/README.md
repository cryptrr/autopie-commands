### Combine Images Horizontally

Resize and arrange multiple images side by side in a single JPEG.

#### Command

- Path: `default`
- Command slug: `magick`

```sh
magick "${INPUT_FILES_ARR[@]}" -resize x${QUALITY} +append "${INPUT_FILE}.horiz-${RAND}.jpeg"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| QUALITY | SELECTABLE | no | 720x | - | 720x, 480x, 1080x | - |
