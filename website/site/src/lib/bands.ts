// Bands for drawing a spectrum (TASKS 44–45, 10 Oct 2026): sticks from the export (position, height in km/mol), degenerate partners within 1 cm⁻¹
// of the previous one summed, and bands under 0.5 % of the strongest dropped as not infrared-active — the rule module 08's spectrum module uses.
export interface Stick { omega_cm: number; km_mol: number | null }
export interface Band { omega: number; km: number }

export function mergeBands(sticks: Stick[], tolCm = 1.0, activeFraction = 0.005): Band[] {
  const merged: Band[] = [];
  for (const s of [...sticks].sort((a, b) => a.omega_cm - b.omega_cm)) {
    const km = s.km_mol ?? 0;
    const last = merged[merged.length - 1];
    if (last && s.omega_cm - last.omega <= tolCm) last.km += km; else merged.push({ omega: s.omega_cm, km });
  }
  const top = merged.reduce((m, b) => Math.max(m, b.km), 0);
  return merged.filter((b) => b.km >= activeFraction * top && b.km > 0);
}

// Heights aligned with listed positions (the cheap rung's export field) as sticks.
export function sticksFrom(positions: number[], heights: number[]): Stick[] {
  return positions.map((w, i) => ({ omega_cm: w, km_mol: heights[i] }));
}
