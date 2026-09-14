### Combine Images to GIF

Turn a sequence of images into a looping GIF with a configurable frame delay.

#### Command

- Path: `default`
- Command slug: `magick`
- Type: `SHARE`

```sh
magick -delay ${DELAY} -loop 0 ${INPUT_FILES} -gravity center "${INPUT_FILE}-${RAND}.gif"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| DELAY | STRING | no | 100 | - | - | Delay between frames in milliseconds. |
