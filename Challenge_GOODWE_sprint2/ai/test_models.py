import unittest
from datetime import datetime, timedelta
from models import analyze, forecast, ZONE


def history():
    rows = []
    start = datetime(2026, 8, 1, 18, tzinfo=ZONE)
    for i in range(42):
        dt = start+timedelta(days=i)
        rows.append({'id': f'S{i}', 'start_at': dt.isoformat(), 'end_at': (dt+timedelta(hours=2)).isoformat(),
                     'duration_minutes': 120, 'energy_wh': 10000+i%5*100, 'review_status': 'clear'})
    return rows


class ModelTests(unittest.TestCase):
    def test_extreme_anomaly_is_flagged(self):
        result = analyze(history(), [{'id': 'BAD', 'energy_wh': 50000, 'duration_minutes': 10, 'reasons': []}])
        self.assertEqual(result['results'][0]['review_status'], 'pending')
        self.assertLess(result['results'][0]['score'], 0)

    def test_candidates_are_not_part_of_training(self):
        rows = history()
        result = analyze(rows, [dict(rows[0], reasons=[])])
        self.assertEqual(result['training_samples'], 41)

    def test_missing_and_insufficient_history_require_review(self):
        result = analyze([], [{'id': 'MISSING', 'energy_wh': None, 'duration_minutes': 10, 'reasons': ['Sem leitura válida.']}])
        self.assertEqual(result['results'][0]['review_status'], 'pending')
        self.assertIsNone(result['results'][0]['score'])

    def test_forecast_is_repeatable_and_excludes_future_and_rejected(self):
        rows = history()
        expected = forecast(rows, '2026-09-12')
        future = dict(rows[0], id='FUTURE', start_at='2026-09-13T18:00:00-03:00', end_at='2026-09-13T20:00:00-03:00', energy_wh=9999999)
        rejected = dict(rows[0], id='REJECTED', review_status='rejected', energy_wh=9999999)
        self.assertEqual(expected, forecast(rows+[future, rejected], '2026-09-12'))
        self.assertEqual(len(expected['hours']), 24)
        self.assertTrue(all(h['expected_kw'] >= 0 for h in expected['hours']))
        self.assertIn(expected['peak_hour'], (18, 19))
        self.assertEqual(expected['validation_days'], 7)

    def test_forecast_refuses_insufficient_history(self):
        with self.assertRaises(ValueError):
            forecast(history()[:3], '2026-08-05')


if __name__ == '__main__':
    unittest.main()
