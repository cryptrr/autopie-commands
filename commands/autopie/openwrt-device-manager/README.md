### OpenWRT Device Manager

Discover and manage OpenWrt network clients over SSH.

#### Steps

##### Step 1

- Path: `Download`
- Command slug: `openssh`

```sh
set -eo pipefail

command -v ssh >/dev/null 2>&1 || {
  echo "OpenSSH is not installed."
  exit 1
}

if [[ ! "$ROUTER_PORT" =~ ^[0-9]+$ ]]; then
  echo "Invalid SSH port."
  exit 1
fi

if [[ ! "$FIREWALL_SRC_ZONE" =~ ^[A-Za-z0-9_-]+$ ]] || [[ ! "$FIREWALL_DEST_ZONE" =~ ^[A-Za-z0-9_-]+$ ]]; then
  echo "Invalid firewall zone name."
  exit 1
fi

if [[ "$AUTH_METHOD" == "password" ]] && ! command -v sshpass >/dev/null 2>&1; then
  echo "sshpass is required for password authentication."
  exit 1
fi

export SSH_KEY_RESOLVED="${SSH_KEY_PATH/#\~/$HOME}"

if [[ "$AUTH_METHOD" == "key" && ! -r "$SSH_KEY_RESOLVED" ]]; then
  echo "SSH private key is not readable: $SSH_KEY_RESOLVED"
  exit 1
fi

SSH_BASE=(
  ssh
  -p "$ROUTER_PORT"
  -o ConnectTimeout=7
  -o ServerAliveInterval=10
  -o StrictHostKeyChecking=accept-new
)

router_ssh() {
  if [[ "$AUTH_METHOD" == "password" ]]; then
    SSHPASS="$ROUTER_PASSWORD" sshpass -e "${SSH_BASE[@]}" \
      "$ROUTER_USER@$ROUTER_HOST" "$@"
  else
    "${SSH_BASE[@]}" \
      -o BatchMode=yes \
      -i "$SSH_KEY_RESOLVED" \
      "$ROUTER_USER@$ROUTER_HOST" "$@"
  fi
}

router_ssh "printf 'AUTOPIE_OPENWRT_OK\\n'" | grep -q '^AUTOPIE_OPENWRT_OK$' || {
  echo "Could not connect to the OpenWrt router."
  exit 1
}

CLIENT_RAW="$(
  router_ssh 'sh -s' <<'REMOTE'
if [ -r /tmp/dhcp.leases ]; then
  awk '{
    host=$4
    if (host=="" || host=="*") host="Unknown"
    printf "LEASE\t%s\t%s\t%s\n", tolower($2), $3, host
  }' /tmp/dhcp.leases
fi

ip neigh show 2>/dev/null | awk '{
  ip=$1
  mac=""
  state=$NF

  for (i=1; i<=NF; i++) {
    if ($i=="lladdr" && i<NF) mac=tolower($(i+1))
  }

  if (mac!="")
    printf "NEIGH\t%s\t%s\t%s\n", mac, ip, state
}'

for obj in $(ubus list 'hostapd.*' 2>/dev/null); do
  ubus call "$obj" get_clients 2>/dev/null |
    grep -Eio '([0-9a-f]{2}:){5}[0-9a-f]{2}' |
    tr 'A-F' 'a-f' |
    sort -u |
    while IFS= read -r mac; do
      [ -n "$mac" ] && printf "WIFI\t%s\t%s\n" "$mac" "$obj"
    done
done
REMOTE
)"

export CLIENT_RAW

eval "$(
  CLIENT_RAW="$CLIENT_RAW" CLIENT_SCOPE="$CLIENT_SCOPE" python - <<'PYCLIENTS'
import os
import re
import shlex

records = os.environ.get("CLIENT_RAW", "").splitlines()
scope = os.environ.get("CLIENT_SCOPE", "online")
devices = {}

mac_re = re.compile(r"^(?:[0-9a-f]{2}:){5}[0-9a-f]{2}$", re.I)


def get_device(mac):
    mac = mac.lower()
    return devices.setdefault(mac, {
        "mac": mac,
        "ip": "",
        "hostname": "Unknown",
        "online": False,
        "wifi_object": ""
    })


for line in records:
    parts = line.split("\t")
    if not parts:
        continue

    kind = parts[0]

    if kind == "LEASE" and len(parts) >= 4:
        mac = parts[1].lower()
        if not mac_re.match(mac):
            continue

        d = get_device(mac)
        d["ip"] = parts[2]

        if parts[3] and parts[3] != "*":
            d["hostname"] = parts[3]

    elif kind == "NEIGH" and len(parts) >= 4:
        mac = parts[1].lower()
        if not mac_re.match(mac):
            continue

        d = get_device(mac)

        if not d["ip"]:
            d["ip"] = parts[2]

        state = parts[3].upper()
        if state not in {"FAILED", "INCOMPLETE", "NONE"}:
            d["online"] = True

    elif kind == "WIFI" and len(parts) >= 3:
        mac = parts[1].lower()
        if not mac_re.match(mac):
            continue

        d = get_device(mac)
        d["wifi_object"] = parts[2]
        d["online"] = True


def include(d):
    if scope == "all":
        return True
    if scope == "wifi":
        return bool(d["wifi_object"])
    if scope == "wired":
        return d["online"] and not d["wifi_object"]
    return d["online"]


selected = [d for d in devices.values() if include(d)]

selected.sort(key=lambda d: (
    not d["online"],
    d["hostname"].lower(),
    d["ip"],
    d["mac"]
))

if not selected:
    raise SystemExit(
        f"No clients matched scope '{scope}'. "
        "Try All known clients if the device is offline."
    )


def clean(value):
    value = re.sub(r"\s+", " ", str(value)).strip()
    return value.replace(",", " ").replace("=", "-")


options = []

for d in selected:
    if d["wifi_object"]:
        connection = "Wi-Fi"
    elif d["online"]:
        connection = "LAN"
    else:
        connection = "Offline"

    label = (
        f"{clean(d['hostname'])} — "
        f"{clean(d['ip'] or 'No IP')} — "
        f"{connection} — {d['mac']}"
    )

    options.append(f"{label}={d['mac']}")

print("export CLIENT_OPTIONS=" + shlex.quote(",".join(options)))
print("export CLIENT_DEFAULT=" + shlex.quote(selected[0]["mac"]))
print("export CLIENT_COUNT=" + shlex.quote(str(len(selected))))
PYCLIENTS
)"

printf 'Router: %s\nDiscovered clients: %s\n\nChoose a device in the next step.\n' \
  "$ROUTER_HOST" \
  "$CLIENT_COUNT"
```

