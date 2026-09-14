### YT-DLP: Download as Audio

Download media from a URL and extract it in a selected audio format.

#### Command

- Path: `Download`
- Command slug: `yt-dlp`
- Type: `SHARE`

```sh
yt-dlp --no-mtime -x --audio-format ${FORMAT} "${INPUT_URL}"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| FORMAT | SELECTABLE | yes | mp3 | - | mp3, m4a, aac, opus, vorbis, flac, wav | Choose the format to convert to. |
