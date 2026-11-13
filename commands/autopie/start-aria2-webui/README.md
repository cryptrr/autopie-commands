### Start aria2 WebUI

Open AriaNg with a local aria2 server that saves and restores download tasks.

#### Command

- Path: `default`
- Command slug: ``
- Type: `MANUAL`

```sh
#@SHELL
set -euo pipefail
for tool in aria2c curl flock; do
  command -v "$tool" >/dev/null || { echo 'Install: pkg install aria2 curl util-linux' >&2; exit 1; }
done
umask 077
state="$HOME/.config/autopie/aria2"
mkdir -p "$state"
exec 9>"$state/start.lock"
flock -x 9
if [[ ! -s "$state/secret" ]]; then
  od -An -N24 -tx1 /dev/urandom | tr -d ' \n' > "$state/secret"
fi
secret=$(cat "$state/secret")
request="{\"jsonrpc\":\"2.0\",\"id\":\"ping\",\"method\":\"aria2.getVersion\",\"params\":[\"token:$secret\"]}"
rpc_ready() {
  curl -fsS -m 1 -H 'Content-Type: application/json' -d "$request" http://127.0.0.1:6800/jsonrpc 2>/dev/null | grep -q '"result"'
}
pid=''
if ! rpc_ready; then
  session="$state/session"
  touch "$session"
  aria2c --daemon=false --enable-rpc=true --rpc-listen-all=false \
    --rpc-allow-origin-all=true --rpc-secret="$secret" \
    --dir=/sdcard/Download --continue=true --force-save=true \
    --input-file="$session" --save-session="$session" \
    --auto-save-interval=15 --save-session-interval=15 9>&- > "$state/server.log" 2>&1 &
  pid=$!
  trap 'kill -TERM "$pid" 2>/dev/null || true; wait "$pid" || true' EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  trap 'exit 129' HUP
  for i in {1..25}; do
    rpc_ready && break
    kill -0 "$pid" 2>/dev/null || break
    sleep 0.2
  done
  if ! rpc_ready; then
    echo "aria2 RPC did not become ready. Check $state/server.log." >&2
    exit 1
  fi
fi
exec 9>&-
encoded=$(printf '%s' "$secret" | base64 | tr '+/' '-_' | tr -d '\n=')
am start -a android.intent.action.VIEW -d "https://ariang.mayswind.net/latest/#!/settings/rpc/set/http/127.0.0.1/6800/jsonrpc/$encoded"
if [[ -n "$pid" ]]; then
  status=0
  wait "$pid" || status=$?
  trap - EXIT
  exit "$status"
fi
```

- Flags: `--show-loading-screen-small`

#### Extras

No extras.
