### Health Check Notification

Check a URL every 15 minutes and send an Android notification only when a failure is detected.

AutoPie must have Android notification permission, and its main notification channel must be enabled. Tapping a notification opens the command log.

#### Command

- Path: `default`
- Command slug: ``
- Type: `CRON`
- Cron interval: `15m`

```sh
RESPONSE_FILE="$HOME/.cache/autopie-health-notification-response.txt"
mkdir -p "$(dirname "$RESPONSE_FILE")"
: > "$RESPONSE_FILE"

METRICS="$(
  curl -sS \
    -o "$RESPONSE_FILE" \
    -w '%{http_code}|%{time_total}|%{time_connect}|%{time_starttransfer}|%{size_download}' \
    --max-time 10 \
    "$URL"
)"
CURL_STATUS=$?

IFS='|' read -r HTTP_CODE TIME_TOTAL TIME_CONNECT TIME_TTFB SIZE_DOWNLOAD <<< "$METRICS"

if [[ "$CURL_STATUS" -ne 0 ]]; then
  HTTP_CODE="000"
fi

LATENCY_MS=$(awk "BEGIN {printf \"%.0f\", ${TIME_TOTAL:-0} * 1000}")
CONNECT_MS=$(awk "BEGIN {printf \"%.0f\", ${TIME_CONNECT:-0} * 1000}")
TTFB_MS=$(awk "BEGIN {printf \"%.0f\", ${TIME_TTFB:-0} * 1000}")
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')

if [[ "$CURL_STATUS" -eq 0 && "$HTTP_CODE" == "200" ]]; then
  printf 'Healthy: %s (HTTP %s, %s ms)\n' "$URL" "$HTTP_CODE" "$LATENCY_MS"
  exit 0
fi

RESPONSE="$(cat "$RESPONSE_FILE" 2>/dev/null || true)"

URL="$URL" \
CURL_STATUS="$CURL_STATUS" \
HTTP_CODE="$HTTP_CODE" \
LATENCY_MS="$LATENCY_MS" \
CONNECT_MS="$CONNECT_MS" \
TTFB_MS="$TTFB_MS" \
CURRENT_TIME="$CURRENT_TIME" \
RESPONSE="$RESPONSE" \
python -c '
import json
import os
from urllib.parse import urlparse

url = os.environ["URL"]
host = urlparse(url).hostname or url
curl_status = int(os.environ["CURL_STATUS"])
http_code = int(os.environ["HTTP_CODE"]) if os.environ["HTTP_CODE"].isdigit() else 0
latency_ms = os.environ["LATENCY_MS"]
connect_ms = os.environ["CONNECT_MS"]
ttfb_ms = os.environ["TTFB_MS"]
current_time = os.environ["CURRENT_TIME"]

if curl_status:
    status = f"Connection failed (curl exit {curl_status})"
else:
    status = f"HTTP {http_code}"

lines = [
    f"URL: {url}",
    f"Status: {status}",
    f"Latency: {latency_ms} ms",
    f"Connect: {connect_ms} ms",
    f"TTFB: {ttfb_ms} ms",
    f"Checked: {current_time}",
]

response = os.environ.get("RESPONSE", "").strip()
if response:
    if len(response) > 500:
        response = response[:500] + "…"
    lines.extend(["", f"Response: {response}"])

print("#@AUTOPIE " + json.dumps({
    "type": "notification",
    "title": f"Health Check Failed • {host}",
    "body": "\n".join(lines),
}, separators=(",", ":")))
'
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| URL | STRING | yes | - | --internal-config | - | The URL to check health. |
