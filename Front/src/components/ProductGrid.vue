<template>
  <div class="products-grid" :class="{ 'is-list': view === 'list' }">
    <ProductCard
      v-for="(product, index) in products"
      :key="product.slug || product.id"
      :product="product"
      :priority="index < 4"
    />
  </div>
</template>

<script setup lang="ts">
import ProductCard from "./ProductCard.vue";
import type { Product } from "@/types";

withDefaults(defineProps<{ products: Product[]; view?: "grid" | "list" }>(), { view: "grid" });
</script>

<!-- Styles in styles/site/ -->
