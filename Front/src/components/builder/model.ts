// "Соберите систему": which equipment fits where on the scene, and what the visitor assembled.
// Pure data and functions — the component only draws and handles dragging.

export type PieceId = "dome" | "bullet" | "nvr" | "poe" | "router" | "wifi" | "access" | "ups";

export interface Piece {
  id: PieceId;
  label: string;
  search: string;
  img: string;
}

export interface Slot {
  id: string;
  label: string;
  accepts: PieceId[];
  /** position of the slot centre on the scene, in % of its width and height */
  x: number;
  y: number;
}

/** slotId -> piece standing there */
export type Placement = Readonly<Record<string, PieceId>>;

const piece = (id: PieceId, label: string, search: string): Piece => ({
  id,
  label,
  search,
  img: `/builder/${id}.webp`,
});

export const PIECES: Piece[] = [
  piece("dome", "Купольная камера", "купольная камера"),
  piece("bullet", "Уличная камера", "цилиндрическая камера"),
  piece("nvr", "Видеорегистратор", "видеорегистратор"),
  piece("poe", "PoE-коммутатор", "коммутатор PoE"),
  piece("router", "Роутер", "роутер"),
  piece("wifi", "Точка Wi‑Fi", "точка доступа"),
  piece("access", "Контроль доступа", "контроль доступа"),
  piece("ups", "ИБП", "ИБП"),
];

// Order matters: firstFreeSlot fills slots in this order.
export const SLOTS: Slot[] = [
  { id: "entrance", label: "Вход", accepts: ["dome", "bullet"], x: 22, y: 44 },
  { id: "hall-1", label: "Торговый зал", accepts: ["dome"], x: 29, y: 38 },
  { id: "hall-2", label: "Торговый зал", accepts: ["dome"], x: 57, y: 41 },
  { id: "cashier", label: "Касса", accepts: ["dome"], x: 51, y: 56 },
  { id: "parking", label: "Парковка", accepts: ["bullet"], x: 78, y: 49 },
  { id: "yard", label: "Двор", accepts: ["bullet", "dome"], x: 9, y: 50 },
  { id: "door", label: "Дверь в служебное помещение", accepts: ["access"], x: 65, y: 47 },
  { id: "ceiling", label: "Потолок зала", accepts: ["wifi"], x: 44, y: 46 },
  { id: "rack-nvr", label: "Серверный шкаф", accepts: ["nvr"], x: 71, y: 27 },
  { id: "rack-poe", label: "Серверный шкаф", accepts: ["poe"], x: 80, y: 26 },
  { id: "rack-router", label: "Серверный шкаф", accepts: ["router"], x: 71, y: 38 },
  { id: "rack-ups", label: "Серверный шкаф", accepts: ["ups"], x: 82, y: 40 },
];

const slotById = new Map(SLOTS.map((s) => [s.id, s]));
const CAMERAS: PieceId[] = ["dome", "bullet"];

export function place(p: Placement, slotId: string, pieceId: PieceId): Placement {
  const slot = slotById.get(slotId);
  if (!slot || p[slotId] || !slot.accepts.includes(pieceId)) return p;
  return { ...p, [slotId]: pieceId };
}

export function removeAt(p: Placement, slotId: string): Placement {
  if (!(slotId in p)) return p;
  const next = { ...p };
  delete next[slotId];
  return next;
}

export function firstFreeSlot(p: Placement, pieceId: PieceId): string | null {
  return SLOTS.find((s) => !p[s.id] && s.accepts.includes(pieceId))?.id ?? null;
}

export function summary(p: Placement): { id: PieceId; label: string; count: number }[] {
  const placed = Object.values(p);
  return PIECES.map((pc) => ({
    id: pc.id,
    label: pc.label,
    count: placed.filter((x) => x === pc.id).length,
  })).filter((r) => r.count > 0);
}

export function hints(p: Placement): string[] {
  const placed = new Set(Object.values(p));
  if (placed.size === 0) return [];
  const out: string[] = [];
  const hasCameras = CAMERAS.some((c) => placed.has(c));
  if (hasCameras && !placed.has("nvr"))
    out.push("Камерам нужен видеорегистратор: он записывает и хранит видео.");
  if (hasCameras && !placed.has("poe"))
    out.push("IP-камеры получают питание по сетевому кабелю — добавьте PoE-коммутатор.");
  if (!placed.has("ups")) out.push("Добавьте ИБП, чтобы система работала при отключении света.");
  return out;
}

export function requestText(p: Placement): string {
  const rows = summary(p);
  if (rows.length === 0) return "";
  return [
    "Здравствуйте! Хочу рассчитать систему:",
    ...rows.map((r) => `— ${r.label} × ${r.count}`),
  ].join("\n");
}
