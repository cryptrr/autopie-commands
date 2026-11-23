### Changelog

#### 1.0.3

- Create the output directory explicitly and save QR codes there regardless of the shell working directory.

#### 1.0.2

- Save QR code images under `/storage/emulated/0/AutoPie/autopie.qr-code-generator/`.

#### 1.0.1

- Launch the output viewer using AutoPie's `OUTPUT_ACTIVITY` environment variable. Fall back to the legacy activity component on older AutoPie versions.

#### 1.0.0

- Generate a PNG QR code from shared text or a URL, save it in Downloads, and open it in AutoPie's output viewer.
