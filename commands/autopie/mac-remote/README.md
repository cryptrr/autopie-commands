### Mac Remote

Control Music playback, adjust volume, open Safari, or sleep a Mac's display over SSH.

#### Command

- Path: `default`
- Command slug: `openssh`
- Type: `SHARE`

```sh
mkdir -p "$HOME/.ssh"

case "$ACTION" in
  previous)
    REMOTE="osascript -e 'tell application \"Music\" to previous track'"
    ;;
  play_pause)
    REMOTE="osascript -e 'tell application \"Music\" to playpause'"
    ;;
  next)
    REMOTE="osascript -e 'tell application \"Music\" to next track'"
    ;;
  volume_down)
    REMOTE="osascript -e 'set volume output volume ((output volume of (get volume settings)) - 10)'"
    ;;
  mute)
    REMOTE="osascript -e 'set volume output muted (not (output muted of (get volume settings)))'"
    ;;
  volume_up)
    REMOTE="osascript -e 'set volume output volume ((output volume of (get volume settings)) + 10)'"
    ;;
  safari)
    REMOTE="open -a Safari"
    ;;
  sleep_display)
    REMOTE="pmset displaysleepnow"
    ;;
  *)
    printf 'Unsupported action: %s\n' "$ACTION" >&2
    exit 2
    ;;
esac

SSH_TARGET="$MAC_USER@$MAC_HOST"
SSH_OPTIONS=(
  -o ConnectTimeout=4
  -o StrictHostKeyChecking=accept-new
  -o ControlMaster=auto
  -o ControlPersist=10m
  -o ControlPath="$HOME/.ssh/autopie-%C"
)

case "$AUTH_METHOD" in
  password)
    if [ -z "$MAC_PASSWORD" ]; then
      printf 'The Mac password is required.\n' >&2
      exit 2
    fi

    SSHPASS="$MAC_PASSWORD" sshpass -e ssh \
      "${SSH_OPTIONS[@]}" \
      -o PubkeyAuthentication=no \
      -o PreferredAuthentications=password,keyboard-interactive \
      -o NumberOfPasswordPrompts=1 \
      "$SSH_TARGET" \
      "$REMOTE"
    ;;
  key)
    ssh \
      "${SSH_OPTIONS[@]}" \
      -o BatchMode=yes \
      "$SSH_TARGET" \
      "$REMOTE"
    ;;
  *)
    printf 'Unsupported authentication method: %s\n' "$AUTH_METHOD" >&2
    exit 2
    ;;
esac
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| MAC_USER | STRING | yes | amal | --internal-config | - | Your macOS account username |
| MAC_HOST | STRING | yes | amals-mac-mini.lan | --internal-config | - | Mac hostname or IP address |
| AUTH_METHOD | SELECTABLE | yes | password | --internal-config | Password=password, SSH key=key | SSH authentication method |
| MAC_PASSWORD | STRING | yes | - | --password, --large, --internal-config | - | macOS login password; encrypted by AutoPie |
| ACTION | BUTTON | yes | play_pause | --realtime, --large | ⏯ Play/Pause=play_pause, 🌙 Sleep Display=sleep_display, ⏮ Previous=previous, ⏭ Next=next, 🔉 Volume −=volume_down, 🔊 Volume +=volume_up, 🔇 Mute=mute, 🌐 Safari=safari | Control your Mac |
