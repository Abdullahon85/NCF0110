<template>
  <div class="product-card">
    <router-link :to="`/product/${product.slug}`" class="card-link">
      <!-- Изображение -->
      <div class="card-image">
        <img
          v-if="product.main_image"
          :src="product.main_image.image"
          :alt="product.name"
        />
        <div v-else class="placeholder-image">
          <span>{{ product.name[0] }}</span>
        </div>

        <span v-if="!product.is_available" class="out-of-stock"
          >Нет в наличии</span
        >
      </div>

      <!-- Контент -->
      <div class="card-content">
        <h3 class="product-title">{{ product.name }}</h3>
        <p class="category">{{ product.category_name }}</p>

        <p v-if="product.price" class="price">
          {{ formatPrice(product.price) }} ₽
        </p>
      </div>
    </router-link>
  </div>
</template>

<script setup lang="ts">
import type { Product } from "@/types";

defineProps<{ product: Product }>();

const formatPrice = (price: number) =>
  new Intl.NumberFormat("ru-RU").format(price);
</script>

<!-- Styles in main.css -->
