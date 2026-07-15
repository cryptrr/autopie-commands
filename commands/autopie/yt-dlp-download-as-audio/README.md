### YT-DLP: Download as Audio

AutoPie command for YT-DLP: Download as Audio

#### Command

- Path: `Download`
- Command slug: `yt-dlp`

```sh
yt-dlp --no-mtime -x --audio-format ${FORMAT} "${INPUT_URL}"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| FORMAT | SELECTABLE | yes | mp3 | - | mp3, m4a, aac, opus, vorbis, flac, wav | Choose the format to convert to. |
