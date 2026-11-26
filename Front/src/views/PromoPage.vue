<template>
  <div class="container category-page">
    <nav class="breadcrumb" aria-label="Навигация">
      <router-link to="/">Главная</router-link>
      <span class="separator">›</span>
      <span class="current">Акции</span>
    </nav>
    <h1 class="cp-title">Акции и скидки</h1>
    <ProductListing :fixed="{ promo: '1' }" />
  </div>
</template>

<script setup lang="ts">
// Products with the "Акция" / "Распродажа" label or an old (struck-through) price.
import ProductListing from "@/components/catalog/ProductListing.vue";
</script>
