### JSON - YAML - TOML Converter

Convert shared JSON, YAML, or TOML with editable source text and live format controls.

#### Steps

##### Step 1

- Path: `default`
- Command slug: `python`

```sh
#@SHELL
# Preserve input before a multistage step replaces INPUT.
export SOURCE_SEED=''
export SOURCE_EXTENSION=''
if [[ -n "${INPUT_FILE:-}" && -f "$INPUT_FILE" ]]; then
  export SOURCE_EXTENSION="${INPUT_FILE##*.}"
  export SOURCE_SEED="$(cat -- "$INPUT_FILE")"
elif [[ -n "${INPUT_TEXT:-}" ]]; then
  export SOURCE_SEED="$INPUT_TEXT"
elif [[ -n "${INPUT:-}" && -f "$INPUT" ]]; then
  export SOURCE_EXTENSION="${INPUT##*.}"
  export SOURCE_SEED="$(cat -- "$INPUT")"
elif [[ -n "${INPUT:-}" && ! -d "$INPUT" ]]; then
  export SOURCE_SEED="$INPUT"
fi
export SOURCE_EDITOR="$SOURCE_SEED"
export FROM_FORMAT=auto
export TO_FORMAT=yaml
export JSON_INDENT=2
# Function persists across stages and realtime reruns in AutoPie's shared shell.
autopie_convert_document() {
  python - <<'PY_CONVERTER'
import os
import json
import math
import datetime

try:
    import yaml
    import tomlkit
except ImportError as exc:
    print('Missing dependency: ' + str(exc) + '. Run: pip install pyyaml tomlkit')
    raise SystemExit(0)

text = os.environ.get('SOURCE_EDITOR', '').lstrip('\ufeff')
source = os.environ.get('FROM_FORMAT', 'auto').lower()
target = os.environ.get('TO_FORMAT', 'yaml').lower()
extension = os.environ.get('SOURCE_EXTENSION', '').lower()

if not text.strip():
    print('')
    raise SystemExit(0)

def load(data, fmt):
    if fmt == 'json':
        return json.loads(data, parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Invalid JSON constant ' + x)))
    if fmt == 'yaml':
        documents = list(yaml.safe_load_all(data))
        if len(documents) != 1:
            raise ValueError('Expected exactly one YAML document')
        return documents[0]
    if fmt == 'toml':
        return tomlkit.parse(data).unwrap()
    raise ValueError('Unknown source format: ' + fmt)

def normalize(value):
    if isinstance(value, dict):
        result = {}
        for key, val in value.items():
            if not isinstance(key, str):
                raise ValueError('Non-string map key: ' + repr(key))
            result[key] = normalize(val)
        return result
    if isinstance(value, (list, tuple)):
        return [normalize(x) for x in value]
    if isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
        return value.isoformat()
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError('NaN/Infinity cannot be represented reliably')
        return value
    raise ValueError('Unsupported data type: ' + type(value).__name__)

def check_toml(value, location='root'):
    if value is None:
        raise ValueError('TOML cannot represent null at ' + location)
    if isinstance(value, dict):
        for key, v in value.items():
            check_toml(v, location + '.' + key)
    if isinstance(value, list):
        for i, v in enumerate(value):
            check_toml(v, location + '[' + str(i) + ']')

try:
    if source == 'auto':
        hint = {'json':'json','yaml':'yaml','yml':'yaml','toml':'toml'}.get(extension)
        formats = ([hint] if hint else []) + [fmt for fmt in ('json','toml','yaml') if fmt != hint]
    else:
        formats = [source]
    errors = []
    for fmt in formats:
        try:
            value = normalize(load(text, fmt))
            break
        except Exception as exc:
            errors.append(fmt.upper() + ': ' + str(exc))
    else:
        raise ValueError('Unable to parse input. ' + ' | '.join(errors))

    if target == 'json':
        spaces = int(os.environ.get('JSON_INDENT', '2'))
        result = json.dumps(value, indent=spaces, ensure_ascii=False, allow_nan=False)
    elif target == 'yaml':
        result = yaml.safe_dump(value, sort_keys=False, allow_unicode=True, default_flow_style=False).rstrip('\n')
    elif target == 'toml':
        if not isinstance(value, dict):
            raise ValueError('TOML requires an object at the root')
        check_toml(value)
        result = tomlkit.dumps(value).rstrip('\n')
    else:
        raise ValueError('Unknown target format: ' + target)
    print(result)
except Exception as exc:
    print('Conversion error: ' + str(exc))
PY_CONVERTER
}
export CONVERTED_TEXT="$(autopie_convert_document)"
```

##### Step 2

- Path: `default`
- Command slug: `python`

```sh
#@SHELL
export CONVERTED_TEXT="$(autopie_convert_document)"
export OUTPUT="$CONVERTED_TEXT"
```

#### Extras

| Step | Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Step 2 | FROM_FORMAT | SELECTABLE | no | auto | --realtime | Auto detect=auto, JSON=json, YAML=yaml, TOML=toml | Choose the input format, or detect it automatically. |
| Step 2 | TO_FORMAT | SELECTABLE | no | yaml | --realtime | JSON=json, YAML=yaml, TOML=toml | Format of the live converted result. |
| Step 2 | JSON_INDENT | SELECTABLE | no | 2 | --realtime | 2 spaces=2, 4 spaces=4 | Indentation used for JSON output. |
| Step 2 | SOURCE_EDITOR | STRING | yes | $$SOURCE_SEED | --multiline, --realtime | - | Edit or paste your source text; updates conversion live. |
| Step 2 | RESULT_TEXT | STRING | no | $$CONVERTED_TEXT | --multiline, --realtime | - | Converted result. |
