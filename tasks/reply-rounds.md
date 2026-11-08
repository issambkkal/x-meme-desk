# Reply rounds (@issam0pc4u) — 3 a day in US hours, when the owner says "round"

Bots may only answer people who interact with us, so replies under other accounts' posts are
made in the browser (Chrome, signed in as @issam0pc4u) when the owner asks for a round.

| Round | Doha | US Eastern | Why |
|---|---|---|---|
| Morning | ~16:30 | 8:30am | data releases (CPI, jobs) + market pre-open |
| Midday | ~20:00 | 12:00pm | lunch, busiest hour for finance |
| Close | ~00:00 | 4:00pm | market close, earnings after the bell |

Why it works (X's ranking code): replies from accounts a viewer doesn't follow show up only
inside the thread, so POSITION is everything. Premium replies rank higher, and the first
15–30 minutes of a big post decide who gets seen.

1. Data: smartmoney/signals.md + today's smartmoney/trades/*.jsonl (buys vs sells), research/<date>.md,
   the newest scans/<date>.md sections, queue/ and posted/ (what we already said).
2. Notifications/mentions first: answer real replies (skip spam bots).
3. Sweep WIDE, never a fixed list. Latest tab, last ~60 minutes first (then up to 3h),
   `-filter:replies lang:en`, collect 40+ candidates and pick 12–15 posts from DIFFERENT accounts:
   - Breaking/world: `(BREAKING OR "JUST IN") min_faves:100`
   - Stocks: `($SPY OR $QQQ OR $NVDA OR $TSLA OR $AAPL OR $GLD OR $DXY OR $TLT OR $MSFT OR $PLTR OR $AMD) min_faves:25`
   - Macro: `(fed OR inflation OR CPI OR "rate cut" OR jobs OR tariffs OR oil OR yields OR recession) min_faves:40`
   - Politics: `(congress OR senate OR "white house" OR election OR sanctions OR ceasefire) min_faves:100`
   - Crypto: `($BTC OR $ETH OR $SOL OR $XRP OR $HYPE OR $SUI OR $BNB) min_faves:30`
   - Meme coins: `(memecoin OR memecoins OR pumpfun OR trenches OR rugged OR $PEPE OR $WIF OR $BONK OR $FARTCOIN OR $DOGE) min_faves:20 -giveaway -airdrop`
   - Big accounts that posted in the last 30 minutes (be early): spectatorindex, KobeissiLetter,
     WatcherGuru, unusual_whales, zerohedge, Reuters, AP, CNBC, lookonchain, Cointelegraph, saylor.
   Mix: ~5 huge posts that are under 30 minutes old + ~8 mid-size (1K–20K views) where a reply is seen.
   Skip giveaways, parody, sports/TV, and anyone already replied to today.
4. One reply each: under 280 chars, ONE real number or a sharp sourced angle, adds something
   the post didn't say, no links, no bare domains ("Pump fun"), no buy calls, no hashtags,
   never the same stat twice in a round. Politics: neutral and factual. Token shills:
   check DexScreener first, facts only.
5. Quote posts (browser only; the API can't quote): on the 1–2 biggest stories of the round,
   quote the original with our own number + why it matters.
6. Save to replies/<date>.md (## <time> round), show the owner, post after their yes.
7. Posting: open the status, like it, click the reply box, type, click Reply, verify an
   @issam0pc4u article appears; 10–15 s between replies.
8. Report: replies posted, followers vs last round, and the best reply's views from the last round.

## Sniper mode (2026-11-08, after the data said rounds were invisible)
Evidence: 11 replies under 16K–40K-view posts, sent 40–60 min after the post (46+ replies already there),
got 1–7 views each. New accounts' replies rank near the bottom unless they are among the FIRST few.
- Only reply where the post is under ~10 minutes old AND has fewer than ~5 replies, from accounts whose
  posts reach 20K+ views (Mario Nawfal, FirstSquawk, Kobeissi, Watcher Guru, Spectator Index, zerohedge,
  unusual_whales, Polymarket, lookonchain, Cointelegraph, BNONews, DeItaone, gurgavin, AshCrypto, cryptorover…).
  Check with the live search `(from:A OR from:B …) -filter:replies` and the time/reply counts.
- 1–3 replies per check, at least 2–3 minutes apart. Max ~40 sniper replies a day.
- Use the post's own numbers plus one of ours; a sharp question is fine when we have no extra fact. Never invent.
- Follows: people who reposted lookonchain/Kobeissi/OnchainLens posts (real, active), max ~10 per 30 minutes.
  X rate-limited us after 15 quick follows on 2026-11-08: if "rate limited" or "unable to follow" shows, stop
  follows for 1 hour. Never unfollow-churn.
- Record each reply's views 1–2 hours later (with_replies tab) to learn which accounts/topics pay off.

## 2026-11-08 10:20 update: replies are being hidden — paused
First-minute sniper replies under posts with 14K–18K views got 1–3 views, so X is hiding this account's replies
from other viewers. No reply rounds or sniper loops until a re-test shows replies reaching 20+ views.
Re-test: 2–3 slow, hand-paced replies a day on posts in our niche, check views after 2 hours. Follows: max 10/day.
