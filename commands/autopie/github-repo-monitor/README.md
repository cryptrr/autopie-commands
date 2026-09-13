### GitHub Repo Monitor

A 15-minute GitHub repository monitor cron designed for display as an Android widget.

#### Command

- Path: `default`
- Command slug: ``
- Type: `CRON`
- Cron interval: `15m`

```sh
#@PYTHON
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

repo = os.environ.get("REPO", "cryptrr/AutoPie").strip()
token = os.environ.get("GITHUB_TOKEN", "").strip()

headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "AutoPie-GitHub-Monitor"
}

if token:
    headers["Authorization"] = f"Bearer {token}"


def get_json(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.load(response)


repo_data = get_json(f"https://api.github.com/repos/{repo}")

issue_query = urllib.parse.quote(f"repo:{repo} is:issue is:open")
pr_query = urllib.parse.quote(f"repo:{repo} is:pr is:open")

issue_data = get_json(
    f"https://api.github.com/search/issues?q={issue_query}&per_page=1"
)

pr_data = get_json(
    f"https://api.github.com/search/issues?q={pr_query}&per_page=1"
)

runs_data = get_json(
    f"https://api.github.com/repos/{repo}/actions/runs?per_page=1"
)

runs = runs_data.get("workflow_runs", [])

if runs:
    run = runs[0]
    ci = {
        "name": run.get("name"),
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "branch": run.get("head_branch"),
        "event": run.get("event")
    }
else:
    ci = None

result = {
    "repo": repo,
    "stars": repo_data.get("stargazers_count", 0),
    "forks": repo_data.get("forks_count", 0),
    "open_issues": issue_data.get("total_count", 0),
    "open_prs": pr_data.get("total_count", 0),
    "checked": datetime.now().strftime("%H:%M:%S"),
    "ci": ci
}

output = json.dumps(result, separators=(",", ":"))

print(f'#@AUTOPIE {{"type":"output","value":{output}}}')

os.environ["OUTPUT"] = output
```

#### Extras

| Name | Type | Required | Default | Flags | Options | Details |
| --- | --- | --- | --- | --- | --- | --- |
| REPO | STRING | yes | cryptrr/AutoPie | --internal-config | - | GitHub repository in owner/repo format |
| GITHUB_TOKEN | STRING | yes | - | --password, --internal-config | - | Optional GitHub token for higher API limits and private repositories |
