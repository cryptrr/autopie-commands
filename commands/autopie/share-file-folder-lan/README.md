### Share file/folder over LAN

Temporarily share a file or folder over the local network with an expiring HTTP link.

#### Command

- Path: `default`
- Command slug: ``

```sh
#@PYTHON
import functools
import http.server
import os
import re
import shutil
import signal
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.parse import quote


def die(message):
    print(f"Error: {message}", flush=True)
    raise SystemExit(1)


def command_output(*args):
    try:
        return subprocess.check_output(
            args,
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2,
        ).strip()
    except Exception:
        return ""


def get_lan_ip():
    # Prefer actual LAN interfaces so VPN/cellular routes don't win.
    for iface in ("wlan0", "wlan1", "eth0"):
        text = command_output(
            "ip", "-4", "-o", "addr", "show", "dev", iface
        )
        match = re.search(r"\binet\s+(\d+\.\d+\.\d+\.\d+)/", text)
        if match:
            return match.group(1)

    # Routing-table fallback.
    text = command_output("ip", "-4", "route", "get", "1.1.1.1")
    match = re.search(r"\bsrc\s+(\d+\.\d+\.\d+\.\d+)", text)
    if match:
        return match.group(1)

    # Socket fallback.
    for remote in ("192.0.2.1", "1.1.1.1", "8.8.8.8"):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect((remote, 80))
            ip = sock.getsockname()[0]
            if ip and not ip.startswith("127."):
                return ip
        except OSError:
            pass
        finally:
            sock.close()

    return None


def normalize_lan_hostname(value):
    value = (value or "").strip().lower().rstrip(".")

    if not value or value in {
        "localhost",
        "localhost.localdomain",
        "(none)",
        "null",
    }:
        return None

    if value.endswith(".lan"):
        value = value[:-4]

    value = re.sub(r"[^a-z0-9.-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-.")

    if not value:
        return None

    return f"{value}.lan"


def resolves_to(host, ip):
    try:
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(
                host,
                None,
                socket.AF_INET,
            )
        }
        return ip in addresses
    except OSError:
        return False


def find_lan_hostname(ip):
    candidates = []

    # OpenWrt/dnsmasq PTR record is the preferred source.
    try:
        candidates.append(socket.gethostbyaddr(ip)[0])
    except OSError:
        pass

    candidates.extend([
        command_output("getprop", "net.hostname"),
        command_output("hostname"),
        command_output("getprop", "persist.sys.device_name"),
        command_output("settings", "get", "global", "device_name"),
        socket.gethostname(),
    ])

    seen = set()

    for candidate in candidates:
        hostname = normalize_lan_hostname(candidate)

        if not hostname or hostname in seen:
            continue

        seen.add(hostname)

        # Don't publish a hostname that doesn't resolve to this phone.
        if resolves_to(hostname, ip):
            return hostname

    return None


# ---------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------

target_value = os.environ.get("INPUT_FILE", "").strip()
if not target_value:
    die("No file or folder received")

target = Path(target_value)
if not target.exists():
    die(f"Input does not exist: {target}")

try:
    expiry_seconds = int(os.environ.get("EXPIRY", "300"))
except ValueError:
    die("Invalid expiry")

if expiry_seconds <= 0:
    die("Expiry must be greater than zero")

url_mode = os.environ.get("URL_MODE", "hostname").strip().lower()


# ---------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------

lan_ip = get_lan_ip()
if not lan_ip:
    die("Could not determine LAN IPv4 address")

hostname = None

if url_mode == "hostname":
    hostname = find_lan_hostname(lan_ip)

    if hostname:
        url_host = hostname
    else:
        print("Hostname unavailable; falling back to IP", flush=True)
        url_host = lan_ip
else:
    url_host = lan_ip


# ---------------------------------------------------------------------
# Isolated share root
# ---------------------------------------------------------------------

state_dir = Path.home() / ".cache" / "autopie-lan-share"
state_dir.mkdir(parents=True, exist_ok=True)

share_root = Path(
    tempfile.mkdtemp(
        prefix="share-",
        dir=state_dir,
    )
)

name = target.name or "shared"
share_path = share_root / name

try:
    share_path.symlink_to(
        target.resolve(),
        target_is_directory=target.is_dir(),
    )
except Exception as exc:
    shutil.rmtree(share_root, ignore_errors=True)
    die(f"Could not prepare share: {exc}")


# ---------------------------------------------------------------------
# HTTP handler with byte-range support
# ---------------------------------------------------------------------

class RangeRequestHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print(
            f"[{self.client_address[0]}] {fmt % args}",
            flush=True,
        )

    def send_head(self):
        path = self.translate_path(self.path)

        # Let SimpleHTTPRequestHandler handle directories, redirects,
        # directory listings and errors normally.
        if not os.path.isfile(path):
            return super().send_head()

        try:
            file = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        try:
            stat = os.fstat(file.fileno())
            size = stat.st_size
            content_type = self.guess_type(path)

            range_header = self.headers.get("Range")
            start = 0
            end = size - 1
            partial = False

            if range_header:
                match = re.fullmatch(
                    r"bytes=(\d*)-(\d*)",
                    range_header.strip(),
                )

                if not match:
                    file.close()
                    self.send_error(416, "Invalid Range")
                    return None

                start_text, end_text = match.groups()

                if not start_text and not end_text:
                    file.close()
                    self.send_error(416, "Invalid Range")
                    return None

                if start_text:
                    start = int(start_text)

                    if end_text:
                        end = int(end_text)
                    else:
                        end = size - 1
                else:
                    # Suffix range: bytes=-500
                    suffix_length = int(end_text)

                    if suffix_length <= 0:
                        file.close()
                        self.send_error(416, "Invalid Range")
                        return None

                    suffix_length = min(suffix_length, size)
                    start = size - suffix_length
                    end = size - 1

                if start >= size or start < 0 or end < start:
                    file.close()
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return None

                end = min(end, size - 1)
                partial = True

            self._range_start = start
            self._range_end = end

            if partial:
                self.send_response(206)
                self.send_header(
                    "Content-Range",
                    f"bytes {start}-{end}/{size}",
                )
                content_length = end - start + 1
            else:
                self.send_response(200)
                content_length = size

            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(content_length))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header(
                "Last-Modified",
                self.date_time_string(stat.st_mtime),
            )
            self.end_headers()

            file.seek(start)
            return file

        except Exception:
            file.close()
            raise

    def copyfile(self, source, outputfile):
        start = getattr(self, "_range_start", 0)
        end = getattr(self, "_range_end", None)

        if end is None:
            return super().copyfile(source, outputfile)

        remaining = end - start + 1
        buffer_size = 1024 * 1024

        while remaining > 0:
            chunk = source.read(min(buffer_size, remaining))

            if not chunk:
                break

            try:
                outputfile.write(chunk)
            except (BrokenPipeError, ConnectionResetError):
                # Normal when mpv/VLC closes a probe/range request early.
                break

            remaining -= len(chunk)


class LANServer(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


handler = functools.partial(
    RangeRequestHandler,
    directory=str(share_root),
)

try:
    # Port 0 asks the kernel to assign a free port atomically.
    server = LANServer((lan_ip, 0), handler)
except OSError as exc:
    shutil.rmtree(share_root, ignore_errors=True)
    die(f"Could not start LAN server: {exc}")

port = server.server_address[1]


# ---------------------------------------------------------------------
# URL
# ---------------------------------------------------------------------

url = f"http://{url_host}:{port}/{quote(name, safe='')}"

if target.is_dir():
    url += "/"

print(f"Sharing: {target}", flush=True)
print(f"URL: {url}", flush=True)
print(f"LAN IP: {lan_ip}", flush=True)

if hostname:
    print(f"Hostname: {hostname}", flush=True)

print(f"Expires in: {expiry_seconds // 60} minute(s)", flush=True)
print("Server running...", flush=True)


# ---------------------------------------------------------------------
# Android share sheet
# ---------------------------------------------------------------------

subprocess.run(
    [
        "am",
        "start",
        "-a",
        "android.intent.action.SEND",
        "-t",
        "text/plain",
        "--es",
        "android.intent.extra.TEXT",
        url,
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    check=False,
)


# ---------------------------------------------------------------------
# Keep this AutoPie command alive until expiry / cancellation
# ---------------------------------------------------------------------

server.timeout = 1.0
expires_at = time.monotonic() + expiry_seconds
stopping = False


def stop_server(signum=None, frame=None):
    global stopping
    stopping = True


signal.signal(signal.SIGTERM, stop_server)
signal.signal(signal.SIGINT, stop_server)

try:
    while not stopping and time.monotonic() < expires_at:
        server.handle_request()
finally:
    server.server_close()
    shutil.rmtree(share_root, ignore_errors=True)

print("LAN share stopped", flush=True)

```

- Flags: `--show-loading-screen-small`

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| EXPIRY | SELECTABLE | yes | 300 | - | 5 minutes=300, 15 minutes=900, 30 minutes=1800, 1 hour=3600, 2 hours=7200, 4 hours=14400, 12 hours=43200, 24 hours=86400 | How long the LAN link should remain active. |
| URL_MODE | SELECTABLE | yes | hostname | - | Hostname (.lan)=hostname, IP address=ip | Choose the address used in the shared link. |
