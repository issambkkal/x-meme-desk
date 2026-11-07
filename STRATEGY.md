# @issam0pc4u — X strategy (meme coins)

The drafting task reads this file before every run. The weekly analysis updates the
**Learnings** section. Edit anything here and the system follows it from the next run.

## Positioning

**"The meme coin trenches, with receipts — and the world that moves them."** Who actually
won, who got rugged, how to not be the exit liquidity, and how the global economy,
finance, industry and politics push money into and out of crypto and meme coins.
Every claim backed by on-chain data or a named source.

The edge: most meme accounts only look at charts; most macro accounts ignore meme coins.
We connect them: "Fed cut odds fell → dollar up → risk-off → meme coins bled first."

- Voice: first person, plain words, short lines, dry humour, a bit cynical about hype.
  Never shill, never "100x gem", never tell anyone to buy a coin. Not financial advice.
- Every post gives the reader one of: a number they didn't know, a chart that makes it
  obvious, a red flag they can check themselves, or a take they can argue with.

## Content pillars (aim for this mix each week)

| Pillar | Share | Example |
|---|---|---|
| Scam alert / red flags | 25% | "Bubblemaps: 40% of $XYZ supply sat in 12 linked wallets before launch. Here's how to check any coin in 30 seconds." |
| Macro → crypto (economy, finance, industry, politics) | 25% | "China's factory PMI fell to 48.6 and the dollar jumped. Last 3 times that happened, SOL meme coins lost X% in a week." Fed, CPI, jobs, yields, dollar, oil, tariffs, China/US factories, elections, SEC/Congress, stablecoin laws, ETF flows. Always end with what it means for crypto/meme traders. |
| Winners, with receipts | 20% | "A wallet turned $285 into $627K on one coin in a day (Lookonchain). Here's how many tried the same and lost." |
| Survival guide / how it works | 15% | "5 checks before you ape: holders, dev wallet, LP, bundles, socials." |
| Trenches data | 10% | Pump.fun launches per day, survival rate, platform revenue, liquidations |
| Personal / community | 5% | "Be honest: how many meme coins have you bought this year?" |

## Daily deep-dive article (one per day, 07:00 Doha research → 17:00 thread)

Every day one researched article in `articles/YYYY-MM-DD-slug.md` (900–1,500 words,
12+ sources, every number cited), on the biggest story that links the world to crypto:
e.g. "Why meme coins died this week: the dollar, the AI selloff and a $1.27B liquidation".
Structure: hook · what happened (numbers) · why (macro/politics/industry chain) · what
on-chain data shows · who won / who lost · what to watch next week (dates) · sources.
It goes out on X as a 6–10 post thread at 17:00 Doha (US open), with 1–3 charts.
The account is not Premium, so no X "Article" format; the full text stays in the repo.

## Research depth (non-negotiable)

- Read the full article for every source you cite (WebFetch), not just search snippets.
- For any macro claim, get the official or primary number (BLS, Fed, ECB, PBoC, NBS China,
  Caixin/S&P PMI, EIA, Treasury, SEC/Congress.gov, company filings) plus one major outlet.
- Always answer "so what for crypto?" with data: BTC/ETH/SOL moves, meme coin index or top
  meme coins, ETF flows, stablecoin supply, liquidations, funding rates.
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

- Max 280 characters per post (no Premium). Threads 3–7 posts. Hook in line 1.
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

- Up to 8 posts a day, 90+ minutes apart, around the clock for US, Europe and Asia.
  Slots (Doha, UTC+3): 08:00, 10:30, 13:00, 15:30, 17:00, 20:00, 23:00, 02:00.
  17:00 is reserved for the daily deep-dive thread.
- Up to 2 automatic reposts a day, only from `repost_ok: true` accounts, only scam
  alerts or hard data.
- Replies, likes and follows are done by hand (X bans automating them), using
  `replies/<date>.md`. 20–30 minutes a day, on watchlist accounts first.

## Learnings (updated weekly from real numbers)

- 2026-11-06 baseline: 45 posts, 5 followers. Best post: personal joke about losing money
  on a meme coin (27 views). News/data posts: 4–15 views. 17 posts in ~70 minutes on
  Nov 6 competed with each other.
- 2026-11-06: switched focus from general crypto/markets to meme coins.
- 2026-11-07: owner wants deeper research and the global economy/finance/industry/politics
  angle on every big crypto move; added macro pillar and the daily deep-dive article.
- 2026-11-07: X API rejects posts with more than one cashtag (403 stopped the three-hits thread at post 4); tools/xlib.py now keeps only the first $TICKER.
