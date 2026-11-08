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
