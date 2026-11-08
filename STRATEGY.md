# @issam0pc4u — X strategy (meme coins + economy + politics + world events)

The drafting task reads this file before every run. The weekly analysis updates the
**Learnings** section. Edit anything here and the system follows it from the next run.

## Positioning

**"The meme coin trenches, with receipts — and the world that moves them."** Who actually
won, who got rugged, how to not be the exit liquidity, and how the global economy,
finance, industry and politics push money into and out of crypto and meme coins.
Every claim backed by on-chain data or a named source.

The owner's rule (2026-11-07): the account is NOT only crypto. Politics, the economy and
big world events are core topics in their own right: elections and governments, wars and
diplomacy, sanctions and trade, central banks, inflation and jobs, stocks and big
companies, oil and energy, AI and tech. Cover them every day with numbers and sources;
connect them to crypto only when the link is real, never forced.

The edge: most meme accounts only look at charts; most macro accounts ignore meme coins.
We connect them: "Fed cut odds fell → dollar up → risk-off → meme coins bled first."

- Voice: first person, plain words, short lines, dry humour, a bit cynical about hype.
  Never shill, never "100x gem", never tell anyone to buy a coin. Not financial advice.
- Every post gives the reader one of: a number they didn't know, a chart that makes it
  obvious, a red flag they can check themselves, or a take they can argue with.

## Content pillars (aim for this mix each week)

| Pillar | Share | Example |
|---|---|---|
| Economy & markets | 25% | Fed, ECB, CPI, jobs, yields, the dollar, oil, gold, stock indexes, big company earnings, AI/tech, trade, factories/PMIs. "US productivity +3.5% in Q3 while unit labor costs fell 0.7%: what that means for rate cuts." Crypto angle only if real. |
| Politics & world events | 20% | Elections, Congress/government decisions, wars and ceasefires, sanctions, summits, tariffs, regulation, disasters that move energy or supply chains. Explain what happened, the numbers, what it changes for money and people, what's next (dates). Neutral and factual. |
| Scam alert / red flags | 20% | "Bubblemaps: 40% of $XYZ supply sat in 12 linked wallets before launch. Here's how to check any coin in 30 seconds." |
| Winners & smart money, with receipts | 15% | Tracker data, whale moves, "a wallet turned $285 into $627K... here's how many lost". (Signal/trap posts from tools/x_signals.py count here.) |
| Survival guide / trenches data | 15% | "5 checks before you ape", Pump fun survival rate, liquidations, platform revenue. |
| Personal / community | 5% | "Be honest: how many meme coins have you bought this year?" |

Politics rules: report, don't campaign. No cheering for a party or politician, no insults,
no unverified claims. Use primary sources (official statements, vote records, Reuters/AP,
government data), give both sides when something is contested, and focus on what changes
for money, prices, markets and ordinary people.

## Growth formats (owner approved 2026-11-08 — HOW we post; pillars above are WHAT)

X's open-sourced ranking (xai-org/x-algorithm, param.rs) scores each post by predicted actions:
copy-link share 20, reply 5, quote 5, DM share 5, follow-from-post 4, repost 1, like 0.7,
and punishes "not interested" −53, mute −59, block −31, report −234. Posts older than 48h
drop out; non-followers see us less; repeated posts from one author in a feed are discounted.
The accounts winning in our niches (Spectator Index, Kobeissi, Watcher Guru, Unusual Whales)
post one short headline with one striking number, minutes after the news, often with a chart.

Mix every day:

