### Hash Generator

Generate one or more hashes for a shared file, shared text, or text you enter.

#### Steps

##### Step 1

- Path: `default`
- Command slug: `python`

```sh
if [ -n "${INPUT:-}" ]; then
  export INPUT_PRESENT="yes"
else
  export INPUT_PRESENT="no"
fi
```

##### Step 2

- Path: `default`
- Command slug: `python`

```sh
set -e
OUTPUT="$(python - <<'PYHASH'
import hashlib
import json
import os
import sys

algorithms = {
    "md5": "MD5",
    "sha1": "SHA-1",
    "sha256": "SHA-256",
    "sha512": "SHA-512",
    "sha3_256": "SHA3-256",
    "blake2b": "BLAKE2b",
}
choice = os.environ.get("HASH_ALGORITHM", "all") or "all"
if choice not in ("all", *algorithms):
    sys.exit("Unsupported hash algorithm: " + choice)

active_input = os.environ.get("INPUT", "")
input_file = os.environ.get("INPUT_FILE", "")
path = input_file if input_file and os.path.isfile(input_file) else (
    active_input if active_input and os.path.isfile(active_input) else None
)
selected = algorithms if choice == "all" else {choice: algorithms[choice]}
hashers = {name: hashlib.new(name) for name in selected}

if path:
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            for hasher in hashers.values():
                hasher.update(block)
    title = "File hashes: " + os.path.basename(path)
else:
    text = (os.environ.get("INPUT_TEXT") or active_input) if active_input else os.environ.get("DATA", "")
    if not text:
        sys.exit("Share text or a file, or enter text to hash.")
    data = text.encode("utf-8")
    for hasher in hashers.values():
        hasher.update(data)
    title = "Text hashes (UTF-8)"

digests = {name: hasher.hexdigest() for name, hasher in hashers.items()}
items = [
    {"type": "text", "text": label + "\n" + digests[name]}
    for name, label in selected.items()
]
expected_hash = os.environ.get("EXPECTED_HASH", "").strip().lower()
if choice != "all" and expected_hash:
    matches = digests[choice] == expected_hash
    items.append({"type": "text", "text": "Match: " + ("true" if matches else "false")})

output = {"type": "list", "title": title, "items": items}
print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))
PYHASH
)"
export OUTPUT
am start -n com.autopi/.OutputPresentationActivity --es output "$OUTPUT" >/dev/null
```

- Flags: `--show-loading-screen-small`

#### Extras

| Step | Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Step 2 | HASH_ALGORITHM | SELECTABLE | no | all | - | All=all, MD5=md5, SHA-1=sha1, SHA-256=sha256, SHA-512=sha512, SHA3-256=sha3_256, BLAKE2b=blake2b | Generate all hashes or select one algorithm. |
| Step 2 | EXPECTED_HASH | STRING | no | - | - | - | Paste an expected hash to compare with the generated hash (optional). |
| Step 2 | INPUT_PRESENT | STRING | no | $$INPUT_PRESENT | --internal-config | - | Internal flag reflecting whether data was shared. |
| Step 2 | DATA | STRING | no | - | --multiline | - | Text to hash when no input was shared. |
