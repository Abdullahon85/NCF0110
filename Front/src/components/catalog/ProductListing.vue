<template>
  <div class="page-layout listing">
    <button class="mobile-filter-btn" type="button" @click="showFilters = true">
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        aria-hidden="true"
      >
        <line x1="4" y1="6" x2="20" y2="6" />
        <line x1="4" y1="12" x2="20" y2="12" />
        <line x1="4" y1="18" x2="20" y2="18" />
      </svg>
      Фильтры<span v-if="chips.length"> ({{ chips.length }})</span>
    </button>

    <transition name="fade">
      <div v-if="showFilters" class="filters-overlay show" @click="showFilters = false"></div>
    </transition>

    <aside class="filters-column" :class="{ 'show-mobile': showFilters }" aria-label="Фильтры">
      <div class="panel">
        <button
          class="mobile-filter-close"
          type="button"
          aria-label="Закрыть фильтры"
          @click="showFilters = false"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            aria-hidden="true"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
        <h3>Фильтры</h3>
        <FacetPanel
          v-if="facets"
          :facets="facets"
          :state="state"
          :hide="Object.keys(fixed)"
          @update="update"
        />
        <div class="filter-actions">
          <button class="btn muted" type="button" @click="clearFilters">Сбросить</button>
          <button class="btn primary" type="button" @click="showFilters = false">
            Показать {{ facets?.total ?? total }} {{ itemWord(facets?.total ?? total) }}
          </button>
        </div>
      </div>
    </aside>

    <main class="products-column">
      <ListingToolbar
        :total="total"
        :sort="state.sort"
        :per-page="state.perPage"
        :view="state.view"
        @sort="(sort) => update({ ...state, sort, page: 1 })"
        @per-page="(perPage) => update({ ...state, perPage, page: 1 })"
        @view="(view) => update({ ...state, view })"
      />
      <ActiveChips
        :chips="chips"
        @remove="(key) => update(removeChip(state, key))"
        @clear="clearFilters"
      />

      <div v-if="loading && !products.length" class="loading">
        <div class="spinner"></div>
        <p>Загрузка товаров...</p>
      </div>
      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button class="btn primary" type="button" @click="load">Повторить</button>
      </div>
      <div v-else-if="!products.length" class="empty-state">
        <p>Товары не найдены</p>
        <button v-if="chips.length" class="btn muted" type="button" @click="clearFilters">
          Сбросить фильтры
        </button>
      </div>
      <div v-else :class="{ 'is-loading': loading }">
        <ProductGrid :products="products" :view="state.view" />
        <Pagination
          v-if="totalPages > 1"
          :current-page="state.page"
          :total-pages="totalPages"
          @change="changePage"
        />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { productsAPI } from "@/api";
import type { Product } from "@/types";
import {
  activeChips,
  defaultState,
  parseCatalogQuery,
  removeChip,
  toApiParams,
  toRouteQuery,
  type CatalogFacets,
  type CatalogState,
} from "@/utils/catalogQuery";
import { itemWord } from "@/utils/cartOrder";
import ProductGrid from "@/components/ProductGrid.vue";
import Pagination from "@/components/Pagination.vue";
import FacetPanel from "./FacetPanel.vue";
import ListingToolbar from "./ListingToolbar.vue";
import ActiveChips from "./ActiveChips.vue";

// Every product list of the site (category, brand, search, promotions). Filters live in the
// address; `fixed` are parameters of the page itself (e.g. {category: "kamery"}).
const props = defineProps<{ fixed: Record<string, string> }>();

const route = useRoute();
const router = useRouter();
const state = computed(() => parseCatalogQuery(route.query as Record<string, any>));
const products = ref<Product[]>([]);
const total = ref(0);
const facets = ref<CatalogFacets | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);
const showFilters = ref(false);

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / state.value.perPage)));
const chips = computed(() => activeChips(state.value, facets.value));

function update(next: CatalogState, push = false) {
  const query = toRouteQuery(next);
  if (push) router.push({ query });
  else router.replace({ query });
}

function clearFilters() {
  const s = state.value;
  update({ ...defaultState(), sort: s.sort, perPage: s.perPage, view: s.view });
}

function changePage(page: number) {
  update({ ...state.value, page }, true);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// A slower, older answer must not overwrite a newer one (fast clicks on filters).
let requestId = 0;

async function load() {
  const id = ++requestId;
  loading.value = true;
  error.value = null;
  const params = toApiParams(state.value, props.fixed);
  // Facets do not depend on the page or the order of the list.
  const facetParams = { ...params };
  for (const key of ["page", "page_size", "sort"]) delete facetParams[key];
  try {
    const [list, groups] = await Promise.all([
      productsAPI.list(params),
      productsAPI.facets(facetParams),
    ]);
    if (id !== requestId) return;
    products.value = list.data.results;
    total.value = list.data.count;
    facets.value = groups.data;
    // The server shows the last page for a page number past the end: keep the address in step.
    if (list.data.page && list.data.page !== state.value.page) {
      update({ ...state.value, page: list.data.page });
    }
  } catch (e: any) {
    if (id !== requestId) return;
    error.value =
      e?.response?.status === 429
        ? "Слишком много запросов. Подождите немного и повторите."
        : "Не удалось загрузить товары. Проверьте интернет и повторите.";
  } finally {
    if (id === requestId) loading.value = false;
  }
}

// Compared as text: a parent re-render creates a new `fixed` object with the same content,
// which must not start a second load.
watch(
  () => [JSON.stringify(route.query), JSON.stringify(props.fixed)].join("|"),
  () => load(),
  { immediate: true },
);
</script>
