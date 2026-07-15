### RSYNC: Backup Pics to PC

AutoPie command for RSYNC: Backup Pics to PC

#### Command

- Path: `default`
- Command slug: `rsync`

```sh
rsync -avz "${FOLDER_FROM}" "${FOLDER_TO}"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| RSYNC_PASSWORD | STRING | yes | - | --password, --internal-config | - | The remote machine should be running RSYNC daemon.<br>For security reasons, limit the usage of the RSYNC protocol to the local network. |
| FOLDER_TO | STRING | no | rsync://user@host/path/to/folder/ | --internal-config | - | The remote folder to send backups to.<br>Should be in the format 'rsync://user@host/path/to/folder/' |
| FOLDER_FROM | STRING | no | /storage/emulated/0/Pictures/ | --internal-config | - | Absolute path to the folder on your device |
