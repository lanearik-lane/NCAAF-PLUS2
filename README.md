# NCAAF+ — ESPN weekly schedule

Run `pip install -r requirements.txt` then `streamlit run ncaaf_plus_2026.py`.

The original weekly ESPN schedule view is restored, with the corrected daily fixture loader. No sportsbook API key is required. Use Refresh schedule to reload.

The user uses Hard Rock Florida. ESPN fixtures do not establish which games or lines are available in Florida. The restored legacy picks, grades and prices are unvalidated model estimates, not sportsbook quotes or calibrated win probabilities. Confirm games and prices in Hard Rock Florida before betting.

The API-based Monday odds workflow has been removed. There is no unattended Monday sportsbook sync. ESPN data is fetched when the app runs, cached for five minutes.
