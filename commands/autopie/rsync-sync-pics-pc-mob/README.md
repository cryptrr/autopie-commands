# RSYNC: Sync Pics - PC ➡️ Mob

AutoPie command for RSYNC: Sync Pics - PC ➡️ Mob

## Command

- Path: `default`
- Command slug: `rsync`

```sh
rsync -avz "${FOLDER_FROM}" "${FOLDER_TO}"
```

## Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| RSYNC_PASSWORD | STRING | yes | - | --password, --internal-config | - | The remote machine should be running RSYNC daemon.<br>For security reasons, limit the usage of the RSYNC protocol to the local network. |
| FOLDER_FROM | STRING | no | rsync://user@192.168.1.132/home/user/Pictures_Backup/ | --internal-config | - | The remote folder to sync to your device.<br>Should be in the format 'rsync://user@192.168.1.132/path/to/folder/' |
| FOLDER_TO | STRING | no | /storage/emulated/0/Pictures/ | --internal-config | - | Absolute path to the folder on your device. |
