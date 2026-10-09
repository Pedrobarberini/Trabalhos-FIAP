from datetime import datetime, timedelta
from math import cos, pi, sin

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from config import MODEL_VERSION, RANDOM_SEED, ZONE
from temporal import local_time

HISTORY_DAYS = 90
MINIMUM_DAYS = 14
VALIDATION_DAYS = 7
HOURS_PER_DAY = 24
HOUR = timedelta(hours=1)


def time_features(moment):
    hour_angle = 2 * pi * moment.hour / HOURS_PER_DAY
    weekday_angle = 2 * pi * moment.weekday() / 7
    return [
        sin(hour_angle), cos(hour_angle),
        sin(weekday_angle), cos(weekday_angle),
        int(moment.weekday() >= 5),
    ]


def hourly_history(history, target):
    earliest = target - timedelta(days=HISTORY_DAYS)
    usable = [
        session for session in history
        if session.get('energy_wh') is not None
        and session.get('review_status') in ('clear', 'approved')
        and earliest <= local_time(session['end_at']) <= target
    ]
    if not usable:
        raise ValueError('Sem sessões validadas anteriores à previsão.')
    first = min(local_time(session['start_at']) for session in usable)
    first = max(first.replace(hour=0, minute=0, second=0, microsecond=0), earliest)
    days = (target - first).days
    if days < MINIMUM_DAYS:
        raise ValueError('Previsão exige pelo menos 14 dias de histórico validado.')

    hourly = np.zeros(days * HOURS_PER_DAY)
    for session in usable:
        start = local_time(session['start_at'])
        end = local_time(session['end_at'])
        power = session['energy_wh'] / 1000 / ((end - start).total_seconds() / 3600)
        cursor = max(start, first).replace(minute=0, second=0, microsecond=0)
        while cursor < min(end, target):
            overlap = max(
                0,
                (min(end, cursor + HOUR) - max(start, cursor)).total_seconds() / 3600,
            )
            index = int((cursor - first).total_seconds() / 3600)
            if 0 <= index < len(hourly):
                hourly[index] += power * overlap
            cursor += HOUR
    dates = [first + index * HOUR for index in range(len(hourly))]
    return dates, hourly, len(usable)


def historical_baseline(training_dates, training_values, validation_dates):
    buckets = {}
    for moment, value in zip(training_dates, training_values):
        buckets.setdefault((moment.weekday(), moment.hour), []).append(value)
    return [
        float(np.mean(buckets[(moment.weekday(), moment.hour)]))
        if (moment.weekday(), moment.hour) in buckets else 0
        for moment in validation_dates
    ]


def forecast(history, target_date, capacity_kw=14.4):
    target = datetime.strptime(target_date, '%Y-%m-%d').replace(tzinfo=ZONE)
    dates, hourly, session_count = hourly_history(history, target)
    features = np.array([time_features(moment) for moment in dates])
    split = len(hourly) - VALIDATION_DAYS * HOURS_PER_DAY
    model = RandomForestRegressor(
        n_estimators=100, min_samples_leaf=3, random_state=RANDOM_SEED, n_jobs=1,
    )
    model.fit(features[:split], hourly[:split])
    mae = mean_absolute_error(hourly[split:], model.predict(features[split:]))
    baseline = historical_baseline(dates[:split], hourly[:split], dates[split:])
    baseline_mae = mean_absolute_error(hourly[split:], baseline)

    model.fit(features, hourly)
    target_features = np.array([
        time_features(target + hour * HOUR) for hour in range(HOURS_PER_DAY)
    ])
    estimates = np.maximum(0, model.predict(target_features))
    peak = int(np.argmax(estimates))
    recommendation = (
        'Revisar agendamentos no pico; demanda prevista acima de 80% da capacidade.'
        if estimates[peak] > capacity_kw * 0.8
        else 'Capacidade prevista suficiente. Priorize recargas fora do horário de pico.'
    )
    return {
        'model': 'RandomForestRegressor', 'version': MODEL_VERSION,
        'date': target_date, 'training_days': len(hourly) // HOURS_PER_DAY,
        'training_sessions': session_count, 'validation_days': VALIDATION_DAYS,
        'validation_mae_kw': round(float(mae), 3),
        'baseline_mae_kw': round(float(baseline_mae), 3),
        'peak_hour': peak, 'peak_kw': round(float(estimates[peak]), 3),
        'capacity_kw': capacity_kw, 'recommendation': recommendation,
        'hours': [
            {'hour': hour, 'expected_kw': round(float(value), 3)}
            for hour, value in enumerate(estimates)
        ],
    }
