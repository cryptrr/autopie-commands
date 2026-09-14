### wCurl Download

Download a URL with wcurl using an optional filename and timestamp behavior.

#### Command

- Path: `Download`
- Command slug: `wcurl`
- Type: `SHARE`

```sh
wcurl \
  $NO_REMOTE_TIME \
  ${FILE_NAME_EXTRA:+-o "$FILE_NAME_EXTRA"} \
  "$INPUT_URL"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| NO_REMOTE_TIME | FLAG | no | enabled (`--curl-options=--no-remote-time`) | - | - | Use the download time instead of the server-provided modification time. |
| FILE_NAME_EXTRA | STRING | no | - | - | - | Set a filename for this file. |
