# Watermark Video

AutoPie command for Watermark Video

## Command

- Path: `default`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -i "${WATERMARK_FILE}" -filter_complex "overlay=$( \
    case $POSITION in \
        TOP_LEFT) echo '10:10';; \
        TOP_RIGHT) echo 'W-w-10:10';; \
        BOTTOM_LEFT) echo '10:H-h-10';; \
        BOTTOM_RIGHT) echo 'W-w-10:H-h-10';; \
        CENTER) echo '(W-w)/2:(H-h)/2';; \
        *) echo 'W-w-10:10';; \
    esac)" -codec:a copy "${INPUT_FILE}-watermarked-${RAND}.mp4"
```

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| WATERMARK_FILE | STRING | yes | - | - | - | Full path to the watermark image. |
| POSITION | SELECTABLE | yes | BOTTOM_RIGHT | - | BOTTOM_RIGHT, TOP_RIGHT, TOP_LEFT, BOTTOM_LEFT, CENTER | Choose the position where you want to put the watermark. |
