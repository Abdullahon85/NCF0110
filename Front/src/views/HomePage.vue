<template>
  <div class="hp">
    <!-- First screen: what we sell + the "build your system" game -->
    <section class="hp-hero">
      <div class="hp-wrap">
        <div class="hp-hero-text">
          <div class="hp-hero-copy">
            <h1 class="hp-title">Оборудование для видеонаблюдения и безопасности</h1>
            <p class="hp-lead">
              Системы видеонаблюдения, IP-камеры и оборудование безопасности от ведущих мировых
              брендов. Соберите систему для своего объекта на схеме и отправьте список — поможем с
              подбором.
            </p>
          </div>
          <div class="hp-hero-actions">
            <router-link to="/catalog" class="btn btn-primary">Смотреть каталог</router-link>
            <router-link to="/about" class="btn btn-outline">О компании</router-link>
          </div>
        </div>
        <BuildSystem />
      </div>
    </section>

    <!-- Banners are managed in the admin (section «Баннеры») -->
    <section v-if="bannersLoading || banners.length" class="hp-banners">
      <div class="hp-wrap">
        <BannerSlider :banners="banners" :loading="bannersLoading" :autoplay-interval="5000" />
      </div>
    </section>

    <section class="hp-section" aria-labelledby="hp-cat-title">
      <div class="hp-wrap">
        <div class="hp-head">
          <h2 id="hp-cat-title" class="hp-h2">Каталог товаров</h2>
          <router-link to="/catalog" class="hp-more">Весь каталог</router-link>
        </div>
        <p class="hp-desc">Широкий ассортимент оборудования для любых задач безопасности</p>

        <div v-if="loading" class="hp-cat-grid">
          <div v-for="n in 6" :key="n" class="hp-cat-skeleton skeleton"></div>
        </div>
        <ul v-else-if="categories.length" class="hp-cat-grid">
          <li v-for="cat in categories" :key="cat.id">
            <router-link :to="`/catalog/${cat.slug}`" class="hp-cat">
              <span class="hp-cat-img">
                <img v-if="cat.image" :src="getImageUrl(cat.image)" :alt="''" loading="lazy" />
                <svg
                  v-else
                  width="40"
                  height="40"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <rect x="3" y="3" width="18" height="18" rx="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
              </span>
              <span class="hp-cat-name">{{ cat.name }}</span>
            </router-link>
          </li>
        </ul>
      </div>
    </section>

    <!-- Product tabs like shop.nag.uz; a tab without products is not shown -->
    <section v-if="shownTabs.length" class="hp-section" aria-labelledby="hp-tabs-title">
      <div class="hp-wrap">
        <h2 id="hp-tabs-title" class="sr-only">Товары</h2>
        <div class="hp-tabs" role="tablist">
          <button
            v-for="tab in shownTabs"
            :key="tab.key"
            type="button"
            role="tab"
            class="hp-tab"
            :aria-selected="activeTab === tab.key"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
          <router-link v-if="currentTab?.more" :to="currentTab.more" class="hp-more"
            >Все акции</router-link
          >
        </div>
        <ProductGrid v-if="currentTab" :products="currentTab.products" />
      </div>
    </section>

    <section class="hp-section hp-section--surface" aria-labelledby="hp-feat-title">
      <div class="hp-wrap">
        <h2 id="hp-feat-title" class="hp-h2">Почему выбирают нас</h2>
        <ul class="hp-feat-grid">
          <li v-for="feat in features" :key="feat.title" class="hp-feat">
            <span class="hp-feat-icon" aria-hidden="true" v-html="feat.icon"></span>
            <h3 class="hp-feat-title">{{ feat.title }}</h3>
            <p class="hp-feat-desc">{{ feat.desc }}</p>
          </li>
        </ul>
      </div>
    </section>

    <section v-if="brands.length" class="hp-section" aria-labelledby="hp-brand-title">
      <div class="hp-wrap">
        <div class="hp-head">
          <h2 id="hp-brand-title" class="hp-h2">Наши бренды</h2>
          <router-link to="/brands" class="hp-more">Все бренды</router-link>
        </div>
        <p class="hp-desc">Работаем только с проверенными мировыми производителями</p>
        <ul class="hp-brand-grid">
          <li v-for="brand in brands.slice(0, 12)" :key="brand.id">
            <router-link :to="`/brands/${brand.slug}`" class="hp-brand" :aria-label="brand.name">
              <img
                v-if="brand.image"
                :src="getImageUrl(brand.image)"
                :alt="brand.name"
                loading="lazy"
              />
              <span v-else>{{ brand.name }}</span>
            </router-link>
          </li>
        </ul>
      </div>
    </section>

    <section class="hp-cta" aria-labelledby="hp-cta-title">
      <div class="hp-wrap hp-cta-inner">
        <div>
          <h2 id="hp-cta-title" class="hp-cta-title">Оставьте заявку — свяжемся сегодня</h2>
          <p class="hp-cta-sub">
            Бесплатная консультация по подбору оборудования для вашего объекта
          </p>
        </div>
        <router-link to="/contact" class="btn hp-cta-btn">Получить консультацию</router-link>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import { categoriesAPI, brandsAPI, bannersAPI, getImageUrl, productsAPI } from "@/api";