| Format | Share | Rules |
|---|---|---|
| Headline post | 60% | Starts `BREAKING:` / `JUST IN:` / `RECORD:` / `NEW:` (only when it is genuinely new, <3h old) or a plain one-line fact. ONE striking number + ONE line on why it matters. Under ~200 characters, single post, no thread. Credit the source in words ("per Reuters", "per @bubblemaps"). |
| Shareable chart / data | 25% | Something people save or send: rankings, record comparisons, "who's buying", scoreboards. Chart attached. Line 1 states the finding. |
| Question | 10% | Starts an argument people answer: "Long or short from here?", "Which breaks first: oil at $110 or BTC at $70K?", "Rate hike in December: yes or no?" One fact + the question. |
| Telegram / community CTA | 5% | At most one a day (the drafting routine's invite post) plus the automatic signal/trap posts. Never add a CTA line to ordinary posts. |

- Threads only for the daily deep dive, and its FIRST post must work alone as a headline post.
- Never post the same story twice in 24h unless there is a real update (say "UPDATE:").
- Space posts out (60+ minutes): back-to-back posts from us get discounted in feeds.
- Low-value, repetitive or clickbait posts earn "not interested"/mute, which costs far more
  than a like earns. If a post would not make someone stop scrolling, don't post it.

Recurring series (people follow for a dependable thing):
- **Smart money today** — the daily report thread (18:30 Doha = 10:30am ET).
- **Trap of the day** — the automatic trap post from tools/x_signals.py.
- **Week ahead** (Sunday 23:00 Doha = 3pm ET Sunday): the dates that move markets next week, chart.
- **Scorecard** (Monday 15:30 Doha): last week's signals and traps, what happened since, wins AND losses.

## Breaking desk

`tasks/breaking-desk.md` runs every hour in US hours (15:00–05:00 Doha). It queues 0–2
headline posts with `fast: true` and `max_delay_minutes: 90` about news from the last ~2 hours.
Fast beats perfect, but the truth rules below still apply: two sources or one wire/official source.

## Daily deep-dive article (one per day, 07:00 Doha research → 17:00 thread)

Every day one researched article in `articles/YYYY-MM-DD-slug.md` (900–1,500 words,
12+ sources, every number cited), on the biggest story that links the world to crypto:
e.g. "Why meme coins died this week: the dollar, the AI selloff and a $1.27B liquidation".
Structure: hook · what happened (numbers) · why (macro/politics/industry chain) · what
on-chain data shows · who won / who lost · what to watch next week (dates) · sources.
It goes out on X as a 6–10 post thread at 17:00 Doha (9:00am ET), with 1–3 charts. Post 1 must
stand alone as a headline post (one number, under ~200 characters). The full text stays in the repo.

## Research depth (non-negotiable)

- Read the full article for every source you cite (WebFetch), not just search snippets.
- For any macro claim, get the official or primary number (BLS, Fed, ECB, PBoC, NBS China,
  Caixin/S&P PMI, EIA, Treasury, SEC/Congress.gov, company filings) plus one major outlet.
- Always answer "so what?" with data: for markets (stocks, oil, dollar, yields), for people
  (prices, jobs, rates), and for crypto when the link is real (BTC/ETH/SOL moves, ETF flows,
  stablecoin supply, liquidations). Don't force a crypto angle onto a politics or economy story.
- Track the economic calendar (CPI, PPI, jobs, FOMC, PMIs, China data, big elections or
  votes, token unlocks) and write a heads-up post before, and a result post after.

Quote posts are NOT possible: the X API refuses to quote other accounts (403). Instead write
our own post crediting the source ("per @bubblemaps") and add a number, chart or lesson.

## Naming coins (strict)

- Only call a specific coin a scam, rug or insider play if a credible source said so
  (sleuths in watchlist.yaml, on-chain tools like Bubblemaps/Arkham, or major media).
  Say who found it: "per @bubblemaps", "ZachXBT reported". Never accuse on our own guess.
- Never post a contract address, a buy link, or a "this one will pump" call.
- A "winner" post is about what happened, with the source. Never imply the reader can
  repeat it. Add the odds (e.g. survival rates) when possible.

## Format rules

- Max 280 characters per post (config max_chars). Headline posts under ~200. Hook in line 1.
- At most 2 emojis. Cashtags ($WIF) are fine; X API allows only ONE per post (a 403 stopped the Nov 7 thread).
- No links anywhere in posts: the API charges $0.20 instead of $0.015, and X shows link
  posts to fewer people. Name the source in words; the URL goes in `sources`.
- No referral links until 1,000+ followers; then one disclosed referral in the bio only.
- Tips: never add the wallet address to normal posts. It appears in the bio, the pinned
  post, and automatically as the last post of each daily deep-dive thread (`tip: true`).
  See MONEY.md for the full earning plan.
- Charts: 1600×900 dark style via `tools/chart.py`. At least half of posts carry one.

## Truth rules (non-negotiable)

- Every number in a post appears in the file's `sources` with a URL (X post URLs count).
- Breaking claims (hacks, rugs, arrests, exploits) need two independent sources, or one
  sleuth in watchlist.yaml plus on-chain evidence they link to.
- If sources disagree, use the conservative number or skip.
- Never invent quotes, wallets, trades or personal events.

## Cadence

- Up to 12 posts a day, 60+ minutes apart, in US hours. Slots (Doha = ET + 8h):
  15:30, 17:00, 18:30, 20:00, 21:30, 23:00, 00:30, 02:00, 04:00 (7:30am–8pm ET).
  17:00 is reserved for the daily deep-dive thread. Breaking-desk posts go out between slots.
- Up to 2 automatic reposts a day, only from `repost_ok: true` accounts, only scam
  alerts or hard data.
- Replies under strangers' posts are done in the browser in "reply rounds" the owner asks
  for (tasks/reply-rounds.md), ideally 3 a day: ~16:30, ~20:00, ~00:00 Doha (8:30am, noon,
  4pm ET). Replies to people who mention us are automatic (tools/mentions.py + drafting routine).

## Learnings (updated weekly from real numbers)

- 2026-11-06 baseline: 45 posts, 5 followers. Best post: personal joke about losing money
  on a meme coin (27 views). News/data posts: 4–15 views. 17 posts in ~70 minutes on
  Nov 6 competed with each other.
- 2026-11-06: switched focus from general crypto/markets to meme coins.
- 2026-11-07: owner wants deeper research and the global economy/finance/industry/politics
  angle on every big crypto move; added macro pillar and the daily deep-dive article.
- 2026-11-07: X API rejects posts with more than one cashtag (403 stopped the three-hits thread at post 4); tools/xlib.py now keeps only the first $TICKER.
- 2026-11-08: research-based growth plan applied (GROWTH-PLAN.md): headline-first formats, hourly
  breaking desk, US-hours slots, 3 reply rounds a day, recurring series. Baseline: 19 followers, posts 1–47 views.
