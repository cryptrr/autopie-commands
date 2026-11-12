### Combine MP3 files

Combine two or more shared MP3 files into one file without re-encoding.

#### Command

- Path: `default`
- Command slug: ``
- Type: `SHARE`

```sh
set -e
if (( ${#INPUT_FILES_ARR[@]} < 2 )); then
  echo 'Share at least two MP3 files.' >&2
  exit 1
fi
list=$(mktemp)
trap 'rm -f "$list"' EXIT
for file in "${INPUT_FILES_ARR[@]}"; do
  [[ -f "$file" ]] || exit 1
  printf "file '%s'\n" "${file//\'/\'\\\'\'}" >> "$list"
done
first="${INPUT_FILES_ARR[0]}"
name="${first##*/}"
name="${name%.*}"
output="$DIRECTORY/${name}-combined-$RANDOM.mp3"
ffmpeg -hide_banner -loglevel error -n -f concat -safe 0 -i "$list" -c:a copy "$output"
export OUTPUT="$output"
printf 'Created: %s\n' "$output"
```

#### Extras

No extras.
