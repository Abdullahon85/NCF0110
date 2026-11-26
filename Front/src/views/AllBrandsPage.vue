<!-- src/views/AllBrandsPage.vue -->
<template>
  <div class="all-brands-page">
    <!-- Page hero banner -->
    <div class="brands-hero">
      <div class="brands-hero-content container">
        <h1 class="brands-hero-title">Все бренды</h1>
        <p class="brands-hero-sub">Оборудование от ведущих производителей систем безопасности</p>
      </div>
    </div>

    <div class="container">
      <!-- Mobile Filter Button -->
      <button class="mobile-filter-btn" @click="showFilters = true">
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <line x1="4" y1="6" x2="20" y2="6" />
          <line x1="4" y1="12" x2="20" y2="12" />
          <line x1="4" y1="18" x2="20" y2="18" />
        </svg>
        Фильтры
      </button>

      <!-- Overlay -->
      <transition name="fade">
        <div v-if="showFilters" class="filters-overlay show" @click="showFilters = false"></div>
      </transition>

      <div class="page-layout">
        <aside class="filters-column" :class="{ 'show-mobile': showFilters }">
          <div class="filters-sticky">
            <button class="mobile-filter-close" @click="showFilters = false">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
            <div class="filters-header">
              <h3>
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <line x1="4" y1="21" x2="4" y2="14" />
                  <line x1="4" y1="10" x2="4" y2="3" />
                  <line x1="12" y1="21" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12" y2="3" />
                  <line x1="20" y1="21" x2="20" y2="16" />
                  <line x1="20" y1="12" x2="20" y2="3" />
                  <line x1="1" y1="14" x2="7" y2="14" />
                  <line x1="9" y1="8" x2="15" y2="8" />
                  <line x1="17" y1="16" x2="23" y2="16" />
                </svg>
                Фильтры
              </h3>
              <button class="btn-reset" title="Сбросить все" @click="resetFilters">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                  <path d="M3 3v5h5" />
                </svg>
              </button>
            </div>

            <!-- Поиск по брендам -->
            <div class="filter-section">
              <label class="filter-label">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                Поиск
              </label>
              <div class="search-wrapper">
                <input
                  v-model="filters.search"
                  type="text"
                  placeholder="Поиск брендов..."
                  class="search-input"
                  @keyup.enter="applyFilters"
                />
                <button class="btn-search" @click="applyFilters">
                  <svg
                    width="16"
                    height="16"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    viewBox="0 0 24 24"
                  >
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Фильтр по категориям -->
            <div v-if="categories.length > 0" class="filter-section">
              <label class="filter-label">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <rect x="3" y="3" width="7" height="7" />
                  <rect x="14" y="3" width="7" height="7" />
                  <rect x="14" y="14" width="7" height="7" />
                  <rect x="3" y="14" width="7" height="7" />
                </svg>
                Каталог товаров
              </label>
              <div class="categories-list">
                <label v-for="category in categories" :key="category.slug" class="category-item">
                  <input
                    v-model="filters.categories"
                    type="checkbox"
                    :value="category.slug"
                    @change="applyFilters"
                  />
                  <span class="category-checkbox"></span>
                  <span>{{ category.name }}</span>
                </label>
              </div>
            </div>

            <!-- Фильтр по наличию товаров -->
            <div class="filter-section">
              <label class="filter-label">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle cx="9" cy="21" r="1" />
                  <circle cx="20" cy="21" r="1" />
                  <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                </svg>
                Наличие товаров
              </label>
              <label class="toggle-switch">
                <input v-model="filters.hasProducts" type="checkbox" @change="applyFilters" />
                <span class="toggle-slider"></span>
                <span class="toggle-text">Только с товарами</span>
              </label>
            </div>

            <!-- Active Filters -->
            <div v-if="hasActiveFilters" class="active-filters">
              <div class="active-filters-header">Активные фильтры:</div>
              <div class="filter-tags">
                <span v-if="filters.search" class="filter-tag">
                  {{ filters.search }}
                  <button
                    @click="
                      filters.search = '';
                      applyFilters();
                    "
                  >
                    ×
                  </button>
                </span>
                <span v-for="cat in filters.categories" :key="cat" class="filter-tag">
                  {{ getCategoryName(cat) }}
                  <button @click="removeCategory(cat)">×</button>
                </span>
                <span v-if="filters.hasProducts" class="filter-tag">
                  С товарами
                  <button
                    @click="
                      filters.hasProducts = false;
                      applyFilters();
                    "
                  >
                    ×
                  </button>
                </span>
              </div>
            </div>

            <!-- Filter Actions -->
            <div class="filter-actions">
              <button class="btn muted" @click="resetFilters">Сбросить</button>
              <button class="btn primary" @click="showFilters = false">Применить</button>
            </div>
          </div>
        </aside>

        <main class="content-column">
          <!-- Панель управления -->
          <div class="topbar">
            <div class="topbar-left">
              <div v-if="!loading" class="results-badge">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                <span
                  >Найдено: <strong>{{ pagination.total }}</strong></span
                >
              </div>
            </div>
            <div class="topbar-right">
              <label class="sort-label">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <line x1="3" y1="6" x2="21" y2="6" />
                  <line x1="6" y1="12" x2="18" y2="12" />
                  <line x1="9" y1="18" x2="15" y2="18" />
                </svg>
              </label>
              <select v-model="filters.ordering" class="sort-select" @change="applyFilters">
                <option value="name">По названию (А-Я)</option>
                <option value="-name">По названию (Я-А)</option>
              </select>
            </div>
          </div>

          <!-- Контент -->
          <div v-if="loading" class="loading">
            <div class="spinner"></div>
            <p>Загрузка брендов...</p>
          </div>

          <div v-else-if="error" class="error-state">
            <div class="error-icon">⚠️</div>
            <h3>Ошибка загрузки</h3>
            <p>{{ error }}</p>
            <button class="btn-retry" @click="() => loadBrands()">
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
              Повторить попытку
            </button>
          </div>

          <div v-else-if="brands.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg
                width="64"
                height="64"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
              >
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>
            <h3>Бренды не найдены</h3>
            <p>Попробуйте изменить параметры фильтрации</p>
            <button class="btn-retry" @click="resetFilters">
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
              Сбросить фильтры
            </button>
          </div>

          <div v-else>
            <div class="brands-grid">
              <BrandCard v-for="brand in brands" :key="brand.slug" :brand="brand" />
            </div>

            <Pagination
              v-if="pagination.totalPages > 1"
              :current-page="pagination.page"
              :total-pages="pagination.totalPages"
              class="brands-pagination"
              @change="changePage"
            />
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from "vue";
import { brandsAPI, categoriesAPI } from "@/api";
import type { Brand, Category } from "@/types";
import BrandCard from "@/components/BrandCard.vue";
import Pagination from "@/components/Pagination.vue";

