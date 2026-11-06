# X system for @issam0pc4u

```
 every 4h (Claude scheduled task "X: research & queue posts")
   research news + data → write sourced posts → make charts → queue/   + replies/<date>.md
                                                                 │
 every 15 min (background job, poster.py)                        ▼
   due + waited 60 min + passes checks + under 4/day → post to X API → posted/ + analytics/posts.csv
                                                                 │
 Sundays (tasks/weekly-analysis.md)                              ▼
   read your post stats in Chrome → analytics/week-*.md → updates STRATEGY.md → better drafts
```

## One-time setup

1. **X API keys.** Go to developer.x.com, create a Project + App, set App permissions to
   **Read and write**, then generate the Access Token and Secret. Copy `.env.example`
   to `.env` and paste the 4 keys. Until `.env` has keys, everything runs as a dry run.
2. **Start the background poster** (runs every 15 minutes while your Mac is awake):
   ```bash
   cp "/Users/issam/Claude/Projects/social media/x-system/com.issam0pc4u.xposter.plist" ~/Library/LaunchAgents/ && launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.issam0pc4u.xposter.plist
   ```
   Stop it any time:
   ```bash
   launchctl bootout gui/$(id -u)/com.issam0pc4u.xposter
   ```
3. Keep the Claude app open for the drafting task (if it's closed, the run happens next
   time you open it). A sleeping Mac posts nothing: set it to not sleep while plugged in.

## Daily use

- **See what's coming:** `.venv/bin/python tools/poster.py --status`
- **Stop a post:** open it in `queue/` and set `status: hold`, or delete the file.
  Every post waits at least 60 minutes in the queue before it can go out.
- **Review everything first instead:** set `mode: approve` in `config.yaml`; then only
  posts you change to `status: approved` go out.
- **Pause all posting:** set `dry_run: true` in `config.yaml`.
- **Replies:** open `replies/<today>.md` and spend 20–30 min replying by hand.
- **Add your own post:** copy `examples/post-example.md` into `queue/`, edit, then run
  `.venv/bin/python tools/check.py`.
- **Make a chart:** copy a spec from `examples/`, edit, run
  `.venv/bin/python tools/chart.py charts/specs/<name>.json`.

## Files

| Path | What |
|---|---|
| `STRATEGY.md` | Voice, pillars, rules, cadence, learnings. The drafting task follows it. |
| `config.yaml` | Mode, limits, time slots. |
| `queue/` | Posts waiting to go out. `failed/` holds ones X rejected (+ `.error.txt`). |
| `posted/` | What went out, with tweet IDs. |
| `analytics/` | `posts.csv`, `followers.csv`, weekly reports. |
| `replies/` | Reply targets for manual replies. |
| `watchlist.yaml` | Verified legit meme coin accounts; `repost_ok` decides what may be quoted/reposted. |
| `scans/` | What the scanner found on X each run (`tools/scan.py`, $0.005 per post read, daily cap in config). |
| `logs/api_spend.csv` | Every scanner read and its cost. |
| `logs/poster.log` | What the poster did and when. |
