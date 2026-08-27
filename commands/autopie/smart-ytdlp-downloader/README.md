### Smart YT-DLP Downloader

Inspect a shared media URL, then download video, audio, subtitles, or a selected clip.

#### Steps

##### Step 1

- Path: `Download`
- Command slug: `smart-ytdlp-downloader`

```sh
set -euo pipefail

command -v yt-dlp >/dev/null 2>&1 || {
  echo "yt-dlp is not installed. Run: pip install -U yt-dlp"
  exit 1
}

command -v ffmpeg >/dev/null 2>&1 || {
  echo "ffmpeg is not installed. Run: pkg install ffmpeg"
  exit 1
}

export SOURCE_URL="$INPUT_URL"
export WORK_ROOT="$HOME/.cache/autopie-smart-ytdlp-$RAND"
mkdir -p "$WORK_ROOT"

INFO_JSON="$WORK_ROOT/info.json"

yt-dlp \
  --ignore-config \
  --dump-single-json \
  --no-playlist \
  --no-warnings \
  "$SOURCE_URL" > "$INFO_JSON"

eval "$(
python - "$INFO_JSON" <<'PYINFO'
import json
import math
import re
import shlex
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    info = json.load(f)

def clean(value, fallback="Unknown"):
    value = str(value or fallback)
    value = value.replace("\n", " ").replace("\r", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value or fallback

def option_label(value):
    return clean(value).replace(",", " ").replace("=", "-")

def safe_code(value):
    value = str(value or "")
    return value if re.fullmatch(r"[A-Za-z0-9._-]+", value) else ""

def export(name, value):
    print(f"export {name}={shlex.quote(str(value))}")

title = clean(info.get("title"), "Untitled media")
uploader = clean(
    info.get("uploader")
    or info.get("channel")
    or info.get("creator"),
    "Unknown uploader"
)
source = clean(
    info.get("extractor_key")
    or info.get("extractor")
    or info.get("webpage_url_domain"),
    "Unknown source"
)

duration_raw = info.get("duration") or 0
try:
    duration = max(0.0, float(duration_raw))
except (TypeError, ValueError):
    duration = 0.0

if duration:
    total = int(round(duration))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    duration_text = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
else:
    duration_text = "Live / unknown"

formats = info.get("formats") or []
heights = []

for fmt in formats:
    if fmt.get("vcodec") in (None, "none"):
        continue

    try:
        height = int(fmt.get("height") or 0)
    except (TypeError, ValueError):
        height = 0

    if height > 0:
        heights.append(height)

max_height = max(heights, default=0)
max_height_text = f"{max_height}p" if max_height else "Unknown"

quality = [("Best available", "best")]

for height, label in [
    (4320, "Up to 4320p (8K)"),
    (2160, "Up to 2160p (4K)"),
    (1440, "Up to 1440p"),
    (1080, "Up to 1080p"),
    (720, "Up to 720p"),
    (480, "Up to 480p"),
    (360, "Up to 360p")
]:
    if max_height >= height:
        quality.append((label, str(height)))

quality_options = ",".join(
    f"{option_label(label)}={value}"
    for label, value in quality
)

if max_height >= 1080:
    quality_default = "1080"
elif max_height >= 720:
    quality_default = "720"
elif max_height >= 480:
    quality_default = "480"
else:
    quality_default = "best"

subtitle_options = [("None", "none")]
manual = info.get("subtitles") or {}
automatic = info.get("automatic_captions") or {}

def subtitle_name(code, entries):
    if isinstance(entries, list):
        for entry in entries:
            if isinstance(entry, dict) and entry.get("name"):
                return clean(entry["name"], code)
    return code

def language_priority(code):
    lowered = code.lower()
    if lowered == "en":
        return (0, lowered)
    if lowered.startswith("en-"):
        return (1, lowered)
    return (2, lowered)

for raw_code in sorted(manual.keys(), key=language_priority):
    code = safe_code(raw_code)
    if not code or code == "live_chat":
        continue

    label = subtitle_name(code, manual.get(raw_code))
    subtitle_options.append(
        (f"{label} [{code}] - manual", f"manual|{code}")
    )

auto_codes = [
    code
    for code in sorted(automatic.keys(), key=language_priority)
    if code not in manual
]

for raw_code in auto_codes[:30]:
    code = safe_code(raw_code)
    if not code or code == "live_chat":
        continue

    label = subtitle_name(code, automatic.get(raw_code))
    subtitle_options.append(
        (f"{label} [{code}] - auto", f"auto|{code}")
    )

subtitle_options_value = ",".join(
    f"{option_label(label)}={value}"
    for label, value in subtitle_options
)

if duration >= 2:
    duration_seconds = max(2, int(math.ceil(duration)))
    clip_options = "Full media=full,Choose a clip=clip"
    trim_start_range = f"0,0,{duration_seconds}"
    trim_end_range = f"0,{duration_seconds},{duration_seconds}"
else:
    clip_options = "Full media=full"
    trim_start_range = "0,0,1"
    trim_end_range = "0,1,1"

export("MEDIA_TITLE", title)
export("MEDIA_UPLOADER", uploader)
export("MEDIA_SOURCE", source)
export("MEDIA_DURATION_TEXT", duration_text)
export("MEDIA_MAX_HEIGHT_TEXT", max_height_text)
export("QUALITY_OPTIONS", quality_options)
export("QUALITY_DEFAULT", quality_default)
export("SUBTITLE_OPTIONS", subtitle_options_value)
export("CLIP_OPTIONS", clip_options)
export("TRIM_START_RANGE", trim_start_range)
export("TRIM_END_RANGE", trim_end_range)
PYINFO
)"

printf 'Found: %s\nUploader: %s\nSource: %s\nDuration: %s\nMax video: %s\n' \
  "$MEDIA_TITLE" \
  "$MEDIA_UPLOADER" \
  "$MEDIA_SOURCE" \
  "$MEDIA_DURATION_TEXT" \
  "$MEDIA_MAX_HEIGHT_TEXT"
```

