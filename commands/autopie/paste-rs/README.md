### Send to Paste.rs

Upload shared text to Paste.rs, then share the resulting URL through Android.

#### Command

- Path: `default`
- Command slug: ``
- Type: `SHARE`

```sh
set -e

if [[ -z "$INPUT" ]]; then
  echo "No text provided"
  exit 1
fi

RESPONSE_FILE="$(mktemp)"
trap 'rm -f "$RESPONSE_FILE"' EXIT

HTTP_CODE=$(printf '%s' "$INPUT" | curl -sS \
  -o "$RESPONSE_FILE" \
  -w '%{http_code}' \
  --data-binary @- \
  https://paste.rs/)

if [[ "$HTTP_CODE" != "201" ]]; then
  echo "Paste upload failed (HTTP $HTTP_CODE)"
  cat "$RESPONSE_FILE"
  exit 1
fi

URL="$(cat "$RESPONSE_FILE")"
export OUTPUT="$URL"

am start \
  -a android.intent.action.SEND \
  -t 'text/plain' \
  --es android.intent.extra.TEXT "$URL"
```

- Flags: `--show-loading-screen-small`

#### Extras

No extras.
