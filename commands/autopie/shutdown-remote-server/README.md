# Shutdown Remote Server

AutoPie command for Shutdown Remote Server

## Command

- Path: `AutoSec/scripts`
- Command slug: `openssh`

```sh
sshpass -p "$PASSWORD" \
ssh -nT \
-o StrictHostKeyChecking=no \
"$USER@$HOST" \
"echo '$PASSWORD' | sudo -S /sbin/shutdown -h now"
```

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| USER | STRING | yes | - | --internal-config | - | The SSH user on host. |
| HOST | SELECTABLE | yes | amals-mac-mini.lan | --internal-config | amals-mac-mini.lan, pop-os | The SSH host to connect to. |
| PASSWORD | STRING | yes | - | --password, --internal-config | - | SSH password. |
