# Open in Video Player

AutoPie command for Open in Video Player

## Command

- Path: `default`
- Command slug: `am`

```sh
url=$(yt-dlp --no-warnings -q -g -f "${FORMAT}" "${INPUT_URL}")
am start \
    -a android.intent.action.SEND \
    -t text/plain \
    --es android.intent.extra.TEXT $url
```

- Flags: `--show-loading-screen`

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| FORMAT | SELECTABLE | yes | b | - | b, bv*+ba/b | - |
