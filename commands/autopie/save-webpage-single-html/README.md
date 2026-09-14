### Save Webpage as Single HTML

Save a shared webpage and its assets as one portable HTML file named from the page title.

#### Command

- Path: `Download`
- Command slug: ``
- Type: `SHARE`

```sh
TITLE=$(
  curl -Ls --max-time 15 "$INPUT_URL" |
    python -c 'import sys,re,html; s=sys.stdin.read(); m=re.search(r"<title[^>]*>(.*?)</title>", s, re.I|re.S); print(html.unescape(re.sub(r"\s+", " ", m.group(1))).strip() if m else "")'
)

[ -n "$TITLE" ] || TITLE="webpage"

FILENAME=$(
  printf '%s' "$TITLE" |
    sed 's#[/:*?"<>|]#-#g; s/[[:space:]][[:space:]]*/ /g; s/^ *//; s/ *$//' |
    cut -c1-120
)

[ -n "$FILENAME" ] || FILENAME="webpage"

OUTPUT_FILE="$FILENAME.html"
monolith "$INPUT_URL" -o "$OUTPUT_FILE"

OUTPUT="$OUTPUT_FILE"
export OUTPUT
printf '%s\n' "$OUTPUT_FILE"
```

#### Extras

No extras.