##### Step 2

- Path: `Download`
- Command slug: `openssh`

```sh
set -eo pipefail

export DEVICE_MAC="$(printf '%s' "$DEVICE_MAC" | tr 'A-F' 'a-f')"

DEVICE_RAW="$(
  router_ssh "MAC='$DEVICE_MAC' sh -s" <<'REMOTE'
mac="$(printf '%s' "$MAC" | tr 'A-F' 'a-f')"

lease_line="$(
  awk -v wanted="$mac" '
    tolower($2)==wanted {
      host=$4
      if (host=="" || host=="*") host="Unknown"
      print $3 "\t" host
      exit
    }
  ' /tmp/dhcp.leases 2>/dev/null
)"

ip="$(printf '%s' "$lease_line" | cut -f1)"
hostname="$(printf '%s' "$lease_line" | cut -f2-)"

if [ -z "$ip" ]; then
  ip="$(
    ip neigh show 2>/dev/null |
      awk -v wanted="$mac" '
        {
          found=""
          for (i=1; i<=NF; i++) {
            if ($i=="lladdr" && i<NF)
              found=tolower($(i+1))
          }

          if (found==wanted) {
            print $1
            exit
          }
        }
      '
  )"
fi

[ -n "$hostname" ] || hostname="Unknown"

wifi_obj=""

for obj in $(ubus list 'hostapd.*' 2>/dev/null); do
  if ubus call "$obj" get_clients 2>/dev/null | grep -qi "\"$mac\""; then
    wifi_obj="$obj"
    break
  fi
done

reachable="no"

if [ -n "$ip" ] && ping -c 1 -W 1 "$ip" >/dev/null 2>&1; then
  reachable="yes"
fi

block_name="AutoPie Block $mac"

block_ref="$(
  uci show firewall 2>/dev/null |
    grep -F ".name='$block_name'" |
    head -n 1 |
    sed 's/\.name=.*//'
)"

managed_lease_name="AutoPie Lease $mac"

managed_lease_ref="$(
  uci show dhcp 2>/dev/null |
    grep -F ".name='$managed_lease_name'" |
    head -n 1 |
    sed 's/\.name=.*//'
)"

any_lease_ref="$(
  uci show dhcp 2>/dev/null |
    grep -Fi ".mac='$mac'" |
    head -n 1 |
    sed 's/\.mac=.*//'
)"

printf 'IP=%s\n' "$ip"
printf 'HOSTNAME=%s\n' "$hostname"
printf 'WIFI_OBJECT=%s\n' "$wifi_obj"
printf 'REACHABLE=%s\n' "$reachable"
printf 'BLOCKED=%s\n' "$([ -n "$block_ref" ] && echo yes || echo no)"

if [ -n "$managed_lease_ref" ]; then
  printf 'RESERVATION=managed\n'
elif [ -n "$any_lease_ref" ]; then
  printf 'RESERVATION=existing\n'
else
  printf 'RESERVATION=none\n'
fi
REMOTE
)"

export DEVICE_RAW

eval "$(
  DEVICE_RAW="$DEVICE_RAW" DEVICE_MAC="$DEVICE_MAC" python - <<'PYDEVICE'
import os
import re
import shlex

data = {}

for line in os.environ.get("DEVICE_RAW", "").splitlines():
    if "=" in line:
        key, value = line.split("=", 1)
        data[key] = value

mac = os.environ["DEVICE_MAC"]
hostname = data.get("HOSTNAME") or "Unknown"
ip = data.get("IP") or ""
wifi_object = data.get("WIFI_OBJECT") or ""
reachable = data.get("REACHABLE") == "yes"
blocked = data.get("BLOCKED") == "yes"
reservation = data.get("RESERVATION", "none")

actions = []

if ip:
    actions.append(("Ping device", "ping"))

if blocked:
    actions.append(("Unblock internet", "unblock"))
else:
    actions.append(("Block internet", "block"))

if wifi_object:
    actions.append(("Disconnect from Wi-Fi", "kick"))

if reservation == "managed":
    actions.append(("Remove AutoPie static DHCP lease", "unreserve"))
elif reservation == "none" and ip:
    actions.append(("Reserve current IP with DHCP", "reserve"))


def clean(value):
    return (
        re.sub(r"\s+", " ", str(value))
        .replace(",", " ")
        .replace("=", "-")
        .strip()
    )


options = ",".join(
    f"{clean(label)}={value}"
    for label, value in actions
)

default = "ping" if ip else ("unblock" if blocked else "block")
connection = "Wi-Fi" if wifi_object else "LAN / unknown"

exports = {
    "DEVICE_HOSTNAME": hostname,
    "DEVICE_IP": ip,
    "DEVICE_WIFI_OBJECT": wifi_object,
    "DEVICE_REACHABLE": "yes" if reachable else "no",
    "DEVICE_BLOCKED": "yes" if blocked else "no",
    "DEVICE_RESERVATION": reservation,
    "DEVICE_CONNECTION": connection,
    "ACTION_OPTIONS": options,
    "ACTION_DEFAULT": default
}

for key, value in exports.items():
    print(f"export {key}={shlex.quote(str(value))}")
PYDEVICE
)"

printf 'Device: %s\nIP: %s\nMAC: %s\nConnection: %s\nReachable now: %s\nInternet blocked by AutoPie: %s\nDHCP reservation: %s\n' \
  "$DEVICE_HOSTNAME" \
  "${DEVICE_IP:-Unknown}" \
  "$DEVICE_MAC" \
  "$DEVICE_CONNECTION" \
  "$DEVICE_REACHABLE" \
  "$DEVICE_BLOCKED" \
  "$DEVICE_RESERVATION"
```

