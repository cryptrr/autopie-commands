### OpenWRT Router Automations

AutoPie command for OpenWRT Router Automations

#### Command

- Path: `default`
- Command slug: `openssh`

```sh
sshpass -p "$PASSWORD" ssh -nT \
-o StrictHostKeyChecking=no \
"$USER@$HOST" \
"$REMOTE_COMMAND"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| USER | STRING | yes | root | --internal-config | - | The SSH user on the host. |
| HOST | STRING | yes | openwrt | --internal-config | - | The SSH host to connect to. |
| PASSWORD | STRING | yes | - | --password, --internal-config | - | SSH password. |
| REMOTE_COMMAND | SELECTABLE | yes | uci set wireless.radio0.disabled=0 && uci commit wireless && wifi reload | - | Enable 5GHz=uci set wireless.radio0.disabled=0 && uci commit wireless && wifi reload, Disable 5GHz=uci set wireless.radio0.disabled=1 && uci commit wireless && wifi reload, /etc/init.d/network restart, reboot, logread, ifdown wan && ifup wan, wifi reload, etherwake -i br-lan AA:BB:CC:DD:EE:FF | The command to run after sshing into the remote server. |
