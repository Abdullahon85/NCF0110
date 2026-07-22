<template>
  <div class="compare-page container">
    <nav class="breadcrumb">
      <router-link to="/">Главная</router-link>
      <span class="separator">›</span>
      <span class="current">Сравнение</span>
    </nav>

    <div class="page-header">
      <h1 class="page-title">Сравнение товаров</h1>
      <span class="page-count">
        {{ compareStore.items.length }}&thinsp;/&thinsp;{{ MAX_COMPARE_ITEMS }}
      </span>
    </div>

    <!-- Empty state -->
    <div v-if="compareStore.items.length === 0" class="empty-state">
      <svg
        width="64"
        height="64"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
      >
        <line x1="18" y1="20" x2="18" y2="10" />
        <line x1="12" y1="20" x2="12" y2="4" />
        <line x1="6" y1="20" x2="6" y2="14" />
      </svg>
      <p>Вы ещё не добавили товары для сравнения</p>
      <router-link to="/catalog" class="btn primary"
        >Перейти в каталог</router-link
      >
    </div>

    <div v-else>
      <!-- Toolbar -->
      <div class="compare-toolbar">
        <label class="compare-diff-label">
          <input type="checkbox" v-model="showOnlyDiff" />
          <span>Показывать только различия</span>
        </label>

        <span v-if="compareStore.isFull" class="compare-limit-notice">
          Максимум {{ MAX_COMPARE_ITEMS }} товара
        </span>

        <button
          class="btn cmp-share-btn"
          @click="copyShareLink"
          :class="{ 'cmp-share-btn--copied': shareSuccess }"
        >
          <svg
            v-if="!shareSuccess"
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="18" cy="5" r="3" />
            <circle cx="6" cy="12" r="3" />
            <circle cx="18" cy="19" r="3" />
            <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
            <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
          </svg>
          <svg
            v-else
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
          {{ shareSuccess ? "Скопировано!" : "Поделиться" }}
        </button>

        <button class="btn muted" @click="compareStore.clear()">
          Очистить всё
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Загрузка характеристик...</p>
      </div>

      <div v-else>
        <!-- Category tabs (shown only when products from multiple categories) -->
        <div v-if="categoryNames.length > 1" class="compare-tabs">
          <button
            v-for="cat in categoryNames"
            :key="cat"
            class="compare-tab-btn"
            :class="{ active: activeCategory === cat }"
            @click="activeCategory = cat"
          >
            {{ cat }}
            <span class="compare-tab-count">{{
              productsByCategory[cat]?.length
            }}</span>
          </button>
        </div>

        <!-- Compare table -->
        <div class="compare-table-scroll">
          <table class="compare-table">
            <!-- Sticky product cards header -->
            <thead class="compare-thead-sticky">
              <tr class="compare-products-row">
                <th class="compare-label-col compare-sticky-label">
                  <div class="compare-category-label">
                    {{ activeCategory || "Товары" }}
                  </div>
                </th>

                <!-- Real product columns -->
                <th
                  v-for="product in activeProducts"
                  :key="product.id"
                  class="compare-product-col"
                >
                  <div class="cmp-card">
                    <button
                      class="cmp-remove-btn"
                      title="Убрать из сравнения"
                      @click="compareStore.remove(product.id)"
                    >
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2.5"
                      >
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                      </svg>
                    </button>

                    <router-link
                      :to="`/product/${product.slug}`"
                      class="cmp-card-link"
                    >
                      <div class="cmp-img-wrap">
                        <img
                          v-if="getImg(product)"
                          :src="getImg(product)!"
                          :alt="product.name"
                          class="cmp-img"
                        />
                        <div v-else class="cmp-img-placeholder">
                          <svg
                            width="32"
                            height="32"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.5"
                          >
                            <rect x="3" y="3" width="18" height="18" rx="2" />
                            <circle cx="8.5" cy="8.5" r="1.5" />
                            <polyline points="21 15 16 10 5 21" />
                          </svg>
                        </div>
                      </div>
                      <p class="cmp-name">{{ product.name }}</p>
                    </router-link>

                    <div class="cmp-meta">
                      <p class="cmp-price">
                        <span v-if="product.price">{{
                          formatPrice(product.price)
                        }}</span>
                        <span v-else class="text-muted">По запросу</span>
                      </p>
                      <span
                        class="cmp-badge"
                        :class="
                          product.is_available ? 'cmp-badge-ok' : 'cmp-badge-no'
                        "
                      >
                        {{
                          product.is_available ? "В наличии" : "Нет в наличии"
                        }}
                      </span>
                      <button
                        v-if="product.is_available"
                        class="cmp-cart-btn"
                        :class="{
                          'cmp-cart-btn--added': isJustAdded(product.id),
                        }"
                        @click="addToCart(product)"
                      >
                        <svg
                          v-if="!isJustAdded(product.id)"
                          width="14"
                          height="14"
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
                        <svg
                          v-else
                          width="14"
                          height="14"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2.5"
                        >
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                        {{
                          isJustAdded(product.id) ? "Добавлено" : "В корзину"
                        }}
                      </button>
                      <router-link
                        v-else
                        to="/contact"
                        class="cmp-cart-btn cmp-cart-btn--request"
                      >
                        Запросить цену
                      </router-link>
                    </div>
                  </div>
                </th>

                <!-- Empty slot columns -->
                <th
                  v-for="n in emptySlots"
                  :key="`empty-${n}`"
                  class="compare-product-col compare-empty-col"
                >
                  <div class="cmp-empty-slot">
                    <router-link to="/catalog" class="cmp-empty-slot-link">
                      <div class="cmp-empty-icon">
                        <svg
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                        >
                          <line x1="12" y1="5" x2="12" y2="19" />
                          <line x1="5" y1="12" x2="19" y2="12" />
                        </svg>
                      </div>
                      <span>Добавить товар</span>
                    </router-link>
                  </div>
                </th>
              </tr>
            </thead>

            <tbody>
              <!-- Fixed info rows -->
              <tr v-if="shouldShow(brandValues)" class="compare-feature-row">
                <td class="compare-label compare-sticky-label">Бренд</td>
                <td
                  v-for="product in activeProducts"
                  :key="product.id"
                  class="compare-cell"
                  :class="{ 'compare-cell-diff': !allSame(brandValues) }"
                >
                  {{ getBrand(product) }}
                </td>
                <td
                  v-for="n in emptySlots"
                  :key="`brand-empty-${n}`"
                  class="compare-cell compare-cell-empty"
                />
              </tr>

              <tr v-if="shouldShow(skuValues)" class="compare-feature-row">
                <td class="compare-label compare-sticky-label">Артикул</td>
                <td
                  v-for="product in activeProducts"
                  :key="product.id"
                  class="compare-cell"
                  :class="{ 'compare-cell-diff': !allSame(skuValues) }"
                >
                  {{ product.manufacturer_sku || "—" }}
                </td>
                <td
                  v-for="n in emptySlots"
                  :key="`sku-empty-${n}`"
                  class="compare-cell compare-cell-empty"
                />
              </tr>

              <tr
                v-if="shouldShow(internalSkuValues)"
                class="compare-feature-row"
              >
                <td class="compare-label compare-sticky-label">
                  Внутренний арт.
                </td>
                <td
                  v-for="product in activeProducts"
                  :key="product.id"
                  class="compare-cell"
                  :class="{ 'compare-cell-diff': !allSame(internalSkuValues) }"
                >
                  {{ product.internal_sku || "—" }}
                </td>
                <td
                  v-for="n in emptySlots"
                  :key="`isku-empty-${n}`"
                  class="compare-cell compare-cell-empty"
                />
              </tr>

              <!-- Feature groups -->
              <template
                v-for="grp in featureGroups"
                :key="grp.group || '__ungrouped__'"
              >
                <!-- Group header (only rendered when group name is present) -->
                <tr v-if="grp.group" class="compare-section-row">
                  <td :colspan="totalCols" class="compare-section-header">
                    {{ grp.group }}
                  </td>
                </tr>
                <!-- Single "Характеристики" header when no groups -->
                <tr
                  v-else-if="
                    featureGroups.length === 1 &&
                    !grp.group &&
                    grp.features.length > 0
                  "
                  class="compare-section-row"
                >
                  <td :colspan="totalCols" class="compare-section-header">
                    Характеристики
                  </td>
                </tr>

                <!-- Feature rows in this group -->
                <tr
                  v-for="featureName in grp.features"
                  :key="featureName"
                  class="compare-feature-row"
                >
                  <td class="compare-label compare-sticky-label">
                    {{ featureName }}
                  </td>
                  <td
                    v-for="product in activeProducts"
                    :key="product.id"
                    class="compare-cell"
                    :class="{ 'compare-cell-diff': isDifferent(featureName) }"
                  >
                    {{ getFeatureValue(product, featureName) }}
                  </td>
                  <td
                    v-for="n in emptySlots"
                    :key="`feat-empty-${n}`"
                    class="compare-cell compare-cell-empty"
                  />
                </tr>
              </template>

              <!-- No features message -->
              <tr v-if="allFeatureNames.length === 0">
                <td :colspan="totalCols" class="compare-empty-features">
                  Нет характеристик для сравнения
                </td>
              </tr>

              <!-- All same message when diff mode active -->
              <tr v-else-if="visibleFeatureNames.length === 0 && showOnlyDiff">
                <td :colspan="totalCols" class="compare-empty-features">
                  Все характеристики одинаковы
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import type { Product, Category } from "@/types";
import { useCompareStore, MAX_COMPARE_ITEMS } from "@/stores/useCompareStore";
import { useCartStore } from "@/stores/useCartStore";
import { productsAPI, getImageUrl } from "@/api";

