// src/composables/useLocalStorage.ts
import { ref, watch } from "vue";
import { readJson } from "@/utils/storage";

export function useLocalStorage<T>(key: string, initial: T) {
  const state = ref<T>(readJson(localStorage, key, initial));

  watch(
    state,
    (v) => {
      try {
        localStorage.setItem(key, JSON.stringify(v));
      } catch {
        // storage full or blocked (private mode): keep working in memory
      }
    },
    { deep: true },
  );

  return state;
}