##### Step 3

- Path: `Download`
- Command slug: `openssh`

```sh
set -eo pipefail

case "$ACTION" in
  ping)
    [[ -n "$DEVICE_IP" ]] || {
      echo "This device does not currently have a known IP address."
      exit 1
    }

    router_ssh "ping -c '$PING_COUNT' '$DEVICE_IP'"
    ;;

  block)
    router_ssh \
      "MAC='$DEVICE_MAC' SRC_ZONE='$FIREWALL_SRC_ZONE' DEST_ZONE='$FIREWALL_DEST_ZONE' TARGET='$BLOCK_TARGET' sh -s" <<'REMOTE'
name="AutoPie Block $MAC"

if uci show firewall 2>/dev/null | grep -Fq ".name='$name'"; then
  echo "Device is already blocked by AutoPie."
  exit 0
fi

section="$(uci add firewall rule)"

uci set "firewall.$section.name=$name"
uci set "firewall.$section.src=$SRC_ZONE"
uci set "firewall.$section.dest=$DEST_ZONE"
uci set "firewall.$section.src_mac=$MAC"
uci set "firewall.$section.proto=all"
uci set "firewall.$section.target=$TARGET"
uci commit firewall
/etc/init.d/firewall reload

echo "Internet access blocked for $MAC."
REMOTE
    ;;

  unblock)
    router_ssh "MAC='$DEVICE_MAC' sh -s" <<'REMOTE'
name="AutoPie Block $MAC"
removed=0

while :; do
  ref="$(
    uci show firewall 2>/dev/null |
      grep -F ".name='$name'" |
      head -n 1 |
      sed 's/\.name=.*//'
  )"

  [ -n "$ref" ] || break

  uci delete "$ref"
  removed=1
done

if [ "$removed" -eq 1 ]; then
  uci commit firewall
  /etc/init.d/firewall reload
  echo "Internet access restored for $MAC."
else
  echo "No AutoPie block rule exists for $MAC."
fi
REMOTE
    ;;

  kick)
    [[ -n "$DEVICE_WIFI_OBJECT" ]] || {
      echo "The selected client is not currently associated with Wi-Fi."
      exit 1
    }

    router_ssh \
      "MAC='$DEVICE_MAC' OBJ='$DEVICE_WIFI_OBJECT' BAN_MS='$BAN_TIME_MS' sh -s" <<'REMOTE'
ubus call "$OBJ" del_client \
  "{\"addr\":\"$MAC\",\"reason\":5,\"deauth\":true,\"ban_time\":$BAN_MS}"

echo "Disconnected $MAC from $OBJ."
REMOTE
    ;;

  reserve)
    [[ "$RESERVED_IP" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]] || {
      echo "Enter a valid IPv4 address."
      exit 1
    }

    router_ssh "MAC='$DEVICE_MAC' IP='$RESERVED_IP' sh -s" <<'REMOTE'
if uci show dhcp 2>/dev/null | grep -Fiq ".mac='$MAC'"; then
  echo "A static DHCP lease already exists for $MAC."
  exit 1
fi

name="AutoPie Lease $MAC"
section="$(uci add dhcp host)"

uci set "dhcp.$section.name=$name"
uci set "dhcp.$section.mac=$MAC"
uci set "dhcp.$section.ip=$IP"
uci commit dhcp
/etc/init.d/dnsmasq restart

echo "Reserved $IP for $MAC."
REMOTE
    ;;

  unreserve)
    router_ssh "MAC='$DEVICE_MAC' sh -s" <<'REMOTE'
name="AutoPie Lease $MAC"
removed=0

while :; do
  ref="$(
    uci show dhcp 2>/dev/null |
      grep -F ".name='$name'" |
      head -n 1 |
      sed 's/\.name=.*//'
  )"

  [ -n "$ref" ] || break

  uci delete "$ref"
  removed=1
done

if [ "$removed" -eq 1 ]; then
  uci commit dhcp
  /etc/init.d/dnsmasq restart
  echo "Removed AutoPie static DHCP lease for $MAC."
else
  echo "No AutoPie-managed DHCP lease exists for $MAC."
fi
REMOTE
    ;;

  *)
    echo "Unsupported action: $ACTION"
    exit 1
    ;;
esac
```

