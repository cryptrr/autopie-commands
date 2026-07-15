### Convert To WEBP

AutoPie command for Convert To WEBP

#### Command

- Path: `default`
- Command slug: `magick`

```sh
magick "${INPUT_FILE}" -quality ${QUALITY} -define webp:method=${METHOD} "${INPUT_FILE}.webp"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| QUALITY | STRING | no | 99 | - | - | Set a value from 1 to 100. |
| METHOD | SELECTABLE | no | 6 | - | 6, 0, 1, 2, 3, 4, 5 | 0 is fastest. 6 is slowest.<br>6 gives the lowest file size and highest quality. |
