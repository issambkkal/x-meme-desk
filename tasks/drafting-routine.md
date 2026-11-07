# Cloud drafting routine (runs every 3 hours)

You run the meme coin content desk for the X account @issam0pc4u: "The meme coin trenches,
with receipts" (who actually won, who got rugged, how not to be exit liquidity).

The owner lives in Doha (UTC+3). ALL times in this repo (post_at, queued_at, slots, file
names) are Doha local time. Get it with: `TZ=Asia/Qatar date '+%Y-%m-%d %H:%M'`.
The owner wants the account active around the clock: never leave the next 12 hours of
slots empty.

You work in a checkout of the GitHub repo issambkkal/x-meme-desk. GitHub Actions
(`.github/workflows/poster.yml`) publishes due files from `queue/` every 5 minutes, and
`scanner.yml` searches X for the watchlist accounts and writes `scans/`. You have NO X API
keys: never try to post, reply, like or follow on X, and never run tools/scan.py.

## 0. Setup
- `git pull --rebase origin main`
- `pip install -q -r requirements.txt` (python3)

## 1. Load context (read first)
- `STRATEGY.md`: voice, pillars, naming-coins rules, format rules, truth rules, cadence,
  Learnings. Follow it exactly; it overrides anything below.
- `config.yaml` (mode, slots, limits) and `watchlist.yaml` (legit accounts, repost_ok flags).
- Everything in `queue/`, `failed/` (read any .error.txt and fix the cause), the newest 30
  files in `posted/*.json`, and the end of `logs/poster.log`. Never repeat a topic, coin or
  number posted in the last 7 days.
- `TZ=Asia/Qatar python3 tools/poster.py --status` shows what is queued.
- Re-read queued posts due in the next 12 hours: if the story moved on (a teased name was
  revealed, a number changed, "today" is no longer true), edit the post or set `status: hold`.

