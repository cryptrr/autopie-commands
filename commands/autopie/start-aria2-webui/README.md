### Start aria2 WebUI

Start a local aria2 RPC server for Android downloads and open AriaNg in the browser.

#### Command

- Path: `default`
- Command slug: ``
- Type: `SHARE`

```sh
#@SHELL
set -euo pipefail
command -v aria2c >/dev/null || { echo 'Install: pkg install aria2 curl'; exit 1; }
umask 077
state="$HOME/.config/autopie/aria2"
mkdir -p "$state"
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
  aria2c --enable-rpc=true --rpc-listen-all=false --rpc-allow-origin-all=true --rpc-secret="$secret" --dir=/sdcard/Download --continue=true > "$state/server.log" 2>&1 &
  pid=$!
  for i in {1..15}; do rpc_ready && break; sleep 0.2; done
  if ! rpc_ready; then cat "$state/server.log"; exit 1; fi
fi
encoded=$(printf '%s' "$secret" | base64 | tr '+/' '-_' | tr -d '\n=')
am start -a android.intent.action.VIEW -d "https://ariang.mayswind.net/latest/#!/settings/rpc/set/http/127.0.0.1/6800/jsonrpc/$encoded"
if [[ -n "$pid" ]]; then
  trap 'kill "$pid" 2>/dev/null || true' EXIT
  wait "$pid"
fi
```

- Flags: `--show-loading-screen-small`

#### Extras

No extras.
