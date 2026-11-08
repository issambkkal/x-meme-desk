# Weekly analysis (run on Sundays)

Paste this into Claude Code in this folder, or make it a scheduled task in the app
(Scheduled → New task, every Sunday 20:00).

---

Analyse the X account @issam0pc4u for the past week and improve its strategy.
Working folder: /Users/issam/Claude/Projects/social media/x-system

1. **Collect numbers (read-only).** In Claude in Chrome (I'm signed in to X there),
   open a new tab at https://x.com/issam0pc4u. The account has Premium now: first read
   https://x.com/i/account_analytics (impressions, engagement, follows per day); then read
   per-post stats from the posts: scroll the profile with javascript_tool, collect each article's
   time, text and the `[role="group"]` aria-label (replies/likes/views), store them in a
   window variable, and return them with links and `? & =` characters stripped. Note the
   follower count. Close the tab. Never like, reply, follow or post.
2. **Update data.** Fill views/likes/replies/reposts/bookmarks/checked_at in
   `analytics/posts.csv`; add rows for hand-made posts with pillar `manual`. Append
   `date,followers` to `analytics/followers.csv`.
3. **Analyse.** Views and follows by FORMAT (headline / chart-data / question / thread / signal-trap /
   breaking-desk `*-brk-*`), by pillar, chart vs no chart, single vs thread, time slot, hook
   style, length. Top 3 / bottom 3 posts and why. Small samples are hints, not rules.
4. **Report.** Write `analytics/week-YYYY-WW.md`: followers start → end, posts, total and
   median views, best/worst, what worked, what to change, 5 post ideas for next week.
5. **Improve.** Add a dated bullet to STRATEGY.md → Learnings (keep under ~25 bullets).
   If a pattern holds 2+ weeks, adjust the pillar mix, slots (also `config.yaml`) or
   format rules. Never change the Truth rules.
5b. **Pin.** Name the best post of the week (most views + replies) for the owner to pin.
6. **Summary.** 5 lines: follower change, best post, do more, stop, what changed.
