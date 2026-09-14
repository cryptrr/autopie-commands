### Rotate Video

Rotate a video clockwise by 90, 180, or 270 degrees while preserving its audio.

#### Command

- Path: `default`
- Command slug: `ffmpeg`
- Type: `SHARE`

```sh
ffmpeg -i ${INPUT_FILE} -vf "$( \
    case $ROTATE in \
        90) echo 'transpose=1';; \
        180) echo 'transpose=2,transpose=2';; \
        270) echo 'transpose=3';; \
    esac)" -c:a copy ${INPUT_FILE}.rotated.mp4
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| ROTATE | SELECTABLE | yes | 90 | - | 90, 180, 270 | Degrees to rotate (clockwise) |
