# Strategy change, Nov 11 2026 (owner decision)

Posting 33-41 times a day to ~90 followers pushed median views per post from 19 to 2. The owner chose to cut automatic posting to 4 a day.

- max_posts_per_day 20 -> 4 (config.yaml)
- x_signals.py GREEN_PER_DAY 3 -> 1, TRAP_PER_DAY stays 2
- Disabled cloud routines: breaking desk, content desk, daily deep-dive (re-enable at claude.ai/code/routines)
- Queued news posts set to status: hold, not deleted.