##### Step 2

- Path: `Download`
- Command slug: `smart-ytdlp-downloader`

```sh
set -euo pipefail

mkdir -p "$OUTPUT_FOLDER"

COMMON_ARGS=(
  --ignore-config
  --no-playlist
  --no-overwrites
  --newline
  --no-simulate
  -o "$OUTPUT_FOLDER/%(title).180B [%(id)s].%(ext)s"
)

FORMAT_ARGS=()

if [[ "$DOWNLOAD_TYPE" == "video" ]]; then
  if [[ "$QUALITY" == "best" ]]; then
    case "$VIDEO_CONTAINER" in
      mp4)
        FORMAT_SELECTOR='bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best'
        ;;
      webm)
        FORMAT_SELECTOR='bestvideo[ext=webm]+bestaudio[ext=webm]/bestvideo+bestaudio/best'
        ;;
      mkv)
        FORMAT_SELECTOR='bestvideo+bestaudio/best'
        ;;
      *)
        echo "Unsupported video container: $VIDEO_CONTAINER"
        exit 1
        ;;
    esac
  else
    case "$VIDEO_CONTAINER" in
      mp4)
        FORMAT_SELECTOR="bestvideo[ext=mp4][height<=$QUALITY]+bestaudio[ext=m4a]/bestvideo[height<=$QUALITY]+bestaudio/best[height<=$QUALITY]"
        ;;
      webm)
        FORMAT_SELECTOR="bestvideo[ext=webm][height<=$QUALITY]+bestaudio[ext=webm]/bestvideo[height<=$QUALITY]+bestaudio/best[height<=$QUALITY]"
        ;;
      mkv)
        FORMAT_SELECTOR="bestvideo[height<=$QUALITY]+bestaudio/best[height<=$QUALITY]"
        ;;
      *)
        echo "Unsupported video container: $VIDEO_CONTAINER"
        exit 1
        ;;
    esac
  fi

  FORMAT_ARGS=(
    -f "$FORMAT_SELECTOR"
    --merge-output-format "$VIDEO_CONTAINER"
  )
else
  FORMAT_ARGS=(
    -f "bestaudio/best"
    -x
    --audio-format "$AUDIO_FORMAT"
  )

  if [[ "$AUDIO_FORMAT" != "flac" ]]; then
    FORMAT_ARGS+=(--audio-quality "$AUDIO_QUALITY")
  fi
fi

SUBTITLE_ARGS=()

if [[ "$DOWNLOAD_TYPE" == "video" && "$SUBTITLE_CHOICE" != "none" ]]; then
  SUB_KIND="${SUBTITLE_CHOICE%%|*}"
  SUB_LANG="${SUBTITLE_CHOICE#*|}"

  if [[ "$SUB_KIND" == "manual" ]]; then
    SUBTITLE_ARGS=(
      --write-subs
      --sub-langs "$SUB_LANG"
      --sub-format "srt/best"
      --embed-subs
    )
  elif [[ "$SUB_KIND" == "auto" ]]; then
    SUBTITLE_ARGS=(
      --write-auto-subs
      --sub-langs "$SUB_LANG"
      --sub-format "srt/best"
      --embed-subs
    )
  fi
fi

CLIP_ARGS=()

if [[ "$CLIP_MODE" == "clip" ]]; then
  if (( CLIP_END <= CLIP_START )); then
    echo "Clip End must be greater than Clip Start."
    exit 1
  fi

  CLIP_ARGS=(
    --download-sections "*${CLIP_START}-${CLIP_END}"
  )
fi

POST_ARGS=()

if [[ -n "$EMBED_METADATA" ]]; then
  POST_ARGS+=("$EMBED_METADATA")
fi

if [[ -n "$EMBED_THUMBNAIL" ]]; then
  POST_ARGS+=("$EMBED_THUMBNAIL")
fi

if [[ -n "$EMBED_CHAPTERS" ]]; then
  POST_ARGS+=("$EMBED_CHAPTERS")
fi

if [[ -n "$REMOVE_SPONSORS" ]]; then
  POST_ARGS+=(--sponsorblock-remove "$REMOVE_SPONSORS")
fi

PATH_FILE="$WORK_ROOT/final-path.txt"
rm -f -- "$PATH_FILE"

yt-dlp \
  "${COMMON_ARGS[@]}" \
  "${FORMAT_ARGS[@]}" \
  "${SUBTITLE_ARGS[@]}" \
  "${CLIP_ARGS[@]}" \
  "${POST_ARGS[@]}" \
  --print-to-file "after_move:filepath" "$PATH_FILE" \
  "$SOURCE_URL"

[[ -s "$PATH_FILE" ]] || {
  echo "Download completed but the output path could not be determined."
  exit 1
}

DOWNLOADED_FILE="$(tail -n 1 "$PATH_FILE")"

[[ -f "$DOWNLOADED_FILE" ]] || {
  echo "Downloaded file not found: $DOWNLOADED_FILE"
  exit 1
}

export OUTPUT="$DOWNLOADED_FILE"

printf 'Downloaded successfully\nTitle: %s\nUploader: %s\nSaved: %s\n' \
  "$MEDIA_TITLE" \
  "$MEDIA_UPLOADER" \
  "$OUTPUT"

rm -rf -- "$WORK_ROOT"
```