const compareStore = useCompareStore();
const cartStore = useCartStore();

// Full product details fetched on mount (includes features, full category, full brand)
const detailedProducts = ref<Product[]>([]);
const loading = ref(false);
const showOnlyDiff = ref(false);
const activeCategory = ref<string>("");
const shareSuccess = ref(false);
const justAddedIds = ref<Set<number>>(new Set());

// ─────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────
const getImg = (product: Product): string | null => {
  const mainImage = product.main_image;
  if (!mainImage) return null;
  const imgPath = typeof mainImage === "object" ? mainImage.image : mainImage;
  return getImageUrl(imgPath);
};

const formatPrice = (price: number | null) =>
  price
    ? new Intl.NumberFormat("ru-RU", {
        style: "currency",
        currency: "UZS",
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(price)
    : "По запросу";

const getCategoryName = (product: Product): string => {
  if (product.category && typeof product.category === "object") {
    return (product.category as Category).name ?? "Прочее";
  }
  return product.category_name ?? "Прочее";
};

const getBrand = (product: Product): string => {
  if (product.brand && typeof product.brand === "object") {
    return (product.brand as any).name ?? "—";
  }
  return String(product.brand ?? "—");
};

const getFeatureValue = (product: Product, featureName: string): string => {
  const feat = product.features?.find((f) => f.feature_name === featureName);
  if (!feat) return "—";
  if (feat.value_names && feat.value_names.length > 0)
    return feat.value_names.join(", ");
  if (feat.value_name) return feat.value_name;
  return "—";
};

// ─────────────────────────────────────────────
// Cart
// ─────────────────────────────────────────────
const addToCart = (product: Product) => {
  cartStore.add(product);
  justAddedIds.value = new Set([...justAddedIds.value, product.id]);
  setTimeout(() => {
    justAddedIds.value = new Set(
      [...justAddedIds.value].filter((id) => id !== product.id),
    );
  }, 2000);
};

const isJustAdded = (id: number) => justAddedIds.value.has(id);

// ─────────────────────────────────────────────
// Share
// ─────────────────────────────────────────────
const copyShareLink = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href);
    shareSuccess.value = true;
    setTimeout(() => {
      shareSuccess.value = false;
    }, 2200);
  } catch {
    shareSuccess.value = false;
  }
};

