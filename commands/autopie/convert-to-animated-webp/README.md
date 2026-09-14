### Convert to Animated WebP

Convert a video or animation into a looping 15 FPS animated WebP.

#### Command

- Path: `default`
- Command slug: `ffmpeg`
- Type: `SHARE`

```sh
ffmpeg -i "${INPUT_FILE}" -vf "fps=15,scale=600:-1:flags=lanczos" -c:v libwebp -loop 0 -an -preset default -quality 80 "${INPUT_FILE}-anim.webp"
```

#### Extras

No extras.
