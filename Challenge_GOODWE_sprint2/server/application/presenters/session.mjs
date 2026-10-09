export function publicSession(row) {
  return {
    ...row,
    energy_kwh: row.energy_wh == null ? null : row.energy_wh / 1000,
    average_kw: row.energy_wh == null ? null : row.energy_wh / 1000 / (row.duration_minutes / 60),
  };
}
