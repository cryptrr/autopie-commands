### Check Internet Archive

AutoPie command for Check Internet Archive

#### Command

- Path: `default`
- Command slug: ``

```sh
#@PYTHON
#@OPEN_LOGS

import os
import sys
import subprocess
import json
import urllib.parse
import urllib.request

def latest_wayback_snapshot(url: str) -> str | None:
    api = "https://archive.org/wayback/available"
    query = urllib.parse.urlencode({"url": url})
    api_url = f"{api}?{query}"

    with urllib.request.urlopen(api_url, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))

    snapshot = data.get("archived_snapshots", {}).get("closest")
    if snapshot and snapshot.get("available"):
        return snapshot.get("url")

    return None



def main():
    
    url = os.getenv("INPUT_URL")
    print("CHECKING...", flush=True)
    snapshot_url = latest_wayback_snapshot(url)

    if snapshot_url:
        print(snapshot_url)
        subprocess.run([
            "am",
            "start",
            "-a",
            "android.intent.action.VIEW",
            "-d",
            snapshot_url,
        ], stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    else:
        print("No snapshot found", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

```

#### Extras

No extras.