// ─────────────────────────────────────────────
// Load full product details
// ─────────────────────────────────────────────
const loadDetails = async () => {
  if (compareStore.items.length === 0) {
    detailedProducts.value = [];
    return;
  }
  loading.value = true;
  try {
    const results = await Promise.allSettled(
      compareStore.items.map((p) => productsAPI.getBySlug(p.slug)),
    );
    detailedProducts.value = results
      .map((r, i) =>
        r.status === "fulfilled" ? r.value.data : compareStore.items[i],
      )
      .filter(Boolean) as Product[];
  } finally {
    loading.value = false;
    if (categoryNames.value.length > 0 && !activeCategory.value) {
      activeCategory.value = categoryNames.value[0];
    }
  }
};

// ─────────────────────────────────────────────
// Grouping by category
// ─────────────────────────────────────────────
const categoryNames = computed<string[]>(() => {
  const seen = new Set<string>();
  for (const p of detailedProducts.value) seen.add(getCategoryName(p));
  return Array.from(seen);
});

const productsByCategory = computed<Record<string, Product[]>>(() => {
  const map: Record<string, Product[]> = {};
  for (const p of detailedProducts.value) {
    const cat = getCategoryName(p);
    if (!map[cat]) map[cat] = [];
    map[cat].push(p);
  }
  return map;
});

