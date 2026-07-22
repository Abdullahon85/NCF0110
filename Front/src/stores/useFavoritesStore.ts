// src/stores/useFavoritesStore.ts
import { defineStore } from 'pinia';
import { useLocalStorage } from '@/composables/useLocalStorage';
import type { Product } from '@/types';

export const useFavoritesStore = defineStore('favorites', () => {
  const items = useLocalStorage<Product[]>('favorites', []);

  const toggle = (product: Product) => {
    const idx = items.value.findIndex(p => p.id === product.id);
    if (idx >= 0) items.value.splice(idx, 1);
    else items.value.push(product);
  };

  const isFavorite = (id: number) => items.value.some(p => p.id === id);

  return { items, toggle, isFavorite };
});
