// JSON value from localStorage; a missing, broken or unreadable entry gives `fallback`
// (a corrupted entry must not stop the whole site from starting).
export function readJson<T>(storage: Pick<Storage, "getItem">, key: string, fallback: T): T {
  try {
    const raw = storage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}
