### GitHub Stars

Fetch a GitHub repository's star count every 15 minutes for display in an Android widget.

The command prints the current star count as a plain number so it can be used directly as the widget value.

#### Command

- Path: `default`
- Command slug: ``
- Type: `CRON`
- Cron interval: `15m`

```sh
OUTPUT=$(curl -fsSL --max-time 10 "https://api.github.com/repos/${REPO}" | python -c 'import sys, json; print(json.load(sys.stdin)["stargazers_count"])')
export OUTPUT
printf '%s\n' "$OUTPUT"
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| REPO | STRING | yes | cryptrr/AutoPie | --internal-config | - | GitHub repository in owner/repo format |
