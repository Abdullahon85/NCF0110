// src/composables/useLocalStorage.ts
import { ref, watch } from 'vue';

export function useLocalStorage<T>(key: string, initial: T) {
  const raw = localStorage.getItem(key);
  const state = ref<T>(raw ? JSON.parse(raw) as T : initial);

  watch(state, (v) => {
    localStorage.setItem(key, JSON.stringify(v));
  }, { deep: true });

  return state;
}
