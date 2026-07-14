# Combine Images to GIF

AutoPie command for Combine Images to GIF

## Command

- Path: `default`
- Command slug: `magick`

```sh
magick -delay ${DELAY} -loop 0 ${INPUT_FILES} -gravity center "${INPUT_FILE}-${RAND}.gif"
```

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| DELAY | STRING | no | 100 | - | - | Delay between frames in milliseconds. |
