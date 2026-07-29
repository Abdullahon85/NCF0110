<!-- src/views/AllBrandsPage.vue -->
<template>
  <div class="all-brands-page">
    <!-- Page hero banner -->
    <div class="brands-hero">
      <div class="brands-hero-bg"></div>
      <div class="brands-hero-content">
        <span class="brands-hero-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          Мировые производители
        </span>
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
        <div
          v-if="showFilters"
          class="filters-overlay show"
          @click="showFilters = false"
        ></div>
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
              <button
                @click="resetFilters"
                class="btn-reset"
                title="Сбросить все"
              >
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
                  type="text"
                  v-model="filters.search"
                  @keyup.enter="applyFilters"
                  placeholder="Поиск брендов..."
                  class="search-input"
                />
                <button @click="applyFilters" class="btn-search">
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
            <div class="filter-section" v-if="categories.length > 0">
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
                <label
                  v-for="category in categories"
                  :key="category.slug"
                  class="category-item"
                >
                  <input
                    type="checkbox"
                    :value="category.slug"
                    v-model="filters.categories"
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
                  <path
                    d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"
                  />
                </svg>
                Наличие товаров
              </label>
              <label class="toggle-switch">
                <input
                  type="checkbox"
                  v-model="filters.hasProducts"
                  @change="applyFilters"
                />
                <span class="toggle-slider"></span>
                <span class="toggle-text">Только с товарами</span>
              </label>
            </div>

            <!-- Active Filters -->
            <div class="active-filters" v-if="hasActiveFilters">
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
                <span
                  v-for="cat in filters.categories"
                  :key="cat"
                  class="filter-tag"
                >
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
              <button @click="resetFilters" class="btn muted">Сбросить</button>
              <button @click="showFilters = false" class="btn primary">
                Применить
              </button>
            </div>
          </div>
        </aside>

        <main class="content-column">
          <!-- Панель управления -->
          <div class="topbar">
            <div class="topbar-left">
              <div class="results-badge" v-if="!loading">
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
              <select
                v-model="filters.ordering"
                @change="applyFilters"
                class="sort-select"
              >
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
            <button @click="() => loadBrands()" class="btn-retry">
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
            <button @click="resetFilters" class="btn-retry">
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
              <BrandCard
                v-for="brand in brands"
                :key="brand.slug"
                :brand="brand"
              />
            </div>

            <Pagination
              v-if="pagination.totalPages > 1"
              :current-page="pagination.page"
              :total-pages="pagination.totalPages"
              @change="changePage"
              class="brands-pagination"
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
    filters.categories = Array.isArray(parsed.categories)
      ? parsed.categories
      : [];
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
    pagination.totalPages = Math.max(
      1,
      Math.ceil(pagination.total / pagination.pageSize),
    );

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

<style scoped>
/* ═══ Brands Hero Banner ═══ */
.brands-hero {
  position: relative;
  background: linear-gradient(135deg, #081c15 0%, #1b4332 60%, #2d6a4f 100%);
  overflow: hidden;
  padding: 52px 0 44px;
  text-align: center;
}

.brands-hero-bg {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 50%, rgba(212, 165, 116, 0.12) 0%, transparent 50%),
    radial-gradient(circle at 80% 30%, rgba(64, 145, 108, 0.15) 0%, transparent 50%);
  pointer-events: none;
}

.brands-hero-content {
  position: relative;
  z-index: 1;
  max-width: 640px;
  margin: 0 auto;
  padding: 0 20px;
}

.brands-hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: rgba(212, 165, 116, 0.15);
  border: 1px solid rgba(212, 165, 116, 0.3);
  border-radius: 20px;
  color: #d4a574;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  margin-bottom: 16px;
}

.brands-hero-title {
  font-size: clamp(28px, 5vw, 48px);
  font-weight: 800;
  color: #fff;
  margin: 0 0 12px;
  letter-spacing: -0.5px;
}

.brands-hero-sub {
  font-size: clamp(13px, 2vw, 16px);
  color: rgba(255,255,255,0.65);
  margin: 0;
  line-height: 1.6;
}

