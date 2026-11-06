# @issam0pc4u — X strategy (meme coins)

The drafting task reads this file before every run. The weekly analysis updates the
**Learnings** section. Edit anything here and the system follows it from the next run.

## Positioning

**"The meme coin trenches, with receipts."** Who actually won, who got rugged, and how
to not be the exit liquidity. Every claim backed by on-chain data or a named source.

- Voice: first person, plain words, short lines, dry humour, a bit cynical about hype.
  Never shill, never "100x gem", never tell anyone to buy a coin. Not financial advice.
- Every post gives the reader one of: a number they didn't know, a chart that makes it
  obvious, a red flag they can check themselves, or a take they can argue with.

## Content pillars (aim for this mix each week)

| Pillar | Share | Example |
|---|---|---|
| Scam alert / red flags | 30% | "Bubblemaps: 40% of $XYZ supply sat in 12 linked wallets before launch. Here's how to check any coin in 30 seconds." |
| Winners, with receipts | 25% | "A wallet turned $285 into $627K on one coin in a day (Lookonchain). Here's how many tried the same and lost." |
| Survival guide / how it works | 20% | "5 checks before you ape: holders, dev wallet, LP, bundles, socials." |
| Trenches data | 15% | Pump.fun launches per day, survival rate, platform revenue, liquidations |
| Personal / community | 10% | "Be honest: how many meme coins have you bought this year?" |

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
- At most 2 emojis. Cashtags ($WIF) are fine; at most 2 per post.
- No links anywhere in posts: the API charges $0.20 instead of $0.015, and X shows link
  posts to fewer people. Name the source in words; the URL goes in `sources`.
- No referral links until 1,000+ followers.
- Charts: 1600×900 dark style via `tools/chart.py`. At least half of posts carry one.

## Truth rules (non-negotiable)

- Every number in a post appears in the file's `sources` with a URL (X post URLs count).
- Breaking claims (hacks, rugs, arrests, exploits) need two independent sources, or one
  sleuth in watchlist.yaml plus on-chain evidence they link to.
- If sources disagree, use the conservative number or skip.
- Never invent quotes, wallets, trades or personal events.

## Cadence

- Up to 6 posts a day, 2+ hours apart, around the clock for US and Asia traders.
  Slots (Doha, UTC+3): 09:00, 13:00, 16:30, 20:00, 23:00, 02:00.
- Up to 2 automatic reposts a day, only from `repost_ok: true` accounts, only scam
  alerts or hard data.
- 1 deep thread a week (Sunday 20:00): "I tracked X meme coins, here's what I found."
- Replies, likes and follows are done by hand (X bans automating them), using
  `replies/<date>.md`. 20–30 minutes a day, on watchlist accounts first.

## Learnings (updated weekly from real numbers)

- 2026-11-06 baseline: 45 posts, 5 followers. Best post: personal joke about losing money
  on a meme coin (27 views). News/data posts: 4–15 views. 17 posts in ~70 minutes on
  Nov 6 competed with each other.
- 2026-11-06: switched focus from general crypto/markets to meme coins.
