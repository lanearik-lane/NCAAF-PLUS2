import copy
import datetime as dt
import unittest
from hardrock_data import hardrock_events, screen, implied, ET, monday_due

NOW = dt.datetime(2026, 10, 29, 16, tzinfo=dt.timezone.utc)
def book(key, a, h):
    return {'key': key, 'last_update': NOW.isoformat(), 'markets': [
        {'key': 'h2h', 'outcomes': [{'name': 'Away', 'price': a}, {'name': 'Home', 'price': h}]}]}
def event():
    return {'id': 'one', 'away_team': 'Away', 'home_team': 'Home',
            'commence_time': '2026-10-31T17:00:00Z',
            'bookmakers': [book('hardrockbet', 120, -140), book('draftkings', -110, -110), book('fanduel', -110, -110)]}

class BoardTests(unittest.TestCase):
    def test_hardrock_only_and_started_games(self):
        other = event(); other['id'] = 'other'; other['bookmakers'].pop(0)
        started = event(); started['commence_time'] = NOW.isoformat()
        self.assertEqual(hardrock_events({'events':[other, started]}, NOW), [])
    def test_sort_and_dedupe(self):
        a = event(); b = event(); b['id']='two'; b['commence_time']='2026-10-30T17:00:00Z'
        self.assertEqual([e['id'] for e in hardrock_events({'events':[a,b,a]}, NOW)], ['two','one'])
    def test_price_edge_and_no_vig(self):
        p = screen(event(), NOW)
        self.assertEqual(p['pick'], 'Away')
        expected=.75*.5+.25*implied(120)/(implied(120)+implied(-140))
        self.assertAlmostEqual(p['probability'], expected)
        self.assertAlmostEqual(p['ev'], expected*1.2-(1-expected))
        self.assertEqual(p['grade'], 'B')
    def test_favorite_is_not_automatic_pick(self):
        e=event(); e['bookmakers'][0]=book('hardrockbet', -110, -110)
        self.assertEqual(screen(e, NOW)['pick'], 'PASS')
    def test_stale_or_missing_comparison_pass(self):
        self.assertEqual(screen(event(), NOW+dt.timedelta(hours=1))['pick'], 'PASS')
        e=event(); e['bookmakers'].pop()
        self.assertEqual(screen(e, NOW)['pick'], 'PASS')
    def test_missing_side_pass(self):
        e=event(); e['bookmakers'][0]['markets'][0]['outcomes'].pop()
        self.assertEqual(screen(e, NOW)['pick'], 'PASS')
    def test_zero_spread_is_available(self):
        e=event(); e['bookmakers'][0]['markets'].append({'key':'spreads','outcomes':[{'name':'Away','price':-110,'point':0}]})
        self.assertEqual(len(hardrock_events({'events':[e]}, NOW)), 1)
    def test_eastern_dst(self):
        self.assertEqual(dt.datetime(2026,10,26,16,tzinfo=dt.timezone.utc).astimezone(ET).hour,12)
        self.assertEqual(dt.datetime(2026,11,2,17,tzinfo=dt.timezone.utc).astimezone(ET).hour,12)
    def test_grade_a_requires_three_books_and_edge(self):
        e=event();e['bookmakers'][0]=book('hardrockbet',150,-170)
        e['bookmakers'].append(book('betmgm',-110,-110))
        self.assertEqual(screen(e,NOW)['grade'],'A')
    def test_large_disagreement_pass(self):
        e=event();e['bookmakers'][2]=book('fanduel',-300,250)
        self.assertEqual(screen(e,NOW)['grade'],'PASS')
    def test_started_game_pass(self):
        e=event();e['commence_time']=NOW.isoformat()
        self.assertEqual(screen(e,NOW)['pick'],'PASS')
    def test_monday_schedule_dst_and_delays(self):
        summer=dt.datetime(2026,10,26,18,tzinfo=dt.timezone.utc)
        winter=dt.datetime(2026,11,2,19,tzinfo=dt.timezone.utc)
        self.assertTrue(monday_due(summer,'0 16 * * 1'))
        self.assertFalse(monday_due(summer,'0 17 * * 1'))
        self.assertTrue(monday_due(winter,'0 17 * * 1'))
        self.assertFalse(monday_due(winter,'0 16 * * 1'))
        self.assertFalse(monday_due(winter+dt.timedelta(days=1),'0 17 * * 1'))
    def test_invalid_odds(self):
        for price in [0,float('nan'),float('inf'),True]:
            with self.assertRaises(ValueError): implied(price)

if __name__ == '__main__': unittest.main()
