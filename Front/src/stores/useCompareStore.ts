// src/stores/useCompareStore.ts
import { defineStore } from "pinia";
import { computed } from "vue";
import { useLocalStorage } from "@/composables/useLocalStorage";
import type { Product } from "@/types";

export const MAX_COMPARE_ITEMS = 4;

export const useCompareStore = defineStore("compare", () => {
  const items = useLocalStorage<Product[]>("compare", []);

  const isFull = computed(() => items.value.length >= MAX_COMPARE_ITEMS);

  const add = (p: Product) => {
    if (items.value.some((i) => i.id === p.id)) return;
    if (items.value.length >= MAX_COMPARE_ITEMS) return;
    items.value.push(p);
  };

  const remove = (id: number) => {
    items.value = items.value.filter((i) => i.id !== id);
  };

  const clear = () => {
    items.value = [];
  };

  const isInCompare = (id: number) => items.value.some((i) => i.id === id);

  return { items, isFull, add, remove, clear, isInCompare };
});
