# Change Volume on Mac

AutoPie command for Change Volume on Mac

## Command

- Path: `AutoSec/scripts`
- Command slug: `openssh`

```sh
sshpass -p "$PASSWORD" ssh -nT \
-o StrictHostKeyChecking=no \
"$USER@$HOST" \
"osascript -e \"set volume output volume ${VOLUME}\""
```

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| USER | STRING | yes | amal | --internal-config | - | The SSH user on the host. |
| HOST | STRING | yes | amals-mac-mini.lan | --internal-config | - | The SSH host to connect to. |
| PASSWORD | STRING | yes | - | --password, --internal-config | - | SSH password. |
| VOLUME | SLIDER | yes | 0,50,100 | --int, --realtime | - | Slider to set volume. |
