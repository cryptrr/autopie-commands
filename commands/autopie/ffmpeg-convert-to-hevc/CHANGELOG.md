### Changelog

#### 1.1.0

- Fix the encoder: use `libx265` to produce HEVC/H.265 instead of H.264.
- Add validated quality (CRF 0–51), encoding speed, and audio controls, with defaults of CRF 24, medium speed, and AAC at 192 kb/s per track.
- Support copying MP4-compatible audio or removing audio, and accept videos without audio.
- Encode the first non-cover video stream, preserve all audio tracks unless removed, and omit subtitles and attachments. Copy source metadata and chapters.
- Add the `hvc1` tag and fast-start MP4 layout for playback support. HEVC decoding support is still required.
- Pad odd frame dimensions to even dimensions without scaling. Let FFmpeg negotiate pixel format rather than forcing 8-bit conversion.
- Validate shared input and settings, quote file paths, and save beside the source as `<name>-hevc-<RAND>.mp4` (falling back to the process ID when RAND is unavailable).
- Refuse to overwrite any existing output or source file and report the created path.

#### 1.0.0

- Initial manifest import from `default.json`.
