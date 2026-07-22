// stores/app.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { ContactInfo } from '@/types';
import { contactAPI } from '@/api';

export const useAppStore = defineStore('app', () => {
  const contactInfo = ref<ContactInfo | null>(null);
  const isContactInfoLoaded = ref(false);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const loadContactInfo = async () => {
    if (isContactInfoLoaded.value) return;
    
    try {
      isLoading.value = true;
      error.value = null;
      const response = await contactAPI.getInfo();
      contactInfo.value = response.data;
      isContactInfoLoaded.value = true;
    } catch (err) {
      error.value = 'Ошибка загрузки контактной информации';
      console.error('Failed to load contact info:', err);
    } finally {
      isLoading.value = false;
    }
  };

  const clearError = () => {
    error.value = null;
  };

  return {
    contactInfo,
    isContactInfoLoaded,
    isLoading,
    error,
    loadContactInfo,
    clearError
  };
});