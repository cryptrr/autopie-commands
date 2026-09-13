Designed to send notifications when SSH logins or failures are detected.

### SSH Login Monitor

#### Command

- Path: `default`
- Command slug: ``
- Type: `CRON`
- Cron interval: `15m`

```sh
#@PYTHON
import os
import json
import hashlib
import subprocess
from pathlib import Path

HOST = os.environ.get("SSH_HOST", "").strip()
USER = os.environ.get("SSH_USER", "").strip()
PORT = os.environ.get("SSH_PORT", "22").strip()
AUTH_MODE = os.environ.get("SSH_AUTH_MODE", "key").strip()
PASSWORD = os.environ.get("SSH_PASSWORD", "")
KEY = os.path.expanduser(os.environ.get("SSH_KEY", "~/.ssh/id_ed25519").strip())

if not HOST or not USER:
    raise SystemExit("SSH_HOST and SSH_USER are required")

TARGET = f"{USER}@{HOST}"

state_dir = Path.home() / ".cache" / "autopie" / "ssh-login-monitor"
state_dir.mkdir(parents=True, exist_ok=True)

server_id = hashlib.sha256(
    f"{TARGET}:{PORT}".encode()
).hexdigest()[:16]

state_file = state_dir / f"{server_id}.json"

remote_command = r'''printf '__AUTOPIE_CONNECTION__ %s\n' "$SSH_CONNECTION"

journalctl _COMM=sshd \
    --no-pager \
    -n 1000 \
    -o short-iso \
    -q 2>/dev/null |
grep -E 'Accepted (password|publickey|keyboard-interactive)|Failed (password|publickey|keyboard-interactive)|Invalid user|authentication failure' || true
'''

ssh_args = [
    "ssh",
    "-p", PORT,
    "-o", "ConnectTimeout=10",
    "-o", "ConnectionAttempts=1",
    "-o", "ServerAliveInterval=10",
    "-o", "ServerAliveCountMax=1",
    "-o", "StrictHostKeyChecking=accept-new",
]

run_env = os.environ.copy()

if AUTH_MODE == "password":
    if not PASSWORD:
        raise SystemExit("SSH_PASSWORD is required")

    run_env["SSHPASS"] = PASSWORD

    cmd = [
        "sshpass", "-e",
        *ssh_args,
        "-o", "PreferredAuthentications=password,keyboard-interactive",
        "-o", "PubkeyAuthentication=no",
        TARGET,
        remote_command,
    ]
else:
    cmd = [
        *ssh_args,
        "-i", KEY,
        "-o", "BatchMode=yes",
        "-o", "PreferredAuthentications=publickey",
        TARGET,
        remote_command,
    ]

try:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        env=run_env,
    )
except subprocess.TimeoutExpired:
    print(f"SSH monitor timed out connecting to {TARGET}")
    raise SystemExit(1)
except Exception as e:
    print(f"SSH monitor error: {e}")
    raise SystemExit(1)

if result.returncode != 0:
    print(result.stderr.strip() or "SSH connection failed")
    raise SystemExit(result.returncode)

raw_lines = [
    line.strip()
    for line in result.stdout.splitlines()
    if line.strip()
]

connection_line = None
journal_lines = []

for line in raw_lines:
    if line.startswith("__AUTOPIE_CONNECTION__ "):
        connection_line = line
    else:
        journal_lines.append(line)

if not connection_line:
    raise SystemExit("Could not determine SSH client IP")

parts = connection_line.split()

# __AUTOPIE_CONNECTION__ client_ip client_port server_ip server_port
if len(parts) < 5:
    raise SystemExit(f"Invalid SSH_CONNECTION: {connection_line}")

client_ip = parts[1]

# ---------------------------------------------------------
# Ignore ALL SSH authentication events from AutoPie's IP.
# ---------------------------------------------------------
filtered_lines = []

for line in journal_lines:
    if f"from {client_ip} " in line:
        continue

    filtered_lines.append(line)


def event_hash(line):
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


current_events = [
    {
        "id": event_hash(line),
        "line": line,
    }
    for line in filtered_lines
]

# First run establishes baseline.
if not state_file.exists():
    initial_ids = [event["id"] for event in current_events]

    state_file.write_text(json.dumps({
        "seen": initial_ids[-2000:]
    }))

    print(
        f"SSH monitor initialized for {TARGET}. "
        f"Ignoring SSH events from {client_ip}."
    )
    raise SystemExit(0)

try:
    state = json.loads(state_file.read_text())
    seen_list = state.get("seen", [])
    seen = set(seen_list)
except Exception:
    seen_list = []
    seen = set()

new_events = [
    event
    for event in current_events
    if event["id"] not in seen
]

updated_seen = list(seen_list)
updated_set = set(updated_seen)

for event in current_events:
    if event["id"] not in updated_set:
        updated_seen.append(event["id"])
        updated_set.add(event["id"])

updated_seen = updated_seen[-2000:]

state_file.write_text(json.dumps({
    "seen": updated_seen
}))

if not new_events:
    print(
        f"No new SSH login attempts on {HOST} "
        f"(ignoring {client_ip})"
    )
    raise SystemExit(0)

successful = []
failed = []

for event in new_events:
    line = event["line"]

    if "Accepted " in line:
        successful.append(line)
    else:
        failed.append(line)


def notify(title, body):
    print("#@AUTOPIE " + json.dumps({
        "type": "notification",
        "title": title,
        "body": body,
    }))


if successful:
    body = "\n".join(successful[-5:])

    if len(successful) > 5:
        body += f"\n\n+{len(successful) - 5} more successful logins"

    notify(
        f"SSH Login • {HOST}",
        body,
    )

if failed:
    body = "\n".join(failed[-5:])

    if len(failed) > 5:
        body += f"\n\n+{len(failed) - 5} more failed attempts"

    notify(
        f"SSH Login Failed • {HOST}",
        body,
    )

print(
    f"{TARGET}: {len(successful)} successful, "
    f"{len(failed)} failed new SSH events. "
    f"Ignoring source IP {client_ip}."
)
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| SSH_HOST | STRING | yes | 192.168.1.132 | --internal-config | - | Server hostname or IP address |
| SSH_USER | STRING | yes | amal | --internal-config | - | SSH user AutoPie uses to connect |
| SSH_PORT | STRING | yes | 22 | --internal-config | - | SSH server port |
| SSH_AUTH_MODE | SELECTABLE | yes | password | --internal-config | SSH Key=key, Password=password | Authentication method |
| SSH_KEY | STRING | yes | ~/.ssh/id_ed25519 | --internal-config | - | Private key path |
| SSH_PASSWORD | STRING | yes | - | --secret, --internal-config | - | SSH password |
