<template>
  <div class="favorites-page container">
    <nav class="breadcrumb">
      <router-link to="/">Главная</router-link>
      <span class="separator">›</span>
      <span class="current">Избранное</span>
    </nav>

    <div class="page-header">
      <h1 class="page-title">Избранное</h1>
      <span class="page-count">{{ favStore.items.length }} товар(ов)</span>
    </div>

    <div v-if="favStore.items.length === 0" class="empty-state">
      <svg
        width="64"
        height="64"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
      >
        <path
          d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
        />
      </svg>
      <p>Вы ещё не добавили ни одного товара в избранное</p>
      <router-link to="/catalog" class="btn primary"
        >Перейти в каталог</router-link
      >
    </div>

    <div v-else>
      <div class="fav-toolbar">
        <button class="btn muted" @click="favStore.items.splice(0)">
          Очистить список
        </button>
      </div>
      <ProductGrid :products="favStore.items" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useFavoritesStore } from "@/stores/useFavoritesStore";
import ProductGrid from "@/components/ProductGrid.vue";

const favStore = useFavoritesStore();
</script>

<!-- Styles in main.css -->