- Flags: `--show-loading-screen`

#### Extras

| Step | Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Step 2 | OUTPUT_FOLDER | STRING | no | Download/AutoPie | --internal-config, --folder-picker | - | Folder where the downloaded media will be saved. |
| Step 2 | DOWNLOAD_TYPE | SELECTABLE | no | video | - | Video=video, Audio only=audio | Download as video or extract audio only. |
| Step 2 | QUALITY | SELECTABLE | no | $$QUALITY_DEFAULT | - | Available resolutions=$$QUALITY_OPTIONS | Resolution choices are generated from the inspected media. |
| Step 2 | VIDEO_CONTAINER | SELECTABLE | no | mp4 | - | MP4=mp4, MKV=mkv, WebM=webm | MP4 gives the widest compatibility. MKV accepts almost any source streams. |
| Step 2 | AUDIO_FORMAT | SELECTABLE | no | mp3 | - | MP3=mp3, M4A / AAC=m4a, Opus=opus, FLAC=flac | Output format for audio-only downloads. |
| Step 2 | AUDIO_QUALITY | SELECTABLE | no | 192K | - | 128 kbps=128K, 192 kbps=192K, 320 kbps=320K | Target bitrate for lossy audio formats. |
| Step 2 | SUBTITLE_CHOICE | SELECTABLE | no | none | - | Available subtitles=$$SUBTITLE_OPTIONS | Manual and automatic subtitle languages are discovered from the URL. |
| Step 2 | CLIP_MODE | SELECTABLE | no | full | - | Available clip modes=$$CLIP_OPTIONS | Download the full media or only a selected section. |
| Step 2 | CLIP_START | SLIDER | no | $$TRIM_START_RANGE | --int, --large | - | Clip start position in seconds. |
| Step 2 | CLIP_END | SLIDER | no | $$TRIM_END_RANGE | --int, --large | - | Clip end position in seconds. |
| Step 2 | EMBED_METADATA | FLAG | no | --embed-metadata | - | - | Embed title, uploader and other available metadata. |
| Step 2 | EMBED_THUMBNAIL | FLAG | no | --embed-thumbnail | - | - | Embed the source thumbnail as cover art when supported. |
| Step 2 | EMBED_CHAPTERS | FLAG | no | --embed-chapters | - | - | Preserve chapter markers when the source provides them. |
| Step 2 | REMOVE_SPONSORS | FLAG | no | default | - | - | Remove SponsorBlock segments on supported sites. |
