# Remove Image Borders

AutoPie command for Remove Image Borders

## Command

- Path: `default`
- Command slug: `magick`

```sh
magick "${INPUT_FILE}" -fuzz ${FUZZ}% -trim "${INPUT_FILE}-trim.jpg"
```

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| FUZZ | STRING | yes | 50 | - | - | - |
