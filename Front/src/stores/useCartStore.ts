// src/stores/useCartStore.ts
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { CartItem } from "@/types";
import { useLocalStorage } from "@/composables/useLocalStorage";

export const useCartStore = defineStore("cart", () => {
  // сидируем из localStorage
  const items = useLocalStorage<CartItem[]>("cart_items", []);
  const adding = ref(false);

  const add = (product: any, qty = 1, options = {}) => {
    const idx = items.value.findIndex((i) => i.product.id === product.id);
    if (idx >= 0) {
      items.value[idx].quantity += qty;
    } else {
      items.value.push({ product, quantity: qty, selectedOptions: options });
    }
  };

  const remove = (productId: number) => {
    items.value = items.value.filter((i) => i.product.id !== productId);
  };

  const setQty = (productId: number, qty: number) => {
    const i = items.value.find((it) => it.product.id === productId);
    if (!i) return;
    i.quantity = Math.max(1, qty);
  };

  const clear = () => {
    items.value = [];
  };

  const isInCart = (productId: number) =>
    items.value.some((i) => i.product.id === productId);

  const totalQty = computed(() =>
    items.value.reduce((s, it) => s + it.quantity, 0),
  );
  const subtotal = computed(() =>
    items.value.reduce((s, it) => s + (it.product.price || 0) * it.quantity, 0),
  );
  const hasPrice = computed(() =>
    items.value.some((it) => it.product.price != null),
  );

  return {
    items,
    adding,
    add,
    remove,
    setQty,
    clear,
    isInCart,
    totalQty,
    subtotal,
    hasPrice,
  };
});
