<!-- src/views/Brand.vue -->
<template>
  <div class="brand-page">
    <!-- ── Loading ── -->
    <div v-if="loading" class="brand-loading">
      <div class="brand-loading-spinner"></div>
      <p>Загрузка бренда...</p>
    </div>

    <!-- ── Error ── -->
    <div v-else-if="error" class="brand-error">
      <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <h3>{{ error }}</h3>
      <router-link to="/brands" class="brand-back-btn">← Все бренды</router-link>
    </div>

    <!-- ── Content ── -->
    <template v-else-if="brand">
      <!-- Hero -->
      <div class="brand-hero">
        <div class="brand-hero-bg"></div>
        <div class="brand-hero-inner container">
          <router-link to="/brands" class="brand-hero-back">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
            Бренды
          </router-link>
          <div class="brand-hero-card">
            <div class="brand-hero-logo" v-if="brand.image">
              <img :src="getImageUrl(brand.image)" :alt="brand.name" />
            </div>
            <div class="brand-hero-logo brand-hero-logo--placeholder" v-else>
              {{ brand.name?.charAt(0) }}
            </div>
            <div class="brand-hero-info">
              <h1>{{ brand.name }}</h1>
              <p v-if="brand.description" class="brand-hero-desc" v-html="formatContent(brand.description)"></p>
              <div class="brand-hero-stats">
                <span class="brand-hero-stat">
                  <strong>{{ pagination.total }}</strong> {{ pluralize(pagination.total) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main content -->
      <div class="container brand-container">
        <!-- Mobile filter trigger -->
        <button class="mobile-filter-btn" @click="showFilters = true">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="4" y1="6" x2="20" y2="6"/>
            <line x1="4" y1="12" x2="20" y2="12"/>
            <line x1="4" y1="18" x2="20" y2="18"/>
          </svg>
          Фильтры
          <span v-if="activeFilterCount" class="filter-badge">{{ activeFilterCount }}</span>
        </button>

        <!-- Overlay -->
        <transition name="fade">
          <div v-if="showFilters" class="filters-overlay" @click="showFilters = false"></div>
        </transition>

        <div class="page-layout">
          <!-- ── Filters sidebar ── -->
          <aside class="filters-column" :class="{ 'show-mobile': showFilters }">
            <div class="panel">
              <button class="mobile-filter-close" @click="showFilters = false">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>

              <h3>
                Фильтры
                <button
                  v-if="activeFilterCount"
                  class="panel-reset-btn"
                  @click="resetFilters"
                  title="Сбросить все фильтры"
                >
                  Сбросить
                </button>
              </h3>

              <!-- Categories -->
              <div class="filter-group" v-if="brandCategories.length">
                <label>Категории</label>
                <div class="categories-list">
                  <label
                    v-for="c in brandCategories"
                    :key="c.slug"
                    class="category-item"
                  >
                    <input
                      type="checkbox"
                      :value="c.slug"
                      v-model="filters.categories"
                      @change="applyFilters"
                    />
                    <span>{{ c.name }}</span>
                  </label>
                </div>
              </div>

              <!-- Tags -->
              <div class="filter-group" v-if="brandTags.length">
                <label>Теги</label>
                <div class="tags-list">
                  <label
                    v-for="t in brandTags"
                    :key="t.slug"
                    class="tag-item"
                  >
                    <input
                      type="checkbox"
                      :value="t.slug"
                      v-model="filters.tags"
                      @change="applyFilters"
                    />
                    <span>{{ t.name }}</span>
                  </label>
                </div>
              </div>

              <!-- Price (untouched) -->
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

              <div class="filter-actions">
                <button class="btn muted" @click="resetFilters">Сбросить</button>
                <button class="btn primary" @click="showFilters = false">Применить</button>
              </div>
            </div>
          </aside>

          <!-- ── Products ── -->
          <section class="brand-products-col">
            <div class="products-topbar">
              <span class="products-topbar-count" v-if="!loading">
                {{ pagination.total }} {{ pluralize(pagination.total) }}
              </span>
              <div class="products-topbar-sort">
                <select v-model="filters.ordering" @change="applyFilters" class="sort-select-inline">
                  <option value="-created_at">Новинки</option>
                  <option value="price">Цена ↑</option>
                  <option value="-price">Цена ↓</option>
                  <option value="name">По названию</option>
                </select>
              </div>
            </div>

            <div v-if="productsLoading" class="products-skeleton">
              <div v-for="n in 6" :key="n" class="skeleton-card"></div>
            </div>

            <div v-else-if="products.length === 0" class="brand-empty">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <p>Товары не найдены</p>
              <button class="btn muted" @click="resetFilters">Сбросить фильтры</button>
            </div>

            <template v-else>
              <ProductGrid :products="products" />
              <Pagination
                v-if="pagination.totalPages > 1"
                :current-page="pagination.page"
                :total-pages="pagination.totalPages"
                @change="changePage"
              />
            </template>
          </section>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from "vue";
import { useRoute } from "vue-router";
import { api, brandsAPI, getImageUrl } from "@/api";
import type { Brand, Product } from "@/types";
import ProductGrid from "@/components/ProductGrid.vue";
import Pagination from "@/components/Pagination.vue";
import PriceFilter from "@/components/PriceFilter.vue";

const route = useRoute();

// ── State ─────────────────────────────────────────────────────────────────
const brand        = ref<Brand | null>(null);
const products     = ref<Product[]>([]);
const loading      = ref(true);
const productsLoading = ref(false);
const error        = ref<string | null>(null);
const showFilters  = ref(false);

const brandCategories = ref<any[]>([]);
const brandTags       = ref<any[]>([]);

// Price range bounds (populated per brand, drives the PriceFilter slider)
const priceRange = reactive({ min: null as number | null, max: null as number | null });

// Debounce handle for price input changes
let priceDebounceTimer: ReturnType<typeof setTimeout> | null = null;

const filters = reactive({
  categories: [] as string[],
  tags:       [] as string[],
  priceMin:   null as number | null,
  priceMax:   null as number | null,
  ordering:   "-created_at",
});

const pagination = reactive({
  page:       1,
  pageSize:   12,
  totalPages: 1,
  total:      0,
});

// ── Computed ───────────────────────────────────────────────────────────────

/**
 * True when the user has narrowed the price slider away from the full range.
 * Counts as a single filter regardless of whether min, max, or both changed.
 */
const isPriceFiltered = computed(() => {
  if (priceRange.min === null || priceRange.max === null) return false;
  const lo = filters.priceMin ?? priceRange.min;
  const hi = filters.priceMax ?? priceRange.max;
  return lo > priceRange.min || hi < priceRange.max;
});

const activeFilterCount = computed(() =>
  filters.categories.length +
  filters.tags.length +
  (isPriceFiltered.value ? 1 : 0)
);

// ── Helpers ────────────────────────────────────────────────────────────────
const formatContent = (content: string): string =>
  content ? content.replace(/\n/g, "<br>") : "";

const pluralize = (count: number): string => {
  const cases  = [2, 0, 1, 1, 1, 2];
  const titles = ["товар", "товара", "товаров"];
  return titles[
    count % 100 > 4 && count % 100 < 20
      ? 2
      : cases[count % 10 < 5 ? count % 10 : 5]
  ];
};

// ── API helpers ────────────────────────────────────────────────────────────
const buildBrandParams = () => {
  const params: Record<string, any> = {
    page:      pagination.page,
    page_size: pagination.pageSize,
    ordering:  filters.ordering,
  };
  if (filters.categories.length) params.category  = filters.categories.join(",");
  if (filters.tags.length)       params.tag        = filters.tags.join(",");
  if (filters.priceMin != null)  params.price_min  = filters.priceMin;
  if (filters.priceMax != null)  params.price_max  = filters.priceMax;
  return params;
};

const loadProducts = async (slug: string): Promise<void> => {
  try {
    productsLoading.value = true;
    const response = await brandsAPI.getProducts(slug, buildBrandParams());
    const data = response.data;
    products.value      = data.results || [];
    pagination.total      = Number(data.count ?? 0);
    pagination.totalPages = Math.max(1, Math.ceil(pagination.total / pagination.pageSize));
  } catch (err) {
    console.error("Ошибка загрузки товаров:", err);
    products.value = [];
  } finally {
    productsLoading.value = false;
  }
};

const loadBrandCategories = async (slug: string): Promise<void> => {
  try {
    const res = await brandsAPI.getCategories(slug);
    brandCategories.value = res.data || [];
  } catch (e) {
    console.error("Ошибка загрузки категорий:", e);
  }
};

const loadBrandTags = async (slug: string): Promise<void> => {
  try {
    const res = await brandsAPI.getTags(slug);
    const data = res.data || [];

    // The API may return grouped tags — flatten them, de-duplicating by id.
    if (Array.isArray(data) && data.length > 0 && (data[0] as any).group_name) {
      const flat: any[]       = [];
      const seen = new Set<number>();
      for (const group of data as any[]) {
        for (const tag of (group.tags ?? []) as any[]) {
          if (!seen.has(tag.id)) { flat.push(tag); seen.add(tag.id); }
        }
      }
      brandTags.value = flat;
    } else {
      brandTags.value = data;
    }
  } catch (e) {
    console.error("Ошибка загрузки тегов:", e);
  }
};

// Price filter (untouched — already working correctly)
const fetchBrandPriceRange = async (slug: string): Promise<void> => {
  try {
    const res = await api.get("/products/price-range/", { params: { brand: slug } });
    if (res.data.min_price != null) priceRange.min = Math.floor(Number(res.data.min_price));
    if (res.data.max_price != null) priceRange.max = Math.ceil(Number(res.data.max_price));
  } catch (e) {
    console.error("Ошибка загрузки диапазона цен:", e);
  }
};

const onPriceFilterChange = (value: { min: number | null; max: number | null }) => {
  filters.priceMin = value.min;
  filters.priceMax = value.max;
  if (priceDebounceTimer) clearTimeout(priceDebounceTimer);
  priceDebounceTimer = setTimeout(() => applyFilters(), 400);
};

// ── Actions ────────────────────────────────────────────────────────────────
const loadBrand = async (): Promise<void> => {
  const slug = route.params.slug as string;
  if (!slug) { error.value = "Бренд не найден"; loading.value = false; return; }
  try {
    loading.value = true;
    error.value   = null;
    const brandResponse = await brandsAPI.getBySlug(slug);
    brand.value = brandResponse.data;
    await Promise.all([
      loadBrandCategories(slug),
      loadBrandTags(slug),
      fetchBrandPriceRange(slug),
    ]);
    await loadProducts(slug);
  } catch (err: any) {
    error.value =
      err.response?.status === 404
        ? "Бренд не найден"
        : "Не удалось загрузить бренд";
  } finally {
    loading.value = false;
  }
};

const applyFilters = async (): Promise<void> => {
  pagination.page = 1;
  await loadProducts(route.params.slug as string);
};

const resetFilters = async (): Promise<void> => {
  filters.categories = [];
  filters.tags       = [];
  filters.priceMin   = null;
  filters.priceMax   = null;
  filters.ordering   = "-created_at";
  await applyFilters();
};

const changePage = async (page: number): Promise<void> => {
  if (page < 1 || page > pagination.totalPages) return;
  pagination.page = page;
  await loadProducts(route.params.slug as string);
  window.scrollTo({ top: 0, behavior: "smooth" });
};

// ── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(() => loadBrand());

onUnmounted(() => {
  if (priceDebounceTimer) clearTimeout(priceDebounceTimer);
});

// When navigating between brand pages, fully reset UI state before reloading.
watch(
  () => route.params.slug,
  () => {
    // Reset filter state so stale values from the previous brand don't bleed over.
    filters.categories = [];
    filters.tags       = [];
    filters.priceMin   = null;
    filters.priceMax   = null;
    filters.ordering   = "-created_at";
    // Hide the PriceFilter slider until the new brand's range arrives.
    priceRange.min = null;
    priceRange.max = null;
    pagination.page = 1;
    loadBrand();
  }
);
</script>

<style scoped>
/* ── Page base ── */
.brand-page {
  min-height: 100vh;
  background: #f4f6f8;
}

/* ── Loading ── */
.brand-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 16px;
  color: #6b7280;
}
.brand-loading-spinner {
  width: 44px; height: 44px;
  border: 3px solid #e5e7eb;
  border-top-color: #1b4332;
  border-radius: 50%;
  animation: bspin 0.8s linear infinite;
}
@keyframes bspin { to { transform: rotate(360deg); } }

/* ── Error ── */
.brand-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 16px;
  color: #6b7280;
  text-align: center;
  padding: 40px 20px;
}
.brand-back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: #1b4332;
  color: white;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
}