#### Extras

| Step | Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Step 1 | ROUTER_HOST | STRING | yes | 192.168.1.1 | --internal-config | - | OpenWrt router hostname or IP address. |
| Step 1 | ROUTER_PORT | STRING | yes | 22 | --internal-config | - | SSH port. |
| Step 1 | ROUTER_USER | STRING | yes | root | --internal-config | - | SSH username. |
| Step 1 | AUTH_METHOD | SELECTABLE | no | password | --internal-config | Password=password, SSH key=key | Authentication method used to connect to OpenWrt. |
| Step 1 | ROUTER_PASSWORD | STRING | yes | - | --secret, --internal-config | - | SSH password. Stored in AutoPie's encrypted private preferences. |
| Step 1 | SSH_KEY_PATH | STRING | yes | ~/.ssh/id_ed25519 | --internal-config | - | Private SSH key inside AutoPie's Linux environment. |
| Step 1 | FIREWALL_SRC_ZONE | STRING | yes | lan | --internal-config | - | Source firewall zone used when blocking a device. |
| Step 1 | FIREWALL_DEST_ZONE | STRING | yes | wan | --internal-config | - | Destination firewall zone used when blocking a device. |
| Step 1 | CLIENT_SCOPE | SELECTABLE | no | online | - | Online clients=online, Wi-Fi clients=wifi, Wired clients=wired, All known clients=all | Which devices should be discovered. |
| Step 2 | DEVICE_MAC | SELECTABLE | yes | $$CLIENT_DEFAULT | --large | Discovered devices=$$CLIENT_OPTIONS | Clients discovered live from DHCP leases, neighbour state and Wi-Fi associations. |
| Step 3 | ACTION | SELECTABLE | yes | $$ACTION_DEFAULT | --large | Available actions=$$ACTION_OPTIONS | Actions are generated from the selected device's current state. |
| Step 3 | BLOCK_TARGET | SELECTABLE | no | REJECT | - | Reject immediately=REJECT, Drop silently=DROP | How the firewall should deny this device's WAN traffic. |
| Step 3 | BAN_TIME_MS | SELECTABLE | no | 10000 | - | Disconnect only=0, 10 seconds=10000, 1 minute=60000, 5 minutes=300000 | How long the Wi-Fi client should be prevented from immediately reconnecting. |
| Step 3 | RESERVED_IP | STRING | yes | $$DEVICE_IP | - | - | IPv4 address to reserve for this MAC address. |
| Step 3 | PING_COUNT | SLIDER | no | 1,3,10 | --int | - | Number of ICMP probes to send from the router. |
