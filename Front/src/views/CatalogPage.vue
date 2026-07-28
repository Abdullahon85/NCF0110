<!-- src/views/CatalogPage.vue -->
<template>
  <div class="catalog-page">

    <!-- ── Hero ── -->
    <div class="catalog-hero" v-if="!searchQuery">
      <div class="container">
        <span class="catalog-hero-label">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          Все категории
        </span>
        <h1 class="catalog-hero-title">Каталог товаров</h1>
        <p class="catalog-hero-sub">Профессиональное оборудование систем безопасности</p>
      </div>
    </div>

    <div class="container catalog-body">

      <!-- ══ SEARCH RESULTS ══ -->
      <div v-if="searchQuery" class="search-results-section">
        <div class="search-header">
          <h1>Результаты поиска</h1>
          <div class="search-query-display">
            <span class="search-label">Запрос:</span>
            <span class="search-value">"{{ searchQuery }}"</span>
            <router-link to="/catalog" class="clear-search">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
              Очистить
            </router-link>
          </div>
        </div>

        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>Поиск товаров...</p>
        </div>

        <div v-else-if="searchResults.length === 0" class="no-results-container">
          <div class="no-results-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="11" y1="16" x2="11.01" y2="16"/>
            </svg>
          </div>
          <h2>Ничего не найдено</h2>
          <p>По запросу <strong>"{{ searchQuery }}"</strong> товары не найдены</p>
          <router-link to="/catalog" class="back-to-catalog">Вернуться в каталог</router-link>
        </div>

        <div v-else>
          <div class="search-results-info">
            Найдено товаров: <strong>{{ searchResults.length }}</strong>
          </div>
          <div class="products-grid">
            <ProductCard v-for="product in searchResults" :key="product.id" :product="product" />
          </div>
        </div>
      </div>

      <!-- ══ CATALOG ══ -->
      <div v-else>
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>Загрузка каталога...</p>
        </div>

        <div v-else-if="error" class="error-message">{{ error }}</div>

        <div v-else-if="categories.length" class="categories-section">
          <div
            v-for="(category, index) in categories"
            :key="category.id"
            class="category-block"
          >
            <!-- Category header -->
            <div class="category-header">
              <div class="category-header-left">
                <span class="category-index">{{ String(index + 1).padStart(2, '0') }}</span>
                <h2>{{ category.name }}</h2>
              </div>
              <router-link :to="`/catalog/${category.slug}`" class="view-category-link">
                Все товары ({{ category.products_count }})
                <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
                  <path d="M4 10h12M11 5l5 5-5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </router-link>
            </div>

            <!-- Category card — always shown as a centered preview -->
            <div class="no-subcategories">
              <router-link :to="`/catalog/${category.slug}`" class="category-main-link">
                <div class="category-main-image" v-if="category.image">
                  <img :src="category.image" :alt="category.name" />
                </div>
                <div v-else class="placeholder-image">
                  <span>{{ category.name[0] }}</span>
                </div>
                <div class="category-main-text">
                  <span class="category-main-name">{{ category.name }}</span>
                  <span class="category-main-cta">
                    Смотреть товары
                    <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
                      <path d="M4 10h12M11 5l5 5-5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </span>
                </div>
              </router-link>
            </div>
          </div>
        </div>

        <div v-else class="empty-catalog">
          <p>Каталог пуст</p>
        </div>
      </div>

    </div><!-- /catalog-body -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import { useRoute } from "vue-router";
import { categoriesAPI, productsAPI } from "@/api";
import type { Category, Product } from "@/types";
import ProductCard from "@/components/ProductCard.vue";

