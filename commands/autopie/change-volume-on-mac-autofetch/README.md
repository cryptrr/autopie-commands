## Change Volume on Mac - AutoFetch

AutoPie command for Change Volume on Mac - AutoFetch

## Steps

#### Step 1

- Path: `AutoSec/scripts`
- Command slug: `openssh`

```sh
CURRENT_VOLUME=$(sshpass -p "$PASSWORD" ssh -nT \
-o StrictHostKeyChecking=no \
"$USER@$HOST" \
"osascript -e \"output volume of (get volume settings)\"")
export CURRENT_VOLUME
export SLIDER_OPTIONS=0,"$CURRENT_VOLUME",100
```

#### Step 2

- Path: `AutoSec/scripts`
- Command slug: `openssh`

```sh
sshpass -p "$PASSWORD" ssh -nT \
-o StrictHostKeyChecking=no \
"$USER@$HOST" \
"osascript -e \"set volume output volume ${VOLUME}\""
```

#### Extras

| Step | Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Step 1 | USER | STRING | yes | amal | --internal-config | - | The SSH user on the host. |
| Step 1 | HOST | STRING | yes | amals-mac-mini.lan | --internal-config | - | The SSH host to connect to. |
| Step 1 | PASSWORD | STRING | yes | - | --internal-config, --password | - | SSH password. |
| Step 2 | VOLUME | SLIDER | yes | $$SLIDER_OPTIONS | --int, --realtime | - | Slider to set volume. |
