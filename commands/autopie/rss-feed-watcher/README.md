### RSS Feed Watcher

Watch RSS and Atom feeds every 15 minutes and send notifications for new entries. Tapping a notification opens the article URL.

The first run creates a baseline by default, so existing entries do not generate notifications. Enable `FIRST_RUN_NOTIFY` to notify for matching entries already present when the watcher first runs.

Include and exclude keywords are case-insensitive and match against entry titles and descriptions. Exclusions always take priority.

#### Command

- Path: `default`
- Command slug: ``
- Type: `CRON`
- Cron interval: `15m`

#### Extras

| Name | Type | Required | Default | Details |
| --- | --- | --- | --- | --- |
| `FEED_URLS` | STRING | yes | - | RSS or Atom feed URLs separated by commas or new lines. |
| `INCLUDE_KEYWORDS` | STRING | no | - | Notify only for entries containing any or all configured keywords. |
| `EXCLUDE_KEYWORDS` | STRING | no | - | Ignore entries containing any configured keyword. |
| `KEYWORD_MATCH_MODE` | SELECTABLE | yes | `any` | Match any or all include keywords. |
| `FIRST_RUN_NOTIFY` | BOOLEAN | no | `false` | Notify for matching existing entries during the first run. |
| `MAX_NOTIFICATIONS` | SLIDER | no | `10` | Limit article notifications per run from 1 to 50. |

#### State

The watcher stores up to 500 seen entry IDs in `~/.cache/autopie-rss-watcher/state.json`. Entries rejected by filters are still marked as seen and will not notify after filter changes.

#### Dependencies

- Python
- feedparser
- requests
