### wCurl Download

AutoPie command for wCurl Download

#### Command

- Path: `Download`
- Command slug: `wcurl`

```sh
wcurl \
  $NO_REMOTE_TIME \
  ${FILE_NAME_EXTRA:+-o "$FILE_NAME_EXTRA"} \
  "$INPUT_URL"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| NO_REMOTE_TIME | FLAG | no | `--curl-options=--no-remote-time` | - | - | Use the download time instead of the server-provided modification time. |
| FILE_NAME_EXTRA | STRING | no | - | - | - | Set a filename for this file. |