/* All Brands Page Styles */
.all-brands-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

/* Layout */
.page-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 32px;
  padding: 48px 0;
}

/* Filters */
.filters-column {
}

.filters-sticky {
  position: sticky;
  top: 100px;
  background: white;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(27, 67, 50, 0.08);
}

.filters-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.filters-header h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 700;
  color: #1b4332;
  margin: 0;
}

.filters-header svg {
  color: #40916c;
}

.btn-reset {
  padding: 8px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-reset:hover {
  background: #f8f9fa;
  color: #1b4332;
  transform: rotate(180deg);
}

/* Filter Section */
.filter-section {
  margin-bottom: 28px;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #495057;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-label svg {
  color: #40916c;
}

/* Search */
.search-wrapper {
  position: relative;
  display: flex;
  gap: 8px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #40916c;
  box-shadow: 0 0 0 4px rgba(64, 145, 108, 0.1);
}

.btn-search {
  padding: 12px 16px;
  background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
  border: none;
  border-radius: 12px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-search:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(27, 67, 50, 0.3);
}

/* Categories List */
.categories-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 240px;
  overflow-y: auto;
  padding-right: 8px;
}

.categories-list::-webkit-scrollbar {
  width: 6px;
}

.categories-list::-webkit-scrollbar-thumb {
  background: #dee2e6;
  border-radius: 10px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.category-item:hover {
  background: #f8f9fa;
}

.category-item input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
}

.category-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  transition: all 0.3s;
  position: relative;
  flex-shrink: 0;
}