/* ── Hero ── */
.brand-hero {
  position: relative;
  background: linear-gradient(135deg, #081c15 0%, #1b4332 55%, #2d6a4f 100%);
  padding: 48px 0 40px;
  overflow: hidden;
}
.brand-hero-bg {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 15% 60%, rgba(212,165,116,0.13) 0%, transparent 50%),
    radial-gradient(circle at 85% 25%, rgba(64,145,108,0.14) 0%, transparent 50%);
  pointer-events: none;
}
.brand-hero-inner {
  position: relative;
  z-index: 1;
}
.brand-hero-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: rgba(255,255,255,0.55);
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  margin-bottom: 24px;
  transition: color 0.2s;
}
.brand-hero-back:hover { color: rgba(255,255,255,0.9); }

.brand-hero-card {
  display: flex;
  align-items: center;
  gap: 28px;
}
.brand-hero-logo {
  width: 96px; height: 96px;
  background: rgba(255,255,255,0.06);
  border-radius: 20px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.25);
}
.brand-hero-logo img { width: 100%; height: 100%; object-fit: contain; padding: 12px; }
.brand-hero-logo--placeholder {
  background: linear-gradient(135deg, #2d6a4f, #40916c);
  font-size: 36px;
  font-weight: 800;
  color: white;
}
.brand-hero-info h1 {
  font-size: clamp(24px, 4vw, 36px);
  font-weight: 800;
  color: #fff;
  margin: 0 0 8px;
  letter-spacing: -0.5px;
}
.brand-hero-desc {
  color: rgba(255,255,255,0.65);
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 14px;
  max-width: 560px;
}
.brand-hero-stats { display: flex; gap: 16px; }
.brand-hero-stat {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 20px;
  padding: 5px 14px;
  font-size: 13px;
  color: rgba(255,255,255,0.85);
}
.brand-hero-stat strong { color: #d4a574; font-weight: 700; }

/* ── Container ── */
.brand-container {
  padding-top: 8px;
  padding-bottom: 60px;
}

/* ── Products section ── */
.brand-products-col { min-width: 0; }

.products-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  margin-bottom: 20px;
  gap: 12px;
  flex-wrap: wrap;
}
.products-topbar-count {
  font-size: 14px;
  color: #4b5563;
  font-weight: 500;
}
.sort-select-inline {
  padding: 8px 12px;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  font-size: 13px;
  color: #374151;
  background: #f9fafb;
  cursor: pointer;
}
.sort-select-inline:focus { outline: none; border-color: #40916c; }

/* ── Skeleton ── */
.products-skeleton {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}
.skeleton-card {
  height: 280px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: 16px;
  animation: shimmer 1.4s infinite;
}
@keyframes shimmer { to { background-position: -200% 0; } }

/* ── Empty state ── */
.brand-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 60px 20px;
  text-align: center;
  background: white;
  border-radius: 16px;
  color: #9ca3af;
}
.brand-empty p { font-size: 15px; margin: 0; }

/* ── Panel reset pill (lives inside the global panel h3 flex row) ── */
.panel-reset-btn {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border: none;
  background: #fef3c7;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: #92400e;
  cursor: pointer;
  text-transform: none;
  letter-spacing: 0;
  transition: background 0.2s;
  flex-shrink: 0;
}
.panel-reset-btn:hover { background: #fde68a; }

/* ── Filter badge on the mobile trigger ── */
.filter-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 5px;
  background: #1b4332;
  color: white;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
}

/* ── Mobile breakpoints ── */
@media (max-width: 768px) {
  .brand-hero { padding: 32px 0 28px; }
  .brand-hero-card { gap: 16px; }
  .brand-hero-logo { width: 72px; height: 72px; border-radius: 16px; }
  .brand-hero-info h1 { font-size: 22px; }
  .brand-hero-desc { font-size: 13px; }
  .products-topbar { padding: 10px 12px; }
  .products-topbar-count { font-size: 13px; }
  .sort-select-inline { font-size: 13px; padding: 7px 10px; }
  .products-skeleton { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .skeleton-card { height: 220px; }
}

@media (max-width: 400px) {
  .brand-hero-card { flex-direction: column; align-items: flex-start; gap: 12px; }
  .brand-hero-back { margin-bottom: 16px; }
}
</style>
