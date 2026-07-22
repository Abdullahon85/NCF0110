// components/CategoryCardComponent.vue
<template>
  <div class="category-card">
    <router-link :to="`/catalog/${category.slug}`" class="card-link">
      <div class="card-image">
        <img
          v-if="category.image"
          :src="category.image"
          :alt="category.name"
          loading="lazy"
          decoding="async"
        />
        <div v-else class="placeholder-image">
          <span>{{ category.name[0] }}</span>
        </div>
      </div>
      <div class="card-content">
        <h3>{{ category.name }}</h3>
        <p class="products-count">Товаров: {{ category.products_count }}</p>
      </div>
    </router-link>
  </div>
</template>

<script setup lang="ts">
import type { Category } from "@/types";

defineProps<{
  category: Category;
}>();
</script>

<!-- Styles in main.css -->
