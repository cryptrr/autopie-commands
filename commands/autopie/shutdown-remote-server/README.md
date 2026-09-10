### Shutdown Remote Server

Shut down a remote server using SSH password or private-key authentication.

#### Command

- Path: `default`
- Command slug: `openssh`

```sh
set -euo pipefail

command -v ssh >/dev/null 2>&1 || {
  echo "OpenSSH is not installed."
  exit 1
}

[[ "$SSH_PORT" =~ ^[0-9]+$ ]] || {
  echo "Invalid SSH port: $SSH_PORT"
  exit 1
}

SSH_ARGS=(
  ssh
  -T
  -p "$SSH_PORT"
  -o ConnectTimeout=10
  -o StrictHostKeyChecking=accept-new
)

case "$AUTH_METHOD" in
  password)
    command -v sshpass >/dev/null 2>&1 || {
      echo "sshpass is required for password authentication."
      exit 1
    }

    [[ -n "$PASSWORD" ]] || {
      echo "An SSH password is required for password authentication."
      exit 1
    }
    ;;

  key)
    SSH_KEY_RESOLVED="${SSH_KEY_PATH/#\~/$HOME}"

    [[ -r "$SSH_KEY_RESOLVED" ]] || {
      echo "SSH private key is not readable: $SSH_KEY_RESOLVED"
      exit 1
    }

    SSH_ARGS+=(
      -o BatchMode=yes
      -o IdentitiesOnly=yes
      -i "$SSH_KEY_RESOLVED"
    )
    ;;

  *)
    echo "Unsupported authentication method: $AUTH_METHOD"
    exit 1
    ;;
esac

remote_ssh() {
  if [[ "$AUTH_METHOD" == "password" ]]; then
    SSHPASS="$PASSWORD" sshpass -e "${SSH_ARGS[@]}" \
      "$USER@$HOST" "$@"
  else
    "${SSH_ARGS[@]}" "$USER@$HOST" "$@"
  fi
}

ELEVATION_PASSWORD="$SUDO_PASSWORD"
if [[ -z "$ELEVATION_PASSWORD" && "$AUTH_METHOD" == "password" ]]; then
  ELEVATION_PASSWORD="$PASSWORD"
fi

if [[ -n "$ELEVATION_PASSWORD" ]]; then
  printf '%s\n' "$ELEVATION_PASSWORD" | remote_ssh \
    'if [ "$(id -u)" -eq 0 ]; then /sbin/shutdown -h now; else sudo -S -p "" /sbin/shutdown -h now; fi'
else
  remote_ssh \
    'if [ "$(id -u)" -eq 0 ]; then /sbin/shutdown -h now; else sudo -n /sbin/shutdown -h now; fi'
fi
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| USER | STRING | yes | - | --internal-config | - | The SSH user on host. |
| HOST | SELECTABLE | yes | server.local | - | server.local, workstation.lan | The SSH host to connect to. |
| SSH_PORT | STRING | yes | 22 | --internal-config | - | SSH port on the remote server. |
| AUTH_METHOD | SELECTABLE | yes | password | --internal-config | Password=password, SSH key=key | Authentication method used to connect to the remote server. |
| PASSWORD | STRING | yes | - | --secret, --internal-config | - | SSH password. It is also used for sudo when no separate sudo password is set. |
| SSH_KEY_PATH | STRING | yes | ~/.ssh/id_ed25519 | --internal-config | - | Private SSH key inside AutoPie's Linux environment. |
| SUDO_PASSWORD | STRING | no | - | --secret, --internal-config | - | Optional sudo password. Leave blank for root or passwordless sudo. |
