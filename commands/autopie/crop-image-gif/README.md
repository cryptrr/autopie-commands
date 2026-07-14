# Crop Image/GIF

AutoPie command for Crop Image/GIF

## Command

- Path: `default`
- Command slug: `magick`

```sh
magick "${INPUT_FILE}" -coalesce -gravity ${POSITION} -crop '%[fx:w]x%[fx:w*${RATIO_HEIGHT}/${RATIO_WIDTH}]+0+0' +repage "${INPUT_FILE}-cropped-${RAND}.${FILE_EXT}"
```

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| RATIO_HEIGHT | STRING | no | 5 | - | - | - |
| RATIO_WIDTH | STRING | no | 3 | - | - | - |
| POSITION | SELECTABLE | no | center | - | center, north, south, east, west | - |
