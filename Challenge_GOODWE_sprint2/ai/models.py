"""Modelos determinísticos; medições reais nunca são substituídas por previsões."""
from datetime import datetime, timedelta
from math import sin, cos, pi
from zoneinfo import ZoneInfo

import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import mean_absolute_error

ZONE = ZoneInfo('America/Sao_Paulo')
MODEL_VERSION = 'chargeops-1.0-seed42'


def local_time(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(ZONE)


def vector(session):
    hours = session['duration_minutes'] / 60
    energy = session['energy_wh'] / 1000
    return [energy, hours, energy / hours]


def analyze(history, candidates):
    # Candidatos são removidos do treino: uma observação não se valida a si própria.
    ids = {s['id'] for s in candidates}
    baseline = [s for s in history if s['id'] not in ids and s.get('energy_wh') is not None
                and s['duration_minutes'] > 0 and s.get('review_status') in ('clear', 'approved')]
    model = None
    if len(baseline) >= 30:
        model = IsolationForest(n_estimators=120, contamination='auto', random_state=42, n_jobs=1)
        model.fit(np.array([vector(s) for s in baseline]))
    result = []
    for session in candidates:
        score = None
        reasons = list(session.get('reasons', []))
        if session.get('energy_wh') is not None and model is not None:
            features = np.array([vector(session)])
            score = float(model.decision_function(features)[0])
            if model.predict(features)[0] == -1:
                reasons.append(f'Isolation Forest: energia/duração/potência fora do histórico (score {score:.3f}).')
        if model is None:
            reasons.append('Histórico insuficiente para IA: mínimo de 30 sessões validadas; revisão obrigatória.')
        result.append({'id': session['id'], 'score': score, 'reasons': reasons,
                       'review_status': 'pending' if reasons else 'clear'})
    return {'model': 'IsolationForest', 'version': MODEL_VERSION, 'training_samples': len(baseline), 'results': result}


def features(dt):
    return [sin(2*pi*dt.hour/24), cos(2*pi*dt.hour/24),
            sin(2*pi*dt.weekday()/7), cos(2*pi*dt.weekday()/7), int(dt.weekday() >= 5)]


def forecast(history, target_date, capacity_kw=14.4):
    target = datetime.strptime(target_date, '%Y-%m-%d').replace(tzinfo=ZONE)
    # Retém somente sessões concluídas ANTES do dia previsto (sem vazamento temporal).
    usable = [s for s in history if s.get('energy_wh') is not None
              and s.get('review_status') in ('clear', 'approved')
              and target - timedelta(days=90) <= local_time(s['end_at']) <= target]
    if not usable:
        raise ValueError('Sem sessões validadas anteriores à previsão.')
    first = min(local_time(s['start_at']) for s in usable).replace(hour=0, minute=0, second=0, microsecond=0)
    # Janela de até 90 dias; intervalos vazios entram como zero, não são descartados.
    first = max(first, target - timedelta(days=90))
    days = (target - first).days
    if days < 14:
        raise ValueError('Previsão exige pelo menos 14 dias de histórico validado.')
    count = days * 24
    hourly = np.zeros(count)
    for session in usable:
        start, end = local_time(session['start_at']), local_time(session['end_at'])
        power = session['energy_wh'] / 1000 / ((end-start).total_seconds()/3600)
        cursor = max(start, first).replace(minute=0, second=0, microsecond=0)
        while cursor < min(end, target):
            overlap = max(0, (min(end, cursor+timedelta(hours=1)) - max(start, cursor)).total_seconds()/3600)
            index = int((cursor-first).total_seconds()/3600)
            if 0 <= index < count:
                hourly[index] += power * overlap
            cursor += timedelta(hours=1)
    dates = [first + timedelta(hours=i) for i in range(count)]
    x = np.array([features(dt) for dt in dates])
    # Últimos 7 dias reservados para avaliação cronológica, sem embaralhamento.
    split = count - 7*24
    model = RandomForestRegressor(n_estimators=100, min_samples_leaf=3, random_state=42, n_jobs=1)
    model.fit(x[:split], hourly[:split])
    mae = mean_absolute_error(hourly[split:], model.predict(x[split:]))
    baseline_predictions = []
    for dt in dates[split:]:
        matches = [hourly[i] for i, past in enumerate(dates[:split]) if past.weekday() == dt.weekday() and past.hour == dt.hour]
        baseline_predictions.append(float(np.mean(matches)) if matches else 0)
    baseline_mae = mean_absolute_error(hourly[split:], baseline_predictions)
    model.fit(x, hourly)
    estimates = np.maximum(0, model.predict(np.array([features(target+timedelta(hours=h)) for h in range(24)])))
    peak = int(np.argmax(estimates))
    recommendation = ('Revisar agendamentos no pico; demanda prevista acima de 80% da capacidade.'
                      if estimates[peak] > capacity_kw*0.8
                      else 'Capacidade prevista suficiente. Priorize recargas fora do horário de pico.')
    return {'model': 'RandomForestRegressor', 'version': MODEL_VERSION, 'date': target_date,
            'training_days': days, 'training_sessions': len(usable), 'validation_days': 7,
            'validation_mae_kw': round(float(mae), 3), 'baseline_mae_kw': round(float(baseline_mae), 3),
            'peak_hour': peak, 'peak_kw': round(float(estimates[peak]), 3), 'capacity_kw': capacity_kw,
            'recommendation': recommendation,
            'hours': [{'hour': h, 'expected_kw': round(float(v), 3)} for h, v in enumerate(estimates)]}
