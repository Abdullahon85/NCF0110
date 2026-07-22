// ProductGrid.vue - Simplified using ProductCard component
<template>
  <div class="products-grid">
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

interface Props {
  products: Product[];
}

defineProps<Props>();
</script>

<!-- Styles in main.css -->
