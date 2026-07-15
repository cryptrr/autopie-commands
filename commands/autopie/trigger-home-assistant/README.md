### Trigger Home Assistant

AutoPie command for Trigger Home Assistant

#### Command

- Path: `default`
- Command slug: `httpx`

```sh
httpx -m POST ${COOKIE_FILE:+--cookie-file $COOKIE_FILE} -d entity_id script.${SCRIPT_NAME} $URL
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| COOKIE_FILE | STRING | yes | /storage/emulated/0/cookies.txt | - | - | The full path to cookie file. |
| SCRIPT_NAME | SELECTABLE | yes | night_mode | - | night_mode, day_mode, lights_off, ambient_mode, emergency | The name of the script that is defined in the home automation server. |
| URL | STRING | yes | https://homeassistant.local/api/services/script/turn_on | - | - | The URL endpoint. |
