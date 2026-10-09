CREATE TABLE IF NOT EXISTS units (
  id TEXT PRIMARY KEY, label TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY, name TEXT NOT NULL,
  unit_id TEXT NOT NULL REFERENCES units(id)
);
CREATE TABLE IF NOT EXISTS vehicles (
  id TEXT PRIMARY KEY, label TEXT NOT NULL,
  user_id TEXT NOT NULL REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS chargers (
  id TEXT PRIMARY KEY, label TEXT NOT NULL, max_kw REAL NOT NULL CHECK (max_kw > 0)
);
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  user_id TEXT NOT NULL REFERENCES users(id),
  vehicle_id TEXT NOT NULL REFERENCES vehicles(id),
  charger_id TEXT NOT NULL REFERENCES chargers(id),
  unit_id TEXT NOT NULL REFERENCES units(id),
  start_at TEXT NOT NULL, end_at TEXT NOT NULL, billing_month TEXT NOT NULL,
  start_wh INTEGER NOT NULL CHECK (start_wh >= 0),
  final_wh INTEGER,
  energy_wh INTEGER CHECK (energy_wh >= 0),
  duration_minutes REAL NOT NULL CHECK (duration_minutes > 0),
  status TEXT NOT NULL CHECK (status IN ('completed', 'interrupted')),
  review_status TEXT NOT NULL CHECK (review_status IN ('clear', 'pending', 'approved', 'rejected')),
  reasons TEXT NOT NULL,
  anomaly_score REAL,
  model_version TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS sessions_month ON sessions(billing_month, unit_id);
CREATE INDEX IF NOT EXISTS sessions_charger ON sessions(charger_id, start_at, end_at);
CREATE TABLE IF NOT EXISTS reviews (
  id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
  decision TEXT NOT NULL CHECK (decision IN ('approved', 'rejected')),
  reason TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS invoices (
  id TEXT PRIMARY KEY, unit_id TEXT NOT NULL REFERENCES units(id), month TEXT NOT NULL,
  energy_wh INTEGER NOT NULL CHECK (energy_wh >= 0),
  tariff_millis INTEGER NOT NULL CHECK (tariff_millis >= 0),
  fixed_cents INTEGER NOT NULL CHECK (fixed_cents >= 0),
  consumption_cents INTEGER NOT NULL CHECK (consumption_cents >= 0),
  total_cents INTEGER NOT NULL CHECK (total_cents >= 0), created_at TEXT NOT NULL,
  UNIQUE(unit_id, month)
);
CREATE TABLE IF NOT EXISTS invoice_sessions (
  invoice_id TEXT NOT NULL REFERENCES invoices(id),
  session_id TEXT NOT NULL UNIQUE REFERENCES sessions(id),
  PRIMARY KEY(invoice_id, session_id)
);
