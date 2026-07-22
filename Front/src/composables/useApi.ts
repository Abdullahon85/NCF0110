//compostables/useApi.ts
import { ref } from 'vue';
import type { Ref } from 'vue';
// import { useLoadingStore } from '@/stores/loading';

export function useApi<T>() {
  const data: Ref<T | null> = ref(null);
  const error: Ref<string | null> = ref(null);
  const loading = ref(false);
  // const loadingStore = useLoadingStore(); // сейчас не используется

  const execute = async (apiCall: () => Promise<{ data: T }>) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await apiCall();
      data.value = response.data;
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Произошла ошибка';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    data,
    error,
    loading,
    execute,
  };
}
