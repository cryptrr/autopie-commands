### FFMPEG: Convert to HEVC

Convert a shared video to HEVC (H.265) MP4 with configurable quality, encoding speed, and audio.

#### Command

- Path: `default`
- Command slug: `ffmpeg`
- Type: `SHARE`

```sh
set -eu

input=${INPUT_FILE:-}
if [ ! -f "$input" ] || [ ! -r "$input" ]; then
  printf '%s\n' 'Share a readable video file to convert.' >&2
  exit 1
fi
case "$input" in
  /*) ;;
  *) input="$PWD/$input" ;;
esac

crf=${CRF:-24}
case "$crf" in
  [0-9]|[1-4][0-9]|50|51) ;;
  *) printf '%s\n' 'CRF must be an integer from 0 to 51.' >&2; exit 1 ;;
esac
preset=${PRESET:-medium}
case "$preset" in
  ultrafast|superfast|veryfast|faster|fast|medium|slow|slower|veryslow) ;;
  *) printf '%s\n' 'Choose a supported encoding speed preset.' >&2; exit 1 ;;
esac
audio=${AUDIO_MODE:-aac}
case "$audio" in
  aac) set -- -map '0:a?' -c:a aac -b:a 192k ;;
  copy) set -- -map '0:a?' -c:a copy ;;
  none) set -- -an ;;
  *) printf '%s\n' 'Audio mode must be aac, copy, or none.' >&2; exit 1 ;;
esac

directory=${input%/*}
filename=${input##*/}
stem=${filename%.*}
[ -n "$stem" ] || stem=$filename
suffix=${RAND:-$$}
case "$suffix" in
  *[!a-zA-Z0-9_-]*) printf '%s\n' 'Invalid output filename suffix.' >&2; exit 1 ;;
esac
output="$directory/$stem-hevc-$suffix.mp4"
if [ -e "$output" ] || [ -L "$output" ]; then
  printf 'Output already exists; run again for a new name: %s\n' "$output" >&2
  exit 1
fi

# Uppercase V selects real video, excluding attached cover images.
# Pad odd dimensions for chroma subsampling without resizing the picture.
ffmpeg -hide_banner -nostdin -n -i "$input" \
  -map '0:V:0' "$@" -map_metadata 0 -map_chapters 0 \
  -c:v libx265 -crf "$crf" -preset "$preset" \
  -vf 'pad=ceil(iw/2)*2:ceil(ih/2)*2' \
  -tag:v hvc1 -movflags +faststart "$output"

OUTPUT=$output
export OUTPUT
printf 'Created: %s\n' "$OUTPUT"
```

- Flags: `--show-loading-screen-small`

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| CRF | SLIDER | yes | 0,24,51 | --int | - | Video quality (0–51). Lower values retain more quality and usually produce larger files. Default: 24. |
| PRESET | SELECTABLE | yes | medium | - | ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, ... | Slower presets usually compress better but take longer and use more CPU. Software HEVC encoding can be slow on a phone. |
| AUDIO_MODE | SELECTABLE | yes | aac | - | AAC (compatible)=aac, Copy original audio=copy, Remove audio=none | AAC converts all audio tracks at 192 kb/s each for MP4 playback. Copy keeps the original audio without quality loss but requires MP4-compatible codecs. Remove creates a silent video. Inputs without audio also work. The first video and all audio tracks are included; subtitles and attachments are omitted. |
