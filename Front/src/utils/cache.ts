// src/utils/cache.ts
// Утилита кэширования для API запросов

interface CacheItem<T> {
  data: T;
  expiry: number;
}

class ApiCache {
  private prefix = "api_cache_";

  get<T>(key: string): T | null {
    try {
      const item = sessionStorage.getItem(this.prefix + key);
      if (!item) return null;

      const { data, expiry }: CacheItem<T> = JSON.parse(item);

      if (Date.now() > expiry) {
        sessionStorage.removeItem(this.prefix + key);
        return null;
      }

      return data;
    } catch {
      return null;
    }
  }

  set<T>(key: string, data: T, ttlMs = 300000): void {
    try {
      const item: CacheItem<T> = {
        data,
        expiry: Date.now() + ttlMs,
      };
      sessionStorage.setItem(this.prefix + key, JSON.stringify(item));
    } catch (e) {
      // sessionStorage full или disabled
      console.warn("Cache write failed:", e);
    }
  }

  remove(key: string): void {
    sessionStorage.removeItem(this.prefix + key);
  }

  clear(): void {
    Object.keys(sessionStorage)
      .filter((key) => key.startsWith(this.prefix))
      .forEach((key) => sessionStorage.removeItem(key));
  }
}

export const apiCache = new ApiCache();

/**
 * Helper для кэшированных запросов
 * @param key - уникальный ключ кэша
 * @param fetchFn - функция для выполнения запроса
 * @param ttlMs - время жизни кэша в миллисекундах (по умолчанию 5 минут)
 */
export async function cachedFetch<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttlMs = 300000
): Promise<T> {
  const cached = apiCache.get<T>(key);
  if (cached) {
    return cached;
  }

  const data = await fetchFn();
  apiCache.set(key, data, ttlMs);
  return data;
}
