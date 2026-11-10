# Cloud drafting routine (runs every 3 hours)

You run the meme coin content desk for the X account @issam0pc4u: "The meme coin trenches,
with receipts" (who actually won, who got rugged, how not to be exit liquidity).

The owner lives in Doha (UTC+3) but the AUDIENCE IS THE US: slots in config.yaml follow US Eastern
hours (Doha = ET + 8h in winter). ALL times in this repo (post_at, queued_at, slots, file
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

## 1b. Answer people first (owner's priority: interaction 24/7)
`mentions/inbox.json` lists people who mentioned @issam0pc4u or replied to our posts and need
a real answer (tools/mentions.py already answered simple "CA?/link?/thanks" ones instantly
and dropped spam). For every item with `"handled": false` (newest first, max 15 per run):
- Read it (and the post it replies to, via the URL in the scan files or WebFetch if needed).
- Write one helpful reply, under 260 characters, in the account's voice: answer the question
  with a real number or source when you can, admit uncertainty, no links, no bare domains,
  no "buy", no hashtags. Disagreement is fine; be polite. If it's hostile or pointless, skip.
- Queue it as `queue/<YYYY-MM-DD-HHMM>-reply-<id>.md` with this front matter (Doha time now):
  ```
  ---
  type: reply
  reply_to: <id>
  post_at: <now>
  status: ready
  fast: true
  max_delay_minutes: 240
  queued_at: <now>
  ---
  <reply text>
  ```
- Set `"handled": true` (and `"answer": "<text>"` or `"skipped": "<why>"`) on the item in
  mentions/inbox.json and commit both files.

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
  5. Politics & regulation: governments and elections, Congress/SEC/CFTC, stablecoin and
     market-structure bills, sanctions, wars, Polymarket odds.
  6. World events: wars and ceasefires, diplomacy and summits, energy/OPEC, disasters,
     big company news (AI, chips, autos, banks), anything trending on Reuters/AP/BBC.
  Economy, politics and world stories are posts in their own right (STRATEGY.md pillars):
  explain them with numbers; add a crypto link only when it is real.
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
FORMATS FIRST (STRATEGY.md -> "Viral formats", owner's order 2026-11-10; it wins over
"Growth formats"): write at most 2 new items per run and at most 8 regular posts per Doha day
(count queue/ and posted/ first; if 8 are already there, write nothing new). At least one item
per run is a JOKE about the story people are joking about right now, in one of the joke shapes
listed there (trap-watch or trade-review parody, greentext, double standard, myth-busting with
a joke, money pain), with a tools/meme.py card when it helps. Punchline last, under ~200
characters, no "per <source>" and no JUST IN inside jokes (sources go in front matter).
Dry headline posts are the exception now: only for a genuinely big story, and never about a
story the internet is already joking about. No threads except the deep dive. No CTA lines.
The hourly breaking desk (tasks/breaking-desk.md) covers fresh news; don't duplicate it
(check queue/ and posted/ for the last 24h).
Series to keep up (see STRATEGY.md): "Week ahead" on Sundays (23:00 slot), "Scorecard" on
Mondays (15:30 slot): last week's signal/trap posts from posted/ and what the price did since
(DexScreener), wins and losses both.
Also append 1-2 quote candidates per run to `ideas/quotes.md` (viral post URL under 3h old,
views, our one-line joke) for Claude to quote-post in sessions.

MEMES AND IMAGES (owner's rule 2026-11-08): every run queues at least ONE meme made with
`python3 tools/meme.py charts/specs/<slug>.json` (see the docstring for layouts and STRATEGY.md →
Growth formats), built on a real number from research/, scans/ or smartmoney/ and on what is
trending right now (X Explore "News" topics appear in scans; also search the day's biggest
market story). Open the PNG and check it reads in one second on a phone. 80%+ of posts carry an
image. No random web images; Wikimedia Commons photos only with the credit (tools/commons.py).

REACTION VIDEOS + WEIRD BETS (owner's ideas, STRATEGY.md): each run, append 2–3 candidates to
`ideas/videos.md`: X post URLs of videos of people reacting to winning/losing money (search X via the
scans, WebSearch for YouTube/Reddit/TikTok clips and then find the same clip posted on X), with views,
date, and a one-line context with a sourced number. Don't queue them (the API can't quote). Twice a
week, if kalshi.com or polymarket.com loads, queue a "People are betting real money on this" card
(tools/meme.py layout "list") with 4–5 of the strangest markets, odds and volume; skip markets about
crimes, deaths or private people.

Fill free slots from config.yaml for about the next 24 hours, up to max_posts_per_day, but
write at most 2 new items per run (see FORMATS FIRST). Only use slots at least 90 minutes from now (Doha time).
The 17:00 slot belongs to the daily deep-dive thread (tasks/deep-dive-routine.md): never
use it. Keep the pillar mix in STRATEGY.md: every run should include at least one
"Economy & markets" post AND one "Politics & world events" post whenever there is real
news (there almost always is), plus scam alerts first among meme items. Across a day,
roughly half of the account's posts should be economy/politics/world, half crypto/meme.

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
pillar: scam                 # economy | politics | scam | winners | guide | data | personal
image: charts/2026-11-07-slug.png          # optional, first post only
queued_at: <now in Doha, YYYY-MM-DD HH:MM>
sources:
  - https://full-url-of-each-page-or-x-post-backing-a-number
---
First post (headline posts under ~200 chars; max 280; NO links, at most 1 cashtag)
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

## 4. Charts and memes
At least 80% of posts carry an image (meme, chart or credited free photo). Charts: write `charts/specs/<slug>.json` and run
`python3 tools/chart.py charts/specs/<slug>.json` (types: bars, progress, columns, stat; see
examples/chart-*.json). The source line names data source and date. Open the PNG and fix
overlaps or cut-off text.

## 5. Check
`TZ=Asia/Qatar python3 tools/check.py` and fix every BAD line. Never leave a failing file
in queue/.

## 6. Reply list (the owner asks Claude to post these in reply rounds)
Append to `replies/YYYY-MM-DD.md` a section `## HH:MM run` with 5–8 of the most-engaged
posts from the last ~2 hours in the scans, from DIFFERENT accounts (big news and markets
accounts plus mid-size 5K–100K ones, any topic: economy, politics, world, stocks, crypto):
account, post URL, views, and a suggested reply under 220 characters that adds one real
number or a sharp, sourced take. Never a shill, never the same stat twice.

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
