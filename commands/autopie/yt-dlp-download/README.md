# YT-DLP Download

AutoPie command for YT-DLP Download

## Command

- Path: `Download`
- Command slug: `yt-dlp`

```sh
yt-dlp \
  -o "%(title).200B-${RAND}.%(ext)s" \
  --no-mtime \
  -f "bestvideo[height<=${MAX_QUALITY}]+bestaudio/best[height<=${MAX_QUALITY}]/best" \
  ${COOKIE_JAR:+--cookies "$COOKIE_JAR"} \
  ${START_TIME:+--download-sections "*${START_TIME}-${END_TIME:-inf}"} \
  "$INPUT_URL"
```

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| MAX_QUALITY | SELECTABLE | yes | 1920 | - | 1920, 1080, 720, 480, 2160, 1440 | - |
| START_TIME | STRING | yes | 00:00:00 | - | - | - |
| END_TIME | STRING | no | - | - | - | - |
