export const DAY_START_MIN = 6 * 60;
export const DAY_DUR_MIN = 18 * 60;
export const HOUR_LABELS = ["06", "08", "10", "12", "14", "16", "18", "20", "22", "24"];

export function toMin(t: string): number {
  if (!t || !t.includes(":")) return 0;
  const [h, m] = t.split(":").map(Number);
  return h * 60 + m;
}

export function fromMin(m: number): string {
  const h = Math.floor(Math.max(0, m) / 60);
  const mm = Math.max(0, m) % 60;
  return `${String(h).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
}

export function toPct(t: string): number {
  return Math.max(0, Math.min(100, ((toMin(t) - DAY_START_MIN) / DAY_DUR_MIN) * 100));
}

export function widthPct(start: string, end: string): number {
  const sm = toMin(start);
  const em = toMin(end);
  if (!sm || !em || em <= sm) return 0;
  return Math.min(100 - toPct(start), ((em - sm) / DAY_DUR_MIN) * 100);
}
