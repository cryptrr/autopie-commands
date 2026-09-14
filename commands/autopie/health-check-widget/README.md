### Health Check Widget

A widget that checks a URL every 15 minutes and reports its health and response timings.

#### Command

- Path: `default`
- Command slug: ``
- Type: `CRON`
- Cron interval: `15m`

```sh
RESPONSE_FILE="$HOME/.cache/autopie-health-response.txt"
mkdir -p "$(dirname "$RESPONSE_FILE")"

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

if [[ "$HTTP_CODE" == "200" ]]; then
  STATUS="healthy"
else
  STATUS="unhealthy"
fi

RESPONSE=""
if [[ "$HTTP_CODE" != "200" ]]; then
  RESPONSE="$(cat "$RESPONSE_FILE" 2>/dev/null || true)"
fi

OUTPUT="$(
  STATUS="$STATUS" \
  HTTP_CODE="$HTTP_CODE" \
  LATENCY_MS="$LATENCY_MS" \
  CONNECT_MS="$CONNECT_MS" \
  TTFB_MS="$TTFB_MS" \
  CURRENT_TIME="$CURRENT_TIME" \
  RESPONSE="$RESPONSE" \
  python -c '
import json, os

print(json.dumps({
    "status": os.environ["STATUS"],
    "status_code": int(os.environ["HTTP_CODE"]) if os.environ["HTTP_CODE"].isdigit() else 0,
    "latency_ms": int(os.environ["LATENCY_MS"]),
    "connect_ms": int(os.environ["CONNECT_MS"]),
    "ttfb_ms": int(os.environ["TTFB_MS"]),
    "current_time": os.environ["CURRENT_TIME"],
    "response": os.environ["RESPONSE"] or None
}, separators=(",", ":")))
'
)"

export OUTPUT
printf '%s\n' "$OUTPUT"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| URL | STRING | yes | - | --internal-config | - | The URL to check health. |
