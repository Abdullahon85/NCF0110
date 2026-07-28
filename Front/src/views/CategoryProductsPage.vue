<template>
  <div class="page-layout container">
    <!-- Breadcrumb -->
    <nav class="breadcrumb">
      <router-link to="/">Главная</router-link>
      <span class="separator">›</span>
      <router-link to="/catalog">Каталог</router-link>
      <span class="separator">›</span>
      <span class="current">{{ categoryName }}</span>
    </nav>

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

    <aside class="filters-column" :class="{ 'show-mobile': showFilters }">
      <div class="panel">
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
        <h3>Фильтры</h3>

        <!-- Фильтр цены -->
        <PriceFilter
          v-if="priceRange.min !== null && priceRange.max !== null"
          :min="priceRange.min"
          :max="priceRange.max"
          :model-value="{
            min: filters.priceMin ?? priceRange.min,
            max: filters.priceMax ?? priceRange.max,
          }"
          @update:model-value="onPriceFilterChange"
        />

        <!-- Фильтр брендов -->
        <div v-if="brandsOptions.length > 0" class="filter-group">
          <label>Бренды</label>
          <div class="brands-list">
            <label
              v-for="brand in brandsOptions"
              :key="brand.slug"
              class="brand-item"
            >
              <input
                type="checkbox"
                :value="brand.slug"
                :checked="filters.brands.includes(brand.slug)"
                @change="toggleBrand(brand.slug)"
              />
              <span>{{ brand.name }}<span v-if="brand.product_count !== undefined" class="tag-count">&nbsp;({{ brand.product_count }})</span></span>
            </label>
          </div>
        </div>

        <!-- Фильтр по группам тегов -->
        <div v-for="group in tagGroups" :key="group.id" class="filter-group">
          <label>{{ group.group_name }}</label>
          <div class="tags-list">
            <label
              v-for="tag in group.tags.filter(
                (t) => (t.product_count ?? 1) > 0,
              )"
              :key="tag.slug"
              class="tag-item"
            >
              <input
                type="checkbox"
                :value="tag.slug"
                :checked="filters.tags.includes(tag.slug)"
                @change="toggleTag(tag.slug)"
              />
              <span
                >{{ tag.name
                }}<span v-if="tag.product_count !== undefined" class="tag-count"
                  >&nbsp;({{ tag.product_count }})</span
                ></span
              >
            </label>
          </div>
        </div>

        <!-- Действия с фильтрами -->
        <div class="filter-actions">
          <button @click="resetFilters" class="btn muted">Сбросить</button>
          <button @click="showFilters = false" class="btn primary">
            Применить
          </button>
        </div>
      </div>
    </aside>

    <main class="products-column">
      <!-- Панель управления -->
      <div class="topbar">
        <div class="sort">
          <label>Сортировка:</label>
          <select v-model="filters.ordering" @change="onOrderingChange">
            <option value="-created_at">Сначала новые</option>
            <option value="created_at">Сначала старые</option>
            <option value="price">Сначала дешевые</option>
            <option value="-price">Сначала дорогие</option>
            <option value="name">По названию (А-Я)</option>
            <option value="-name">По названию (Я-А)</option>
          </select>
        </div>

        <!-- Поисковик -->
        <div class="search-bar">
          <input
            type="text"
            v-model="searchInput"
            @input="onSearchInput"
            @keyup.enter="onSearchSubmit"
            placeholder="Поиск товаров..."
          />
          <button @click="onSearchSubmit" class="btn-search">
            <svg
              width="18"
              height="18"
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

        <div class="only-available">
          <label>
            <input
              type="checkbox"
              v-model="filters.onlyAvailable"
              @change="onAvailabilityChange"
            />
            Только в наличии
          </label>
        </div>
      </div>

      <!-- Контент -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Загрузка товаров...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button @click="loadProducts" class="btn primary">Повторить</button>
      </div>

      <div v-else-if="products.length === 0" class="empty-state">
        <p>Товары не найдены</p>
        <button @click="resetFilters" class="btn muted">
          Сбросить фильтры
        </button>
      </div>

      <div v-else>
        <ProductGrid :products="products" />

        <Pagination
          v-if="pagination.totalPages > 1"
          :current-page="pagination.page"
          :total-pages="pagination.totalPages"
          @change="changePage"
        />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from "vue";
import { useRoute } from "vue-router";
import { productsAPI, categoriesAPI } from "@/api";
import type { Product, Brand, ProductTagGroup, Tag } from "@/types";
import PriceFilter from "@/components/PriceFilter.vue";
import ProductGrid from "@/components/ProductGrid.vue";
import Pagination from "@/components/Pagination.vue";

