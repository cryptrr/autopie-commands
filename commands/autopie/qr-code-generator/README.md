### QR Code Generator

Generate a QR code PNG from shared text or a URL and display it in AutoPie's output viewer.

#### Command

- Path: `Download`
- Command slug: `qrencode`
- Type: `SHARE`

```sh
set +x
set -u

text="${INPUT_TEXT:-${INPUT_URL:-${INPUT:-}}}"
if [ -z "$text" ]; then
  printf '%s\n' 'Share text or a URL to generate a QR code.' >&2
  exit 1
fi

image=$(mktemp "$(pwd -P)/qr-code-XXXXXXXX.png") || exit 1
if ! printf '%s' "$text" | qrencode -t PNG -s 8 -o "$image"; then
  rm -f "$image"
  printf '%s\n' 'Could not generate a QR code. Try sharing less text.' >&2
  exit 1
fi

OUTPUT=$(jq -cn --arg path "$image" '{type:"image", path:$path}') || exit 1
export OUTPUT

app_component="${LOADING_ACTIVITY:-com.autopi/.LoadingActivity}"
am start -n "${app_component%%/*}/.OutputPresentationActivity" \
  --es output "$OUTPUT" --es commandName "QR Code Generator" >/dev/null
```

- Flags: `--show-loading-screen-small`

#### Extras

No extras.
