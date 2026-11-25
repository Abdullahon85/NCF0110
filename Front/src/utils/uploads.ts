import { adminErrorMessage } from "./apiError.ts";

// Upload items one by one. A failed upload does not stop the rest; the result
// lists "file name: reason" for every failure so the admin can be told.
export async function uploadEach<T>(
  items: T[],
  upload: (item: T) => Promise<unknown>,
  name: (item: T) => string,
): Promise<string[]> {
  const failures: string[] = [];
  for (const item of items) {
    try {
      await upload(item);
    } catch (e) {
      failures.push(`${name(item)}: ${adminErrorMessage(e, "не удалось загрузить")}`);
    }
  }
  return failures;
}