.category-item input:checked ~ .category-checkbox {
  background: linear-gradient(135deg, #1b4332 0%, #40916c 100%);
  border-color: #1b4332;
}

.category-item input:checked ~ .category-checkbox::after {
  content: "✓";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.category-item span:last-child {
  font-size: 14px;
  color: #495057;
}

/* Toggle Switch */
.toggle-switch {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.toggle-switch:hover {
  background: #e9ecef;
}

.toggle-switch input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
}

.toggle-slider {
  width: 48px;
  height: 26px;
  background: #dee2e6;
  border-radius: 13px;
  position: relative;
  transition: all 0.3s;
  flex-shrink: 0;
}

.toggle-slider::before {
  content: "";
  position: absolute;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  top: 3px;
  left: 3px;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle-switch input:checked ~ .toggle-slider {
  background: linear-gradient(135deg, #1b4332 0%, #40916c 100%);
}

.toggle-switch input:checked ~ .toggle-slider::before {
  transform: translateX(22px);
}

.toggle-text {
  font-size: 14px;
  color: #495057;
  font-weight: 500;
}

/* Active Filters */
.active-filters {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 2px solid #f0f0f0;
}

.active-filters-header {
  font-size: 12px;
  font-weight: 600;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
  color: white;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.filter-tag button {
  background: transparent;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
}

.filter-tag button:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Topbar */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(27, 67, 50, 0.08);
  margin-bottom: 28px;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.results-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 18px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  font-size: 14px;
  color: #495057;
  border: 1px solid #dee2e6;
}

.results-badge svg {
  color: #40916c;
}

.results-badge strong {
  color: #1b4332;
  font-weight: 700;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sort-label {
  display: flex;
  align-items: center;
  color: #40916c;
}

.sort-select {
  padding: 10px 16px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 14px;
  color: #495057;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.sort-select:focus {
  outline: none;
  border-color: #40916c;
  box-shadow: 0 0 0 4px rgba(64, 145, 108, 0.1);
}

/* States */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e9ecef;
  border-top-color: #1b4332;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 20px;
}

.loading p {
  color: #6c757d;
  font-size: 16px;
}

.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.error-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-icon {
  color: #dee2e6;
  margin-bottom: 20px;
}

.error-state h3,
.empty-state h3 {
  font-size: 24px;
  font-weight: 700;
  color: #212529;
  margin: 0 0 12px;
}

.error-state p,
.empty-state p {
  color: #6c757d;
  font-size: 16px;
  margin: 0 0 24px;
}

.btn-retry {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-retry:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(27, 67, 50, 0.3);
}

/* Brands Grid */
.brands-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
  margin-bottom: 48px;
}

/* Pagination */
.brands-pagination {
  margin-top: 48px;
}

/* Animations */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ═══════════════════════════════════════
   MOBILE FILTER BUTTON & OVERLAY (hidden on desktop)
═══════════════════════════════════════ */
.mobile-filter-btn {
  display: none;
}
.mobile-filter-close {
  display: none;
}
.filters-overlay {
  display: none;
}

/* Filter Actions */
.filter-actions {
  display: flex;
  gap: 10px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 2px solid #f0f0f0;
}
.filter-actions .btn {
  flex: 1;
  padding: 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.3s;
}
.filter-actions .btn.muted {
  background: #f8f9fa;
  color: #495057;
  border: 1.5px solid #dee2e6;
}
.filter-actions .btn.primary {
  background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
  color: white;
}
.filter-actions .btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(27, 67, 50, 0.3);
}

/* ═══════════════════════════════════════
   TABLET
═══════════════════════════════════════ */
@media (max-width: 1024px) {
  .page-layout {
    grid-template-columns: 260px 1fr;
    gap: 20px;
    padding: 28px 0;
  }
  .brands-grid {
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
    gap: 16px;
  }
}

/* ═══════════════════════════════════════
   MOBILE  ≤ 768px
═══════════════════════════════════════ */
@media (max-width: 768px) {
  .all-brands-page {
    background: #f4f6f8;
  }

  /* — Filter trigger pill — */
  .mobile-filter-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
    width: 100%;
    margin: 16px 0 0;
    padding: 14px 20px;
    background: white;
    border: 1.5px solid rgba(27, 67, 50, 0.14);
    border-radius: 14px;
    color: #1b4332;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.07);
    transition: background 0.2s, transform 0.15s;
  }
  .mobile-filter-btn:active {
    background: #edf5f0;
    transform: scale(0.98);
  }

  /* — Semi-transparent overlay — */
  .filters-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(5, 20, 12, 0.5);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    z-index: 299;
  }

  /* — Slide-in drawer — */
  .page-layout {
    display: block;
    padding: 14px 0 48px;
  }
  .filters-column {
    position: fixed;
    inset: 0 auto 0 0;
    width: min(340px, 92vw);
    z-index: 300;
    transform: translateX(-110%);
    transition: transform 0.38s cubic-bezier(0.19, 1, 0.22, 1);
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }
  .filters-column.show-mobile {
    transform: translateX(0);
  }
  .filters-sticky {
    position: static;
    min-height: 100%;
    border-radius: 0;
    padding: 22px 18px 60px;
    box-shadow: 6px 0 40px rgba(0, 0, 0, 0.18);
  }

  /* — Close button — */
  .mobile-filter-close {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    margin: 0 0 18px auto;
    border-radius: 10px;
    background: #f1f3f5;
    border: 1px solid #dee2e6;
    color: #495057;
    cursor: pointer;
    transition: background 0.2s, transform 0.15s;
  }
  .mobile-filter-close:active {
    background: #e2e6ea;
    transform: scale(0.92);
  }

  /* — Topbar — */
  .topbar {
    flex-wrap: wrap;
    gap: 10px;
    padding: 12px 14px;
    border-radius: 14px;
    margin-bottom: 14px;
  }
  .topbar-left,
  .topbar-right {
    width: 100%;
  }
  .results-badge {
    width: 100%;
    justify-content: center;
    padding: 9px 14px;
    font-size: 13px;
  }
  .topbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .sort-label { flex-shrink: 0; }
  .sort-select {
    flex: 1;
    padding: 10px 12px;
  }

  /* — Brand cards grid: 2 columns — */
  .brands-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 28px;
  }
}

/* ═══════════════════════════════════════
   SMALL PHONES  ≤ 400px
═══════════════════════════════════════ */
@media (max-width: 400px) {
  .brands-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}
</style>
