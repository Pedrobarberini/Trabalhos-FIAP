import { normalizeSession } from '../../domain/session.mjs';
export function createDemoDataset() {
  const units = ['302', '401', '402', '403', '501', '999'];
  const names = [
    'Ana Martins',
    'Bruno Lima',
    'Carla Souza',
    'Diego Alves',
    'Elisa Rocha',
    'Felipe Costa',
  ];
  const catalog = {
    units: units.map((id) => ({ id, label: `Apto ${id}` })),
    users: units.map((id, i) => ({ id: `U${id}`, name: names[i], unit_id: id })),
    vehicles: units.map((id) => ({ id: `V${id}`, label: `EV • ${id}`, user_id: `U${id}` })),
    chargers: [
      { id: 'HCA01', label: 'GoodWe HCA G2 • Vaga 01', max_kw: 7.2 },
      { id: 'HCA02', label: 'GoodWe HCA G2 • Vaga 02', max_kw: 7.2 },
    ],
  };
  catalog.vehicles.push({ id: 'V302B', label: 'Segundo EV • 302', user_id: 'U302' });
  let state = 42;
  const random = () => {
    state = (1664525 * state + 1013904223) >>> 0;
    return state / 4294967296;
  };

  const history = [];
  for (let day = 0; day < 61; day++) {
    const date = new Date(Date.UTC(2026, 7, 1 + day)).toISOString().slice(0, 10);
    for (let charger = 0; charger < 2; charger++) {
      for (const [hour, maxHours] of [
        [8, 3],
        [12, 4],
        [18, 5],
      ]) {
        const unit = ['401', '402', '403', '501'][Math.floor(random() * 4)];
        const duration = Math.round((1 + random() * (maxHours - 1)) * 60);
        const start = `${date}T${String(hour).padStart(2, '0')}:00:00-03:00`;
        const end = new Date(new Date(start).getTime() + duration * 60000).toISOString();
        const power = 3.2 + random() * 3.8;
        const energy = Math.round(((power * duration) / 60) * 1000) / 1000;
        const input = {
          id: `HIST-${day}-${charger}-${hour}`,
          source: 'simulation',
          user_id: `U${unit}`,
          unit_id: unit,
          vehicle_id: `V${unit}`,
          charger_id: `HCA0${charger + 1}`,
          start_at: start,
          end_at: end,
          status: 'completed',
          start_meter_kwh: 1000,
          end_meter_kwh: 1000 + energy,
        };
        const row = normalizeSession(
          input,
          catalog.vehicles.find((v) => v.id === input.vehicle_id),
          catalog.users.find((u) => u.id === input.user_id),
          catalog.chargers[charger],
        );
        history.push({
          ...row,
          review_status: 'clear',
          reasons: [],
          anomaly_score: null,
          model_version: 'synthetic-validated-v1',
          created_at: '2026-10-01T03:00:00.000Z',
        });
      }
    }
  }

  const examples = [
    {
      id: 'DEMO-302-35',
      user_id: 'U302',
      unit_id: '302',
      vehicle_id: 'V302',
      charger_id: 'HCA01',
      start_at: '2026-09-29T00:00:00-03:00',
      end_at: '2026-09-29T07:00:00-03:00',
      status: 'completed',
      start_meter_kwh: 2000,
      end_meter_kwh: 2035,
    },
    {
      id: 'DEMO-302-25',
      user_id: 'U302',
      unit_id: '302',
      vehicle_id: 'V302B',
      charger_id: 'HCA01',
      start_at: '2026-09-30T00:00:00-03:00',
      end_at: '2026-09-30T05:00:00-03:00',
      status: 'interrupted',
      start_meter_kwh: 3000,
      last_valid_meter_kwh: 3025,
    },
    {
      id: 'DEMO-ANOMALIA',
      user_id: 'U401',
      unit_id: '401',
      vehicle_id: 'V401',
      charger_id: 'HCA02',
      start_at: '2026-09-30T23:00:00-03:00',
      end_at: '2026-09-30T23:10:00-03:00',
      status: 'completed',
      start_meter_kwh: 4000,
      end_meter_kwh: 4050,
    },
    {
      id: 'DEMO-SEM-LEITURA',
      user_id: 'U402',
      unit_id: '402',
      vehicle_id: 'V402',
      charger_id: 'HCA02',
      start_at: '2026-09-30T23:10:00-03:00',
      end_at: '2026-09-30T23:20:00-03:00',
      status: 'interrupted',
      start_meter_kwh: 5000,
    },
  ];

  return { catalog, history, examples };
}
