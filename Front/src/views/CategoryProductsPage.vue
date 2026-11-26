<template>
  <div class="container category-page">
    <nav class="breadcrumb" aria-label="Навигация">
      <router-link to="/">Главная</router-link>
      <span class="separator">›</span>
      <router-link to="/catalog">Каталог</router-link>
      <template v-for="a in category?.ancestors ?? []" :key="a.slug">
        <span class="separator">›</span>
        <router-link :to="`/catalog/${a.slug}`">{{ a.name }}</router-link>
      </template>
      <span class="separator">›</span>
      <span class="current">{{ category?.name ?? "" }}</span>
    </nav>
    <h1 v-if="category" class="cp-title">{{ category.name }}</h1>
    <p v-if="notFound" class="empty-state">
      Каталог не найден. <router-link to="/catalog">Весь каталог</router-link>
    </p>
    <ProductListing v-else :fixed="{ category: slug }" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { categoriesAPI } from "@/api";
import type { Category } from "@/types";
import ProductListing from "@/components/catalog/ProductListing.vue";

const route = useRoute();
const slug = computed(() => String(route.params.categorySlug || ""));
const category = ref<Category | null>(null);
const notFound = ref(false);

watch(
  slug,
  async (value) => {
    category.value = null;
    notFound.value = false;
    if (!value) return;
    try {
      category.value = (await categoriesAPI.getBySlug(value)).data;
    } catch (e: any) {
      notFound.value = e?.response?.status === 404;
    }
  },
  { immediate: true },
);
</script>

<!-- Styles in styles/site/ -->