## 2. Research (be thorough: at least 8 searches and 6 full articles read per run)
- Read today's and yesterday's `scans/YYYY-MM-DD.md` (alerts, news AND macro groups) and
  the last 2 days of `research/*.md` (earlier runs' notes and the event calendar).
- Search the last ~6 hours across ALL of these (WebSearch; use mode "extended" when
  standard results are thin, old or generic):
  1. Meme coins: rugs, exploits, insider/bundled launches, big winners and losers,
     Pump.fun/launchpad data, CoinGecko meme category moves.
  2. Crypto market: BTC/ETH/SOL, ETF flows, stablecoins, liquidations, funding.
  3. Global economy & finance: Fed and central banks, CPI/jobs/PMIs, yields, dollar, oil,
     stocks, AI/tech selloffs.
  4. Industry & trade: factories, tariffs, China/US data, supply chains, energy, chips.
  5. Politics & regulation: Congress/SEC/CFTC, stablecoin and market-structure bills,
     elections, sanctions, wars, Polymarket odds.
  For every macro item, find the crypto link with data (what BTC/SOL/meme coins did).
- Prefer primary sources (BLS, Fed, NBS China, ISM, Farside, CoinGlass, CoinGecko, SEC,
  Congress.gov), watchlist sleuths and on-chain tools (Bubblemaps, Arkham, Dune,
  DexScreener), and major outlets (Reuters, Bloomberg, FT, WSJ, CoinDesk, The Block).
- WebFetch and read in full every page you will cite (X post URLs from the scan files count
  as sources). Confirm each number. Breaking claims need two sources, or a watchlist
  sleuth plus the on-chain evidence they link.
- Append what you learned to `research/YYYY-MM-DD.md` under `## HH:MM run`: bullet facts
  (number, date, source URL), including ones you didn't post, plus any dated upcoming
  events under `## Calendar`. Later runs and the daily deep-dive build on this notebook.

## 3. Queue posts
Fill free slots from config.yaml for about the next 24 hours, up to max_posts_per_day, but
write at most 3 new items per run. Only use slots at least 90 minutes from now (Doha time).
The 17:00 slot belongs to the daily deep-dive thread (tasks/deep-dive-routine.md): never
use it. Keep the pillar mix in STRATEGY.md: every run should include at least one
"Macro → crypto" post if there is real news, and scam alerts first among meme items.

Telegram growth (owner's priority): once per Doha day, queue ONE post that invites people
to the free Telegram group imbi MOON, built on a real, checkable example from
`smartmoney/signals.json`, `smartmoney/trades/` or `posted/*-trap-*.md` / `*-green-*.md`
(e.g. "Yesterday my bot flagged X as a trap at +260%; it's now -40%"). Check the current
price on DexScreener before claiming what happened. Say "link in my pinned post"; never
paste the t.me link (the API charges $0.20 for a link). Don't write signal or trap-watch
posts yourself: tools/x_signals.py queues those automatically from the tracker
(files named *-green-*.md / *-trap-*.md, up to 3 + 2 a day); leave them alone.
Before a scheduled data release (CPI, jobs, FOMC, PMI), queue a short heads-up post.
On Mondays and Thursdays, if no service post is queued for that day, queue one "open for
work" post in the 15:30 slot as described in SERVICES.md (pillar: services; no links).

One file per item: `queue/YYYY-MM-DD-HHMM-short-slug.md`:

```
---
post_at: 2026-11-07 09:00
status: ready                # "draft" instead if config mode is approve
pillar: scam                 # scam | macro | winners | guide | data | personal
image: charts/2026-11-07-slug.png          # optional, first post only
queued_at: <now in Doha, YYYY-MM-DD HH:MM>
sources:
  - https://full-url-of-each-page-or-x-post-backing-a-number
---
First post (max 280 chars, NO links, at most 1 cashtag)
===
Optional 2nd post of a thread
[image: charts/other.png]
```

- NEVER use a `quote:` field: the X API refuses to quote other accounts (403). Credit
  sources with an @mention in the text ("Per @bubblemaps, ...") and add our own angle.
- Don't write "today"/"tonight" unless the post goes out the same day; use the weekday.
- Reposts (max 1 new per run, max_reposts_per_day in config): only a repost_ok account's
  scam/rug/exploit alert or hard data. Format: front matter with `type: repost`,
  `repost: https://x.com/<user>/status/<id>`, post_at at least 70 minutes from now,
  status, queued_at; empty body. If failed/ shows reposts are refused (403), stop
  queueing them and say so.
- Naming rules: only call a coin a scam/rug/insider play if a credible source said so, and
  credit them. Never post contract addresses, buy links or "this will pump" calls.
  Personal-pillar posts must not invent the owner's trades or life events.

## 4. Charts
At least half of posts carry a chart: write `charts/specs/<slug>.json` and run
`python3 tools/chart.py charts/specs/<slug>.json` (types: bars, progress, columns, stat; see
examples/chart-*.json). The source line names data source and date. Open the PNG and fix
overlaps or cut-off text.

## 5. Check
`TZ=Asia/Qatar python3 tools/check.py` and fix every BAD line. Never leave a failing file
in queue/.

## 6. Reply list (the owner posts these by hand or asks Claude to)
Append to `replies/YYYY-MM-DD.md` a section `## HH:MM run` with 3–5 of the most-engaged
fresh posts from the scans (watchlist accounts, especially sleuths and big traders):
account, post URL, and a suggested reply under 200 characters that adds a number, a red
flag or a sharp take, never a shill.

## 7. Save
```
git add -A
git commit -m "desk: <Doha time> <n> posts queued"
git pull --rebase origin main && git push origin HEAD:main
```
Retry the pull/push up to 3 times if it is rejected. Commit straight to main; no branches
or pull requests.

## 8. Finish
Reply with 3–5 lines: items queued (time, type, first line), charts made, anything skipped
or fixed and why.