const activeProducts = computed<Product[]>(() => {
  if (!activeCategory.value) return detailedProducts.value;
  return (
    productsByCategory.value[activeCategory.value] ?? detailedProducts.value
  );
});

// ─────────────────────────────────────────────
// Empty slots (up to MAX_COMPARE_ITEMS total)
// ─────────────────────────────────────────────
// Empty slots = remaining global capacity (not per-category)
const emptySlots = computed(() =>
  Math.max(0, MAX_COMPARE_ITEMS - compareStore.items.length),
);

// Total columns = label + products + empty slots
const totalCols = computed(
  () => 1 + activeProducts.value.length + emptySlots.value,
);

// ─────────────────────────────────────────────
// Feature logic
// ─────────────────────────────────────────────
const allFeatureNames = computed<string[]>(() => {
  const names = new Set<string>();
  for (const p of activeProducts.value) {
    for (const feat of p.features ?? []) names.add(feat.feature_name);
  }
  return Array.from(names);
});

const isDifferent = (featureName: string): boolean => {
  const vals = activeProducts.value.map((p) => getFeatureValue(p, featureName));
  return new Set(vals).size > 1;
};

const visibleFeatureNames = computed<string[]>(() => {
  if (!showOnlyDiff.value) return allFeatureNames.value;
  return allFeatureNames.value.filter((name) => isDifferent(name));
});

// ─────────────────────────────────────────────
// Feature groups (supports optional group_name from backend)
// ─────────────────────────────────────────────
const featureGroups = computed<{ group: string; features: string[] }[]>(() => {
  if (visibleFeatureNames.value.length === 0) return [];

  // Check if any feature has group_name info
  const hasGroups = activeProducts.value.some((p) =>
    p.features?.some((f) => f.group_name),
  );

  if (!hasGroups) {
    return [{ group: "", features: visibleFeatureNames.value }];
  }

  // Build ordered group -> feature names map
  const groupMap = new Map<string, string[]>();
  for (const p of activeProducts.value) {
    for (const feat of p.features ?? []) {
      if (!visibleFeatureNames.value.includes(feat.feature_name)) continue;
      const grp = feat.group_name || "Прочее";
      if (!groupMap.has(grp)) groupMap.set(grp, []);
      const grpArr = groupMap.get(grp)!;
      if (!grpArr.includes(feat.feature_name)) grpArr.push(feat.feature_name);
    }
  }

  return Array.from(groupMap.entries()).map(([group, features]) => ({
    group,
    features,
  }));
});

// ─────────────────────────────────────────────
// "Show differences" for fixed rows
// ─────────────────────────────────────────────
const brandValues = computed(() => activeProducts.value.map(getBrand));
const skuValues = computed(() =>
  activeProducts.value.map((p) => String(p.manufacturer_sku ?? "—")),
);
const internalSkuValues = computed(() =>
  activeProducts.value.map((p) => String(p.internal_sku ?? "—")),
);

const allSame = (values: string[] | readonly string[]): boolean =>
  new Set(values).size <= 1;

const shouldShow = (values: string[] | readonly string[]): boolean => {
  if (!showOnlyDiff.value) return true;
  return !allSame(values);
};

// ─────────────────────────────────────────────
// Watchers
// ─────────────────────────────────────────────
watch(categoryNames, (names) => {
  if (names.length > 0 && !names.includes(activeCategory.value)) {
    activeCategory.value = names[0];
  }
});

watch(
  () => compareStore.items.length,
  () => loadDetails(),
);

onMounted(() => loadDetails());
</script>

<!-- Styles in main.css -->
