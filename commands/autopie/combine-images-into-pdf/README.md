### Combine Images into PDF

AutoPie command for Combine Images into PDF

#### Command

- Path: `default`
- Command slug: `magick`

```sh
magick "${INPUT_FILES_ARR[@]}" -resize ${QUALITY} -gravity center -extent ${QUALITY} "${INPUT_FILE}.pdf"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| QUALITY | SELECTABLE | no | 720x | - | 720x, 480x, 1080x | Choose the PDF width. |
