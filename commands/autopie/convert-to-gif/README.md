### Convert to GIF

Convert a selected portion of a video into a scaled 15 FPS GIF.

#### Command

- Path: `default`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -ss ${START} ${END:+-t $END} -vf "fps=15,scale=480:-1:flags=lanczos" -c:v gif "${INPUT_FILE}.gif"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| START | STRING | yes | 00:00:00 | - | - | - |
| END | STRING | no | - | - | - | - |
