### Crop Image/GIF

Crop an image or GIF to a chosen aspect ratio and anchor position.

#### Command

- Path: `default`
- Command slug: `magick`
- Type: `SHARE`

```sh
magick "${INPUT_FILE}" -coalesce -gravity ${POSITION} -crop '%[fx:w]x%[fx:w*${RATIO_HEIGHT}/${RATIO_WIDTH}]+0+0' +repage "${INPUT_FILE}-cropped-${RAND}.${FILE_EXT}"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| RATIO_HEIGHT | STRING | no | 5 | - | - | - |
| RATIO_WIDTH | STRING | no | 3 | - | - | - |
| POSITION | SELECTABLE | no | center | - | center, north, south, east, west | - |
