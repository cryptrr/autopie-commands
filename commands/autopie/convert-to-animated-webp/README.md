# Convert to Animated WebP

AutoPie command for Convert to Animated WebP

## Command

- Path: `default`
- Command slug: `ffmpeg`

```sh
ffmpeg -i "${INPUT_FILE}" -vf "fps=15,scale=600:-1:flags=lanczos" -c:v libwebp -loop 0 -an -preset default -quality 80 "${INPUT_FILE}-anim.webp"
```

## Extras

No extras.