const route = useRoute();
const categories = ref<Category[]>([]);
const searchResults = ref<Product[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

const searchQuery = computed(() => (route.query.search as string) || "");

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

const loadSearchResults = async (query: string) => {
  try {
    loading.value = true;
    const response = await productsAPI.search(query, { page_size: 100 });
    const payload = "results" in response.data ? response.data.results : response.data;
    searchResults.value = Array.isArray(payload) ? payload : [];
  } catch (err) {
    console.error("Ошибка поиска товаров:", err);
    searchResults.value = [];
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  try {
    loading.value = true;
    await loadCategories();
    if (searchQuery.value) await loadSearchResults(searchQuery.value);
  } catch (err) {
    error.value = "Ошибка загрузки данных";
    console.error(err);
  } finally {
    loading.value = false;
  }
});

watch(
  () => route.query.search,
  async (newSearch) => {
    if (newSearch) await loadSearchResults(newSearch as string);
    else searchResults.value = [];
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
);
</script>

<style scoped>
/* ── Hero ── */
.catalog-hero {
  background: linear-gradient(135deg, #0d2818 0%, #1b4332 50%, #1a3a2a 100%);
  padding: 56px 0 52px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.catalog-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 60% 80% at 20% 50%, rgba(212,165,116,0.07) 0%, transparent 70%),
    radial-gradient(ellipse 50% 70% at 80% 50%, rgba(27,67,50,0.4) 0%, transparent 70%);
  pointer-events: none;
}

.catalog-hero .container {
  position: relative;
  z-index: 1;
}

.catalog-hero-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border: 1px solid rgba(212,165,116,0.35);
  border-radius: 999px;
  color: rgba(212,165,116,0.9);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 18px;
}

.catalog-hero-title {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 800;
  color: #fff;
  margin: 0 0 12px;
  letter-spacing: -0.02em;
}

.catalog-hero-sub {
  font-size: 1rem;
  color: rgba(255,255,255,0.6);
  margin: 0;
}

/* ── Body ── */
.catalog-body {
  padding-top: 48px;
  padding-bottom: 64px;
}

/* ── Categories section ── */
.categories-section {
  display: flex;
  flex-direction: column;
  gap: 32px;
}
.categories-section {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(560px, 1fr));
    gap: 32px;
  }
@media (max-width: 768px){
  .categories-section{
  display: flex;
  flex-direction: column;
  }
}
/* ── Category block ── */
.category-block {
  background: #fff;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.06);
  border: 1px solid rgba(0,0,0,0.06);
  border-left: 4px solid var(--primary, #1b4332);
}

/* ── Category header ── */
.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.category-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.category-index {
  font-size: 11px;
  font-weight: 700;
  color: var(--primary, #1b4332);
  background: rgba(27,67,50,0.08);
  border-radius: 8px;
  padding: 4px 8px;
  letter-spacing: 0.04em;
  flex-shrink: 0;
}

.category-header h2 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #111;
  margin: 0;
}

.view-category-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(27,67,50,0.07);
  color: var(--primary, #1b4332);
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  transition: background 0.18s ease, color 0.18s ease;
  flex-shrink: 0;
}

.view-category-link:hover {
  background: var(--primary, #1b4332);
  color: #fff;
}

/* ── Subcategories grid ── */
.subcategories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

/* ── Subcategory card ── */
.subcategory-card {
  background: #f8faf8;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.subcategory-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 28px rgba(27,67,50,0.12);
  border-color: rgba(27,67,50,0.2);
}

/* ── Category card (centered preview) ── */
.no-subcategories {
  margin-top: 4px;
}

.category-main-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 32px 24px 28px;
  background: #f8faf8;
  border-radius: 14px;
  border: 1px dashed rgba(27,67,50,0.2);
  text-decoration: none;
  color: inherit;
  text-align: center;
  transition: background 0.18s ease, border-color 0.18s ease;
}

.category-main-link:hover {
  background: rgba(27,67,50,0.05);
  border-color: rgba(27,67,50,0.35);
}

.category-main-image {
  width: 96px;
  height: 96px;
  border-radius: 14px;
  overflow: hidden;
  background: #fff;
  flex-shrink: 0;
  border: 1px solid rgba(0,0,0,0.06);
}

.category-main-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 10px;
  transition: transform 0.25s ease;
}

.category-main-link:hover .category-main-image img {
  transform: scale(1.06);
}

.placeholder-image {
  width: 96px;
  height: 96px;
  border-radius: 14px;
  background: var(--primary-gradient, linear-gradient(135deg,#1b4332,#2d6a4f));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 2rem;
  font-weight: 800;
  flex-shrink: 0;
}

.category-main-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.category-main-name {
  font-size: 1rem;
  font-weight: 700;
  color: #111;
}

.category-main-cta {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--primary, #1b4332);
}

/* ── Mobile ── */
@media (max-width: 768px) {
  .catalog-hero {
    padding: 36px 0 32px;
  }

  .catalog-hero-title {
    font-size: 1.7rem;
  }

  .catalog-body {
    padding-top: 24px;
    padding-bottom: 40px;
  }

  .category-block {
    padding: 18px 16px;
    border-radius: 14px;
    border-left-width: 3px;
  }

  .categories-section {
    gap: 16px;
  }

  .category-header {
    margin-bottom: 16px;
    padding-bottom: 12px;
    flex-wrap: wrap;
    gap: 10px;
  }

  .category-header h2 {
    font-size: 1rem;
  }

}
</style>
