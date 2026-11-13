### Image Format Converter

Convert a shared image to PNG, JPG, WebP, AVIF, GIF, BMP, TIFF, or ICO and save it to Downloads.

#### Command

- Path: `Download`
- Command slug: `magick`
- Type: `SHARE`

```sh
input=${INPUT_FILE:-}
if [ ! -f "$input" ] || [ ! -r "$input" ]; then
  printf '%s\n' 'Share a readable image file to convert.' >&2
  exit 1
fi

format=${OUTPUT_FORMAT:-png}
case "$format" in
  png|jpg|webp|avif|gif|bmp|tiff|ico) ;;
  *) printf 'Unsupported output format: %s\n' "$format" >&2; exit 1 ;;
esac

output=$(mktemp --suffix=".$format" ./converted-XXXXXXXX) || exit 1
case "$format" in
  jpg) set -- -background white -alpha remove -alpha off ;;
  ico) set -- -resize '256x256>' ;;
  *) set -- ;;
esac

# Read through stdin so ImageMagick treats the shared path as a literal file.
source='-[0]'
case "$input" in
  *.[iI][cC][oO]) source='ico:-[0]' ;;
esac
if ! magick "$source" -auto-orient "$@" "$format:$output" < "$input" || [ ! -s "$output" ]; then
  rm -f "$output"
  printf 'Could not convert the shared image to %s.\n' "$format" >&2
  exit 1
fi

OUTPUT="${PWD}/${output#./}"
export OUTPUT
printf '%s\n' "$OUTPUT"
```

- Flags: `--show-loading-screen-small`

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| OUTPUT_FORMAT | SELECTABLE | yes | png | - | PNG=png, JPG=jpg, WebP=webp, AVIF=avif, GIF=gif, BMP=bmp, TIFF=tiff, ICO=ico | Choose the output format. Animated and multi-page inputs use the first frame or page. JPG replaces transparency with white. ICO scales large images to fit within 256 × 256 pixels. |
