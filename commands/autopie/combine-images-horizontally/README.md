# Combine Images Horizontally

AutoPie command for Combine Images Horizontally

## Command

- Path: `default`
- Command slug: `magick`

```sh
magick "${INPUT_FILES_ARR[@]}" -resize x${QUALITY} +append "${INPUT_FILE}.horiz-${RAND}.jpeg"
```

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| QUALITY | SELECTABLE | no | 720x | - | 720x, 480x, 1080x | - |
