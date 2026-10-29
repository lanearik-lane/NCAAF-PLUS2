# NCAAF+ — Hard Rock games and price grades

Run `pip install -r requirements.txt` then `streamlit run ncaaf_plus_2026.py`.

## Activate live odds and Monday updates

1. In Streamlit **Manage app → Settings → Secrets**, add:
   ```toml
   ODDS_API_KEY = "your-key-from-the-odds-api"
   ```
2. In this repository **Settings → Secrets and variables → Actions → New repository secret**, add `ODDS_API_KEY` with the same value. Never commit the key or paste it into the source code.
3. Open **Actions → Monday Hard Rock board → Run workflow** once to verify access and generate the first saved board.
4. Ensure Actions is enabled and can write repository contents. Branch protection may prevent saving snapshots and requires adjusting deployment/storage configuration.

The workflow targets **Monday at noon America/New_York**, adjusting for daylight saving time. It runs without an open Streamlit session and commits `data/hardrock_board.json`, causing the repository-connected Streamlit app to redeploy. GitHub schedules are best effort and may be late or skipped; public repository schedules can be disabled after 60 days of inactivity. Failed refreshes retain the old snapshot; the app shows timestamps and blocks stale picks. Keys are not included in snapshots. Odds snapshots in this public repository are public.

The app uses live odds when a key is configured, caching for five minutes per app rerun. Use **Refresh board** for a manual refresh. Without a live key it can display the saved Monday snapshot, but after 30 minutes that snapshot provides schedule/line reference only and picks become PASS. Set the key in both places for current picks throughout the week.

## Views

- **Hard Rock board**: only upcoming events that actually contain a `hardrockbet` bookmaker entry. It never relabels another book as Hard Rock. Posted games may extend beyond the current week. Filter dates and teams. Missing markets show dashes instead of invented prices.
- **Weekly schedule**: the existing ESPN calendar-week loader, including completed games and scores when available. These fixtures do not establish sportsbook availability. No betting grade is assigned to an ESPN-only fixture.

The Odds API documents Hard Rock Indiana coverage. Another state's board, late additions, live games, props, and unposted lines may differ. This app shows pregame h2h, spreads and totals; it does not claim access to a user's signed-in Hard Rock account or supply player props.

## Picks and corrected grading

The old hand-entered ratings, synthetic public betting percentages, sharp-money labels, made-up odds and unsupported confidence percentages have been removed from the active app.

Moneyline screening requires Hard Rock and at least two other distinct sportsbooks with valid two-sided prices updated within 30 minutes. Each comparison book's implied probabilities are normalized to remove the bookmaker margin. The median comparison probability is weighted 75%, with 25% weight on Hard Rock's own margin-removed probability to temper outliers. More than eight percentage points of disagreement across comparison books causes PASS. The best side by estimated return must meet the selected edge threshold (default three percentage points, hard floor two) and have positive estimated return.

| Signal grade | Criteria |
| --- | --- |
| A | Qualifying pick; at least three comparison books, at least four percentage points edge and at most three percentage points disagreement |
| B | Qualifying pick with at least two comparison books and positive estimated return |
| PASS | Started game, missing/stale prices, insufficient comparison books, excessive disagreement, or no qualifying price edge |

Grades describe price evidence, not calibrated hit rates. An A can be an underdog; win probability and price advantage are displayed separately. Estimates are not a trained/backtested model and do not establish a profitable edge. Check injuries and prices before wagering. Spreads and totals are displayed as actual Hard Rock quotes, not unvalidated predictions. There are no automatic wagers.

## Validation

`python -m unittest discover -s tests -v`

Tests cover Hard Rock filtering, started games, duplicate events, time sorting, price calculations, conservative probability weighting, stale and missing prices, disagreement rejection, grade criteria, invalid odds, and Monday daylight saving scheduling with delayed runs. Streamlit UI smoke checks use synthetic fixtures. Live odds access requires the user's key and has not been verified without it.

Sources:
- https://the-odds-api.com/sports-odds-data/bookmaker-apis.html
- https://the-odds-api.com/liveapi/guides/v4/
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
