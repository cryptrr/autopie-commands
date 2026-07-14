# Extract Audio from File

AutoPie command for Extract Audio from File

## Command

- Path: `default`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -b:a ${BITRATE} -vn "${INPUT_FILE}.$FORMAT"
```

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| BITRATE | STRING | no | 195K | - | - | A value from 56K to 320K.<br>Larger means better quality. |
| FORMAT | SELECTABLE | yes | mp3 | - | mp3, m4a, aac, opus, vorbis, flac, wav | Select output format you want. |
