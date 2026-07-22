import { defineStore } from 'pinia';

export const useLoadingStore = defineStore('loading', {
  state: () => ({
    isLoading: false,
    error: null as string | null,
  }),
  
  actions: {
    setLoading(value: boolean) {
      this.isLoading = value;
    },
    
    setError(error: string | null) {
      this.error = error;
    },
    
    async withLoading<T>(callback: () => Promise<T>): Promise<T | null> {
      this.setLoading(true);
      this.setError(null);
      try {
        const result = await callback();
        return result;
      } catch (error) {
        this.setError(error instanceof Error ? error.message : 'Произошла ошибка');
        return null;
      } finally {
        this.setLoading(false);
      }
    },
  },
});