const route = useRoute();
const products = ref<Product[]>([]);
const brandsOptions = ref<Brand[]>([]);
const tagGroups = ref<ProductTagGroup[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const showFilters = ref(false);
const categoryName = ref<string>("");

const priceRange = reactive({
  min: null as number | null,
  max: null as number | null,
});

const filters = reactive({
  priceMin: null as number | null,
  priceMax: null as number | null,
  brands: [] as string[],
  tags: [] as string[],
  ordering: "-created_at" as string,
  onlyAvailable: false,
  search: "" as string,
});

const pagination = reactive({
  page: 1,
  pageSize: 12,
  totalPages: 1,
  total: 0,
});

// Отдельный инпут для поиска (для debounce)
const searchInput = ref("");

// Таймауты для debounce
let priceDebounceTimeout: ReturnType<typeof setTimeout> | null = null;
let searchDebounceTimeout: ReturnType<typeof setTimeout> | null = null;

// ============================================
// LOCALSTORAGE — сохранение / восстановление фильтров
// ============================================

const storageKey = () => `catalog_filters_${categorySlug.value}`;

const saveFiltersToStorage = () => {
  try {
    localStorage.setItem(
      storageKey(),
      JSON.stringify({
        priceMin: filters.priceMin,
        priceMax: filters.priceMax,
        brands: [...filters.brands],
        tags: [...filters.tags],
        ordering: filters.ordering,
        onlyAvailable: filters.onlyAvailable,
        search: filters.search,
        page: pagination.page,
      }),
    );
  } catch {}
};

const restoreFiltersFromStorage = (): boolean => {
  try {
    const raw = localStorage.getItem(storageKey());
    if (!raw) return false;
    const s = JSON.parse(raw);
    filters.ordering = s.ordering ?? "-created_at";
    filters.brands = Array.isArray(s.brands) ? s.brands.filter(Boolean) : [];
    filters.tags = Array.isArray(s.tags) ? s.tags.filter(Boolean) : [];
    filters.onlyAvailable = s.onlyAvailable ?? false;
    filters.search = s.search ?? "";
    searchInput.value = filters.search;
    pagination.page = s.page ?? 1;
    // Цены: восстанавливаем как есть; loadPriceRange уже не перезапишет их (они не null)
    filters.priceMin = s.priceMin ?? null;
    filters.priceMax = s.priceMax ?? null;
    return true;
  } catch {
    return false;
  }
};

const clearFiltersFromStorage = () => {
  try { localStorage.removeItem(storageKey()); } catch {}
};

// ============================================
// COMPUTED
// ============================================
const categorySlug = computed(
  () => (route.params.categorySlug as string) || "",
);

// ============================================
// API ФУНКЦИИ
// ============================================

/**
 * Загрузка брендов для текущего каталога (с учётом активных фильтров тегов и цены)
 */
const loadBrands = async (): Promise<void> => {
  if (!categorySlug.value) return;
  try {
    const params: Record<string, any> = {};
    if (filters.tags.length > 0) {
      params.tag = filters.tags.join(',');
    }
    if (
      filters.priceMin !== null &&
      priceRange.min !== null &&
      filters.priceMin > priceRange.min
    ) {
      params.price_min = filters.priceMin;
    }
    if (
      filters.priceMax !== null &&
      priceRange.max !== null &&
      filters.priceMax < priceRange.max
    ) {
      params.price_max = filters.priceMax;
    }
    const response = await categoriesAPI.getBrands(categorySlug.value, params);
    brandsOptions.value = response.data || [];
  } catch (err) {
    console.error("Ошибка загрузки брендов:", err);
    brandsOptions.value = [];
  }
};

/**
 * Загрузка информации о каталоге
 */
const loadCategoryInfo = async (): Promise<void> => {
  if (!categorySlug.value) return;
  try {
    const response = await categoriesAPI.getBySlug(categorySlug.value);
    categoryName.value = response.data.name || "";
  } catch (err) {
    console.error("Ошибка загрузки каталога:", err);
    categoryName.value = "";
  }
};

/**
 * Загрузка тегов для текущего каталога (с учётом текущего фильтра цены)
 */
const loadTags = async (): Promise<void> => {
  if (!categorySlug.value) return;
  try {
    const params: { price_min?: number; price_max?: number; selected_tags?: string; brand?: string } = {};
    if (
      filters.priceMin !== null &&
      priceRange.min !== null &&
      filters.priceMin > priceRange.min
    ) {
      params.price_min = filters.priceMin;
    }
    if (
      filters.priceMax !== null &&
      priceRange.max !== null &&
      filters.priceMax < priceRange.max
    ) {
      params.price_max = filters.priceMax;
    }
    if (filters.tags.length > 0) {
      params.selected_tags = filters.tags.join(',');
    }
    if (filters.brands.length > 0) {
      params.brand = filters.brands.join(',');
    }
    const response = await categoriesAPI.getTags(categorySlug.value, params);
    const data = response.data;

    // Проверяем формат ответа
    if (Array.isArray(data) && data.length > 0) {
      // Если это массив групп тегов
      if ("group_name" in data[0]) {
        tagGroups.value = data as ProductTagGroup[];
      } else {
        // Если это плоский массив тегов - оборачиваем в одну группу
        tagGroups.value = [
          {
            id: 0,
            group_name: "Теги",
            tags: data as Tag[],
          },
        ];
      }
    } else {
      tagGroups.value = [];
    }
  } catch (err) {
    console.error("Ошибка загрузки тегов:", err);
    tagGroups.value = [];
  }
};

/**
 * Загрузка диапазона цен для текущего каталога
 */
const loadPriceRange = async (): Promise<void> => {
  if (!categorySlug.value) return;
  try {
    const response = await productsAPI.getPriceRange(categorySlug.value);
    const min = response.data?.min_price ?? null;
    const max = response.data?.max_price ?? null;

    priceRange.min = min;
    priceRange.max = max;

    // Инициализируем фильтры цены, если они еще не установлены
    if (filters.priceMin === null) {
      filters.priceMin = min;
    }
    if (filters.priceMax === null) {
      filters.priceMax = max;
    }
  } catch (err) {
    console.error("Ошибка загрузки диапазона цен:", err);
    priceRange.min = null;
    priceRange.max = null;
  }
};

/**
 * Построение параметров для API запроса
 */
const buildApiParams = (): Record<string, any> => {
  const params: Record<string, any> = {
    category: categorySlug.value,
    ordering: filters.ordering,
    page: pagination.page,
    page_size: pagination.pageSize,
  };

  // Цена
  if (
    filters.priceMin !== null &&
    priceRange.min !== null &&
    filters.priceMin > priceRange.min
  ) {
    params.price_min = filters.priceMin;
  }
  if (
    filters.priceMax !== null &&
    priceRange.max !== null &&
    filters.priceMax < priceRange.max
  ) {
    params.price_max = filters.priceMax;
  }

  // Бренды
  if (filters.brands.length > 0) {
    params.brand = filters.brands.join(",");
  }

  // Теги
  if (filters.tags.length > 0) {
    params.tag = filters.tags.join(",");
  }

  // Наличие
  if (filters.onlyAvailable) {
    params.is_available = "true";
  }

  // Поиск
  if (filters.search && filters.search.trim().length > 0) {
    params.search = filters.search.trim();
  }

  return params;
};

/**
 * Загрузка продуктов с учетом фильтров
 */
const loadProducts = async (): Promise<void> => {
  loading.value = true;
  error.value = null;

  try {
    const params = buildApiParams();
    const response = await productsAPI.getAll(params);
    const data = response.data || {};

    products.value = data.results || [];
    pagination.total = Number(data.count ?? 0);
    pagination.totalPages = Math.max(
      1,
      Math.ceil(pagination.total / pagination.pageSize),
    );

    // Если текущая страница больше доступных - возвращаемся на первую
    if (pagination.page > pagination.totalPages) {
      pagination.page = 1;
      await loadProducts();
    }
  } catch (err: any) {
    console.error("Ошибка загрузки товаров:", err);

    // Better error messages
    if (err.response?.status === 429) {
      error.value = "Слишком много запросов. Пожалуйста, подождите немного...";
    } else if (err.response?.status === 404) {
      error.value = "Каталог не найден";
    } else if (err.response?.status >= 500) {
      error.value = "Ошибка сервера. Попробуйте обновить страницу";
    } else if (!navigator.onLine) {
      error.value = "Проверьте подключение к интернету";
    } else {
      error.value = "Не удалось загрузить товары. Попробуйте позже.";
    }

    products.value = [];
  } finally {
    loading.value = false;
  }
};

// ============================================
// ОБРАБОТЧИКИ ФИЛЬТРОВ
// ============================================

/**
 * Изменение фильтра цены (с debounce)
 */
const onPriceFilterChange = (value: {
  min: number | null;
  max: number | null;
}) => {
  filters.priceMin = value.min;
  filters.priceMax = value.max;

  // Сбрасываем предыдущий таймер
  if (priceDebounceTimeout) {
    clearTimeout(priceDebounceTimeout);
  }

  // Запускаем новый таймер на 800ms
  priceDebounceTimeout = setTimeout(() => {
    pagination.page = 1;
    saveFiltersToStorage();
    loadProducts();
    loadTags();
    loadBrands();
  }, 800);
};

/**
 * Переключение бренда — реактивно обновляет теги и товары
 */
const toggleBrand = (brandSlug: string) => {
  const index = filters.brands.indexOf(brandSlug);
  if (index > -1) {
    filters.brands.splice(index, 1);
  } else {
    filters.brands.push(brandSlug);
  }
  pagination.page = 1;
  saveFiltersToStorage();
  loadProducts();
  loadTags();
};

/**
 * Переключение тега — реактивно обновляет бренды и товары
 */
const toggleTag = (tagSlug: string) => {
  const index = filters.tags.indexOf(tagSlug);
  if (index > -1) {
    filters.tags.splice(index, 1);
  } else {
    filters.tags.push(tagSlug);
  }
  pagination.page = 1;
  saveFiltersToStorage();
  loadProducts();
  loadTags();
  loadBrands();
};

/**
 * Изменение сортировки
 */
const onOrderingChange = () => {
  pagination.page = 1;
  saveFiltersToStorage();
  loadProducts();
};

/**
 * Изменение чекбокса "Только в наличии"
 */
const onAvailabilityChange = () => {
  pagination.page = 1;
  saveFiltersToStorage();
  loadProducts();
};

/**
 * Ввод в поле поиска (с debounce)
 */
const onSearchInput = () => {
  // Сбрасываем предыдущий таймер
  if (searchDebounceTimeout) {
    clearTimeout(searchDebounceTimeout);
  }

  // Запускаем новый таймер на 600ms
  searchDebounceTimeout = setTimeout(() => {
    filters.search = searchInput.value;
    pagination.page = 1;
    saveFiltersToStorage();
    loadProducts();
  }, 600);
};

/**
 * Нажатие Enter или кнопки поиска
 */
const onSearchSubmit = () => {
  if (searchDebounceTimeout) {
    clearTimeout(searchDebounceTimeout);
  }
  filters.search = searchInput.value;
  pagination.page = 1;
  saveFiltersToStorage();
  loadProducts();
};

/**
 * Сброс всех фильтров
 */
const resetFilters = () => {
  filters.ordering = "-created_at";
  filters.priceMin = priceRange.min;
  filters.priceMax = priceRange.max;
  filters.brands = [];
  filters.tags = [];
  filters.onlyAvailable = false;
  filters.search = "";
  searchInput.value = "";
  pagination.page = 1;
  showFilters.value = false;
  clearFiltersFromStorage();
  loadTags();
  loadBrands();
  loadProducts();
};

/**
 * Изменение страницы
 */
const changePage = (page: number) => {
  if (page < 1 || page > pagination.totalPages || page === pagination.page) {
    return;
  }
  pagination.page = page;
  saveFiltersToStorage();
  loadProducts();
  window.scrollTo({ top: 0, behavior: "smooth" });
};

// ============================================
// ЖИЗНЕННЫЙ ЦИКЛ
// ============================================

/**
 * Инициализация при монтировании
 */
onMounted(async () => {
  // Восстанавливаем сохранённые фильтры до первой загрузки
  restoreFiltersFromStorage();

  // Загружаем метаданные (loadPriceRange не перезапишет priceMin/Max, если они уже не null)
  await Promise.all([
    loadCategoryInfo(),
    loadBrands(),
    loadTags(),
    loadPriceRange(),
  ]);
  await loadProducts();
});

/**
 * Отслеживание изменения каталога
 */
watch(
  () => route.params.categorySlug,
  async (newSlug, oldSlug) => {
    if (newSlug === oldSlug) return;

    // Полный сброс состояния реактивных переменных
    products.value = [];
    brandsOptions.value = [];
    tagGroups.value = [];
    categoryName.value = "";
    priceRange.min = null;
    priceRange.max = null;
    filters.brands = [];
    filters.tags = [];
    filters.search = "";
    searchInput.value = "";
    filters.priceMin = null;
    filters.priceMax = null;
    filters.ordering = "-created_at";
    filters.onlyAvailable = false;
    pagination.page = 1;

    // Восстанавливаем сохранённые фильтры для новой категории (если есть)
    restoreFiltersFromStorage();

    await Promise.all([
      loadCategoryInfo(),
      loadBrands(),
      loadTags(),
      loadPriceRange(),
    ]);
    await loadProducts();
  },
);
</script>

<!-- Styles in main.css -->
