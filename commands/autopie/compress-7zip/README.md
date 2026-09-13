### Compress with 7-Zip

Compress files or a folder into a configurable 7z or ZIP archive.

#### Steps

##### Step 1

- Path: `default`
- Command slug: `7z`

```sh
set -e

if [[ -d "$INPUT" ]]; then
  IS_FOLDER=true
  SOURCE_COUNT=1
  SOURCE_PARENT="$(dirname "$INPUT")"
  BASE_NAME="$(basename "$INPUT")"
else
  IS_FOLDER=false
  SOURCE_COUNT="${#INPUT_FILES_ARR[@]}"

  if [[ "$SOURCE_COUNT" -eq 0 ]]; then
    echo "No files or folder provided"
    exit 1
  fi

  SOURCE_PARENT="$(dirname "${INPUT_FILES_ARR[0]}")"
  BASE_NAME="$FILENAME_NO_EXT"
fi

export IS_FOLDER
export SOURCE_COUNT
export SOURCE_PARENT
export ARCHIVE_BASENAME="$BASE_NAME"

echo "Ready to compress $SOURCE_COUNT item(s)"

if [[ "$IS_FOLDER" == "true" ]]; then
  echo " • $INPUT"
else
  printf ' • %s\n' "${INPUT_FILES_ARR[@]}"
fi
```

##### Step 2

- Path: `default`
- Command slug: `7z`

```sh
set -e

case "$FORMAT" in
  7z)
    EXT="7z"
    ;;
  zip)
    EXT="zip"
    ;;
  *)
    echo "Unsupported archive format: $FORMAT"
    exit 1
    ;;
esac

OUTPUT_DIR="${OUTPUT_FOLDER:-$SOURCE_PARENT}"
mkdir -p "$OUTPUT_DIR"

FINAL_NAME="$ARCHIVE_NAME"

case "$FINAL_NAME" in
  *.$EXT) ;;
  *) FINAL_NAME="$FINAL_NAME.$EXT" ;;
esac

ARCHIVE_PATH="$OUTPUT_DIR/$FINAL_NAME"

if [[ -e "$ARCHIVE_PATH" ]]; then
  ARCHIVE_PATH="$OUTPUT_DIR/${FINAL_NAME%.$EXT}-${RAND}.$EXT"
fi

ARGS=(a -t"$FORMAT" -mx="$LEVEL" -y)

if [[ "$ENABLE_ENCRYPTION" == "true" ]]; then
  if [[ -z "$PASSWORD" ]]; then
    echo "Encryption enabled but no password provided"
    exit 1
  fi

  ARGS+=("-p$PASSWORD")

  if [[ "$FORMAT" == "7z" && "$ENCRYPT_FILENAMES" == "true" ]]; then
    ARGS+=(-mhe=on)
  fi
fi

if [[ -n "$SPLIT_SIZE" ]]; then
  ARGS+=("-v$SPLIT_SIZE")
fi

echo "Compressing $SOURCE_COUNT item(s)..."
echo "Output: $ARCHIVE_PATH"

if [[ "$IS_FOLDER" == "true" ]]; then
  7z "${ARGS[@]}" "$ARCHIVE_PATH" "$INPUT"
else
  7z "${ARGS[@]}" "$ARCHIVE_PATH" "${INPUT_FILES_ARR[@]}"
fi

export OUTPUT="$ARCHIVE_PATH"

echo
echo "Created: $ARCHIVE_PATH"
printf '#@AUTOPIE {"type":"output","value":"%s"}\n' "$ARCHIVE_PATH"
```

#### Extras

| Step   | Name              | Type            | Required | Default            | Flags           | Options                                                                                  | Details                                               |
| ------ | ----------------- | --------------- | -------- | ------------------ | --------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Step 2 | FORMAT            | SELECTABLE_FLAT | no       | 7z                 | -               | 7z — Best compression=7z, ZIP — Maximum compatibility=zip                                | Archive format                                        |
| Step 2 | LEVEL             | SELECTABLE      | no       | 5                  | -               | Store — No compression=0, Fastest=1, Fast=3, Normal=5, Maximum=7, Ultra=9                | Compression level                                     |
| Step 2 | ARCHIVE_NAME      | STRING          | yes      | $$ARCHIVE_BASENAME | --large         | -                                                                                        | Archive filename. Extension is added automatically.   |
| Step 2 | ENABLE_ENCRYPTION | BOOLEAN         | no       | False              | -               | -                                                                                        | Password protect the archive                          |
| Step 2 | PASSWORD          | STRING          | yes      | -                  | --password      | -                                                                                        | Archive password                                      |
| Step 2 | ENCRYPT_FILENAMES | BOOLEAN         | no       | True               | -               | -                                                                                        | Encrypt filenames inside the archive                  |
| Step 2 | SPLIT_SIZE        | SELECTABLE      | no       | -                  | -               | No splitting=, 10 MB=10m, 50 MB=50m, 100 MB=100m, 500 MB=500m, 1 GB=1g, 2 GB=2g, 4 GB=4g | Optionally split the archive into volumes             |
| Step 2 | OUTPUT_FOLDER     | STRING          | no       | -                  | --folder-picker | -                                                                                        | Leave empty to save next to the selected file/folder. |
