### PDF to Text

Extract embedded PDF text into a UTF-8 file beside the PDF, with optional layout preservation.

#### Command

- Path: `default`
- Command slug: `pdftotext`
- Type: `SHARE`

```sh
set -e
src="$INPUT_FILE"
if [[ -z "$src" || ! -f "$src" ]]; then
  echo "Share or select a PDF file in AutoPie."
  exit 1
fi
if [[ "${src,,}" != *.pdf ]]; then
  echo "The selected file is not a PDF."
  exit 1
fi
if ! command -v pdftotext >/dev/null 2>&1; then
  echo "Missing Poppler. Install with: pkg install poppler"
  exit 1
fi

dir="$(dirname -- "$src")"
file="$(basename -- "$src")"
stem="${file%.*}"
out="$dir/$stem.txt"
if [[ -e "$out" ]]; then
  out="$dir/$stem-$RAND.txt"
fi

args=(-enc UTF-8 -nopgbrk)
if [[ "$LAYOUT" == "preserve" ]]; then
  args+=(-layout)
fi
if ! pdftotext "${args[@]}" "$src" "$out"; then
  rm -f -- "$out"
  echo "PDF text extraction failed."
  exit 1
fi
if [[ ! -s "$out" ]]; then
  rm -f -- "$out"
  echo "No embedded text found. Scanned PDFs require OCR."
  exit 1
fi
export OUTPUT="$out"
printf 'Saved: %s\n\nText preview (first 80 lines):\n' "$out"
sed -n '1,80p' "$out"
```

- Flags: `--show-loading-screen-small`

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| LAYOUT | SELECTABLE | yes | reading | - | Reading order=reading, Preserve layout=preserve | Text extraction mode |
