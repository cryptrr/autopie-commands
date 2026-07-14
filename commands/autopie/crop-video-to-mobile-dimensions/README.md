# Crop Video to Mobile Dimensions

AutoPie command for Crop Video to Mobile Dimensions

## Command

- Path: `default`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -vf \"crop=${WIDTH}/${HEIGHT}*in_h:in_h\" -c:a copy "${INPUT_FILE}.cropped.mp4"
```

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| WIDTH | STRING | no | 9 | - | - | Width as aspect ratio |
| HEIGHT | STRING | no | 16 | - | - | Height as aspect ratio |
