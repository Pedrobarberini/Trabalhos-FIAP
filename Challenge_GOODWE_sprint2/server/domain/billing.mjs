export function consumptionCents(energyWh, tariffMillis) {
  return Number((BigInt(energyWh) * BigInt(tariffMillis) + 5000n) / 10000n);
}
