function timestamp(value) {
  return `${value.length === 16 ? `${value}:00` : value}-03:00`;
}

export function sessionInput(fields, { unitId, userId, status }) {
  const { end_meter_kwh: finalReading, ...rest } = fields;
  const readingKey = status === 'interrupted' ? 'last_valid_meter_kwh' : 'end_meter_kwh';
  return {
    ...rest,
    unit_id: unitId,
    user_id: userId,
    status,
    start_at: timestamp(fields.start_at),
    end_at: timestamp(fields.end_at),
    ...(finalReading === '' ? {} : { [readingKey]: finalReading }),
  };
}
