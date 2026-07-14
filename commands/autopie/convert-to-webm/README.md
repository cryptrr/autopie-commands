# Convert To WebM

AutoPie command for Convert To WebM

## Command

- Path: `Downloads`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -c:v libvpx-vp9 -crf 24 "${INPUT_FILE}.webm"
```

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| BITRATE | STRING | no | 1M | - | - | Use an ffmpeg compatible bitrate value. |
| CODEC | SELECTABLE | no | libvpx-vp9 | - | libvpx-vp9, libvpx | Choose vp9 for better file size. Choose vp8 for better support. |
| CRF | STRING | no | 24 | - | - | Constant Rate Factor.<br>A value between 4 to 63. Lower means better quality. |
