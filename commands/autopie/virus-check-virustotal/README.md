### Virus Check (VirusTotal)

Calculate a file's SHA-256 hash and open its existing VirusTotal report.

#### Command

- Path: `default`
- Command slug: ``
- Type: `SHARE`

```sh
#@SHELL
set -euo pipefail

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Usage: $0 <file>"
    exit 1
fi

HASH=$(sha256sum "$INPUT_FILE" | awk '{print $1}')
URL="https://www.virustotal.com/gui/file/$HASH"

echo "SHA-256: $HASH"
echo "Opening: $URL"

am start \
    -a android.intent.action.VIEW \
    -d "$URL"
```

- Flags: `--show-loading-screen`

#### Extras

No extras.
