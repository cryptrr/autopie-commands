### Remove Image Borders

Automatically trim uniform borders from an image with configurable color tolerance.

#### Command

- Path: `default`
- Command slug: `magick`
- Type: `SHARE`

```sh
magick "${INPUT_FILE}" -fuzz ${FUZZ}% -trim "${INPUT_FILE}-trim.jpg"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| FUZZ | STRING | yes | 50 | - | - | - |