const FILTER_STORAGE_KEY = "allBrandsFilters_v1";

const brands = ref<Brand[]>([]);
const categories = ref<Category[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const showFilters = ref(false);

const filters = reactive({
  search: "",
  categories: [] as string[],
  hasProducts: false,
  ordering: "name" as string,
});

const pagination = reactive({
  page: 1,
  pageSize: 12,
  totalPages: 1,
  total: 0,
});

// Computed
const hasActiveFilters = computed(() => {
  return filters.search || filters.categories.length > 0 || filters.hasProducts;
});

// Restore filters from localStorage
const restoreFilters = () => {
  try {
    const saved = localStorage.getItem(FILTER_STORAGE_KEY);
    if (!saved) return;
    const parsed = JSON.parse(saved);
    filters.search = parsed.search ?? "";
    filters.categories = Array.isArray(parsed.categories) ? parsed.categories : [];
    filters.hasProducts = Boolean(parsed.hasProducts);
    filters.ordering = parsed.ordering ?? "name";
  } catch (e) {
    console.error("Не удалось восстановить фильтры", e);
  }
};

// Persist filters to localStorage
watch(
  () => ({
    search: filters.search,
    categories: [...filters.categories],
    hasProducts: filters.hasProducts,
    ordering: filters.ordering,
  }),
  (value) => {
    try {
      localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(value));
    } catch (e) {
      console.error("Не удалось сохранить фильтры", e);
    }
  },
  { deep: true },
);

// Helpers
const getCategoryName = (slug: string) => {
  const cat = categories.value.find((c) => c.slug === slug);
  return cat ? cat.name : slug;
};

const removeCategory = (slug: string) => {
  filters.categories = filters.categories.filter((c) => c !== slug);
  applyFilters();
};

// Построение параметров API
const buildApiParams = () => {
  const params: Record<string, any> = {
    page: pagination.page,
    page_size: pagination.pageSize,
    ordering: filters.ordering,
  };

  if (filters.search) {
    params.search = filters.search.trim();
  }

  if (filters.categories.length > 0) {
    params.category = filters.categories.filter(Boolean).join(",");
  }

  if (filters.hasProducts) {
    params.has_products = "true";
  }

  return params;
};

// Загрузка данных
const loadBrands = async (allowFallback = true) => {
  loading.value = true;
  error.value = null;

  try {
    const params = buildApiParams();
    const response = await brandsAPI.getAll(params);
    const data = response.data || {};

    brands.value = data.results || [];
    pagination.total = Number(data.count ?? 0);
    pagination.totalPages = Math.max(1, Math.ceil(pagination.total / pagination.pageSize));

    // Keep position; no auto scroll on filter/pagination
  } catch (err) {
    console.error("Ошибка загрузки брендов:", err);

    // Fallback: если сортировка по количеству товаров ломает API, откатываем на имя
    if (allowFallback && String(filters.ordering).includes("products_count")) {
      filters.ordering = "name";
      await loadBrands(false);
      return;
    }

    error.value = "Не удалось загрузить бренды. Попробуйте позже.";
    brands.value = [];
  } finally {
    loading.value = false;
  }
};

const loadCategories = async () => {
  try {
    const response = await categoriesAPI.getAll();
    categories.value = response.data.results || [];
  } catch (err) {
    console.error("Ошибка загрузки категорий:", err);
  }
};

// Обработчики событий
const applyFilters = () => {
  pagination.page = 1;
  loadBrands();
};

const resetFilters = () => {
  filters.search = "";
  filters.categories = [];
  filters.hasProducts = false;
  filters.ordering = "name";
  applyFilters();
};

const changePage = (page: number) => {
  if (page < 1 || page > pagination.totalPages) return;
  pagination.page = page;
  loadBrands();
};

// Инициализация
onMounted(async () => {
  restoreFilters();
  await Promise.all([loadCategories(), loadBrands()]);
});
</script>

<style scoped src="@/styles/views/AllBrandsPage.css"></style>
