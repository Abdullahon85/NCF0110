<!-- src/views/CatalogPage.vue -->
<template>
  <div class="catalog-page">
    <div class="container catalog-body">
      <template v-if="!searchQuery">
        <nav class="cat-crumbs" aria-label="Навигация по сайту">
          <router-link to="/">Главная</router-link>
          <span aria-hidden="true">/</span>
          <span aria-current="page">Каталог</span>
        </nav>
        <h1 class="cat-title">Каталог товаров</h1>
        <p class="cat-sub">Профессиональное оборудование систем безопасности</p>
      </template>

      <!-- ══ SEARCH RESULTS (filters like a category page) ══ -->
      <div v-if="searchQuery" class="search-results-section">
        <div class="search-header">
          <h1>Результаты поиска</h1>
          <div class="search-query-display">
            <span class="search-label">Запрос:</span>
            <span class="search-value">«{{ searchQuery }}»</span>
            <router-link to="/catalog" class="clear-search">Очистить</router-link>
          </div>
        </div>
        <ProductListing :fixed="{}" />
      </div>

      <!-- ══ CATALOG ══ -->
      <div v-else>
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>Загрузка каталога...</p>
        </div>

        <div v-else-if="error" class="error-message">{{ error }}</div>

        <ul v-else-if="categories.length" class="cat-grid">
          <li v-for="category in categories" :key="category.id" class="cat-card">
            <router-link :to="`/catalog/${category.slug}`" class="cat-card-head">
              <span class="cat-card-img">
                <img
                  v-if="category.image"
                  :src="getImageUrl(category.image)"
                  alt=""
                  loading="lazy"
                />
                <svg
                  v-else
                  width="28"
                  height="28"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.6"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <rect x="3" y="3" width="7" height="7" rx="1" />
                  <rect x="14" y="3" width="7" height="7" rx="1" />
                  <rect x="14" y="14" width="7" height="7" rx="1" />
                  <rect x="3" y="14" width="7" height="7" rx="1" />
                </svg>
              </span>
              <span class="cat-card-text">
                <span class="cat-card-name">{{ category.name }}</span>
                <span class="cat-card-count">{{ countLabel(totalCount(category)) }}</span>
              </span>
            </router-link>
            <ul v-if="category.children?.length" class="cat-subs">
              <li v-for="sub in category.children" :key="sub.id">
                <router-link :to="`/catalog/${sub.slug}`" class="cat-sub-link">
                  <span>{{ sub.name }}</span>
                  <span class="cat-sub-count">{{ totalCount(sub) }}</span>
                </router-link>
              </li>
            </ul>
            <router-link :to="`/catalog/${category.slug}`" class="cat-all">
              Все товары раздела
              <svg width="16" height="16" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path
                  d="M4 10h12M11 5l5 5-5 5"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </router-link>
          </li>
        </ul>

        <div v-else class="empty-catalog">
          <p>Каталог пуст</p>
        </div>
      </div>
    </div>
    <!-- /catalog-body -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { categoriesAPI, getImageUrl } from "@/api";
import type { Category } from "@/types";
import ProductListing from "@/components/catalog/ProductListing.vue";

const route = useRoute();
const router = useRouter();
const categories = ref<Category[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

/** Products in a section including all its subsections (the section page lists them all). */
function totalCount(c: Category): number {
  return (c.products_count || 0) + (c.children || []).reduce((n, ch) => n + totalCount(ch), 0);
}

function countLabel(n: number): string {
  const d10 = n % 10,
    d100 = n % 100;
  const word =
    d10 === 1 && d100 !== 11
      ? "товар"
      : d10 >= 2 && d10 <= 4 && (d100 < 12 || d100 > 14)
        ? "товара"
        : "товаров";
  return `${n} ${word}`;
}

const searchQuery = computed(() => String(route.query.q || "").trim());

const loadCategories = async () => {
  try {
    const response = await categoriesAPI.getAll();
    const payload = "results" in response.data ? response.data.results : response.data;
    categories.value = payload;
  } catch (err) {
    error.value = "Ошибка загрузки каталога";
    console.error(err);
  }
};

onMounted(async () => {
  // Old links used ?search=; the product lists read ?q=.
  if (route.query.search && !route.query.q) {
    router.replace({ query: { q: String(route.query.search) } });
  }
  try {
    loading.value = true;
    await loadCategories();
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped src="@/styles/views/CatalogPage.css"></style>