import ProductGrid from "@/components/ProductGrid.vue";
import type { Product } from "@/types";
import BannerSlider from "@/components/BannerSlider.vue";
import BuildSystem from "@/components/builder/BuildSystem.vue";
import type { Category, Brand, Banner } from "@/types";

const categories = ref<Category[]>([]);
const brands = ref<Brand[]>([]);
const banners = ref<Banner[]>([]);
const loading = ref(true);
const bannersLoading = ref(true);

const features = [
  {
    icon: `<svg width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
    title: "Гарантия качества",
    desc: "Все товары проходят строгий контроль качества перед поступлением на склад. Официальные гарантийные обязательства производителей.",
  },
  {
    icon: `<svg width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
    title: "Быстрая доставка",
    desc: "Доставка по всей стране в кратчайшие сроки.",
  },
  {
    icon: `<svg width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
    title: "Экспертная поддержка",
    desc: "Команда специалистов готова помочь с выбором и установкой.",
  },
  {
    icon: `<svg width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>`,
    title: "Лучшие цены",
    desc: "Прямые поставки от производителей обеспечивают конкурентные цены.",
  },
];

// Short-lived session cache so going back to the home page does not refetch.
const cache = {
  get<T>(k: string): T | null {
    try {
      const s = sessionStorage.getItem(k);
      if (!s) return null;
      const { data, expiry } = JSON.parse(s);
      if (Date.now() > expiry) {
        sessionStorage.removeItem(k);
        return null;
      }
      return data as T;
    } catch {
      return null;
    }
  },
  set(k: string, data: unknown, ttl: number) {
    try {
      sessionStorage.setItem(k, JSON.stringify({ data, expiry: Date.now() + ttl }));
    } catch {
      /* storage full or blocked — no cache */
    }
  },
};

// Home product tabs: 8 products each, loaded together; empty tabs are hidden.
type HomeTab = {
  key: string;
  label: string;
  params: Record<string, string>;
  more: string;
  products: Product[];
};
const tabs = ref<HomeTab[]>([
  {
    key: "recommended",
    label: "Рекомендуем",
    params: { recommended: "1" },
    more: "",
    products: [],
  },
  { key: "new", label: "Новинки", params: { sort: "new" }, more: "", products: [] },
  { key: "promo", label: "Акции", params: { promo: "1" }, more: "/promo", products: [] },
  {
    key: "popular",
    label: "Популярное",
    params: { sort: "popular", ordered: "1" },
    more: "",
    products: [],
  },
]);
const activeTab = ref("");
const shownTabs = computed(() => tabs.value.filter((t) => t.products.length));
const currentTab = computed(
  () => shownTabs.value.find((t) => t.key === activeTab.value) ?? shownTabs.value[0],
);

async function loadTabs() {
  await Promise.all(
    tabs.value.map(async (tab) => {
      try {
        const { data } = await productsAPI.list({ ...tab.params, page_size: "20" });
        tab.products = data.results.slice(0, 8);
      } catch {
        tab.products = [];
      }
    }),
  );
}

onMounted(async () => {
  loadTabs();
  bannersAPI
    .getAll()
    .then((r) => (banners.value = r.data))
    .catch(() => {})
    .finally(() => (bannersLoading.value = false));

  const cc = cache.get<Category[]>("home_categories");
  const bc = cache.get<Brand[]>("home_brands");
  if (cc && bc) {
    categories.value = cc;
    brands.value = bc;
    loading.value = false;
    return;
  }
  try {
    const [cr, br] = await Promise.all([categoriesAPI.getAll(), brandsAPI.getAll()]);
    categories.value = cr.data.results ?? cr.data;
    brands.value = br.data.results ?? br.data;
    cache.set("home_categories", categories.value, 120000);
    cache.set("home_brands", brands.value, 120000);
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped src="@/styles/views/HomePage.css"></style>
