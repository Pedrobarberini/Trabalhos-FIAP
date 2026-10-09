import numpy as np
from sklearn.ensemble import IsolationForest

from config import MODEL_VERSION, RANDOM_SEED

MINIMUM_SAMPLES = 30


def session_features(session):
    hours = session['duration_minutes'] / 60
    energy = session['energy_wh'] / 1000
    return [energy, hours, energy / hours]


def analyze(history, candidates):
    candidate_ids = {session['id'] for session in candidates}
    baseline = [
        session for session in history
        if session['id'] not in candidate_ids
        and session.get('energy_wh') is not None
        and session['duration_minutes'] > 0
        and session.get('review_status') in ('clear', 'approved')
    ]
    model = None
    if len(baseline) >= MINIMUM_SAMPLES:
        model = IsolationForest(
            n_estimators=120, contamination='auto', random_state=RANDOM_SEED, n_jobs=1,
        )
        model.fit(np.array([session_features(session) for session in baseline]))

    results = []
    for session in candidates:
        score = None
        reasons = list(session.get('reasons', []))
        if session.get('energy_wh') is not None and model is not None:
            features = np.array([session_features(session)])
            score = float(model.decision_function(features)[0])
            if model.predict(features)[0] == -1:
                reasons.append(
                    'Isolation Forest: energia/duração/potência fora do histórico '
                    f'(score {score:.3f}).'
                )
        if model is None:
            reasons.append(
                'Histórico insuficiente para IA: mínimo de 30 sessões validadas; '
                'revisão obrigatória.'
            )
        results.append({
            'id': session['id'], 'score': score, 'reasons': reasons,
            'review_status': 'pending' if reasons else 'clear',
        })
    return {
        'model': 'IsolationForest', 'version': MODEL_VERSION,
        'training_samples': len(baseline), 'results': results,
    }
