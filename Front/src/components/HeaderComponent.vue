<template>
  <header ref="headerRef" class="header" :class="{ 'header--scrolled': scrolled }">
    <div class="container">
      <nav class="navbar">
        <router-link to="/" class="logo" @click="closeMobileMenu">
          <img src="/logo.png" alt="" width="70" height="32" class="logo-mark" />
          <span class="logo-name">Future Stars</span>
        </router-link>

        <!-- Search Bar (desktop) -->
        <div class="search-container">
          <form class="search-wrapper" @submit.prevent="navigateToSearchResults">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Поиск по названию или артикулу..."
              class="search-input"
            />
            <button type="submit" class="search-btn" :disabled="searchQuery.trim().length < 1">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
            </button>
          </form>
        </div>

        <router-link to="/promo" class="header-promo-link" @click="closeMobileMenu"
          >Акции</router-link
        >

        <!-- Icons -->
        <div class="header-icons">
          <router-link
            to="/favorites"
            class="header-icon-btn"
            title="Избранное"
            @click="closeMobileMenu"
          >
            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
              />
            </svg>
            <span v-if="favCount > 0" class="header-icon-badge">{{ favCount }}</span>
          </router-link>
          <router-link
            to="/compare"
            class="header-icon-btn"
            title="Сравнение"
            @click="closeMobileMenu"
          >
            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <line x1="18" y1="20" x2="18" y2="10" />
              <line x1="12" y1="20" x2="12" y2="4" />
              <line x1="6" y1="20" x2="6" y2="14" />
            </svg>
            <span v-if="compareCount > 0" class="header-icon-badge">{{ compareCount }}</span>
          </router-link>
          <router-link to="/cart" class="header-icon-btn" title="Корзина" @click="closeMobileMenu">
            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <circle cx="9" cy="21" r="1" />
              <circle cx="20" cy="21" r="1" />
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
            </svg>
            <span v-if="cartCount > 0" class="header-icon-badge">{{ cartCount }}</span>
          </router-link>
        </div>

        <!-- Burger button -->
        <button
          class="mobile-menu-toggle"
          :aria-expanded="mobileMenuOpen"
          :aria-label="mobileMenuOpen ? 'Закрыть меню' : 'Открыть меню'"
          :class="{ open: mobileMenuOpen }"
          @click="mobileMenuOpen = !mobileMenuOpen"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <!-- Desktop nav links -->
        <ul class="nav-menu" :class="{ active: mobileMenuOpen }">
          <!-- Mobile search -->
          <li class="mobile-search-item">
            <form class="mobile-search-wrapper" @submit.prevent="navigateToSearchResults">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Поиск по названию или артикулу..."
                class="mobile-search-input"
              />
              <button
                type="submit"
                class="mobile-search-btn"
                :disabled="searchQuery.trim().length < 1"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="11" cy="11" r="8"></circle>
                  <path d="m21 21-4.35-4.35"></path>
                </svg>
              </button>
            </form>
          </li>

          <li><router-link to="/" @click="closeMobileMenu">Главная</router-link></li>

          <!-- КАТАЛОГ — desktop hover trigger -->
          <li class="catalog-menu" @mouseenter="onCatalogEnter" @mouseleave="onCatalogLeave">
            <button class="catalog-nav-btn" @click="handleCatalogBtnClick">
              Каталог
              <svg
                class="catalog-chevron"
                :class="{ rotated: megaOpen || accordionOpen }"
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>

            <!-- Mobile accordion -->
            <ul v-if="isMobile && accordionOpen" class="mobile-accordion">
              <li>
                <router-link to="/catalog" class="accordion-all-link" @click="closeMobileMenu">
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
                    <rect x="3" y="14" width="7" height="7" />
                    <rect x="14" y="14" width="7" height="7" />
                  </svg>
                  Все категории
                </router-link>
              </li>
              <li v-for="cat in categories" :key="cat.id">
                <router-link
                  :to="`/catalog/${cat.slug}`"
                  class="accordion-cat-link"
                  @click="closeMobileMenu"
                >
                  {{ cat.name }}
                </router-link>
              </li>
            </ul>
          </li>

          <li><router-link to="/promo" @click="closeMobileMenu">Акции</router-link></li>
          <li><router-link to="/about" @click="closeMobileMenu">О нас</router-link></li>
          <li><router-link to="/contact" @click="closeMobileMenu">Контакты</router-link></li>
        </ul>
      </nav>
    </div>

    <!-- MEGA MENU PANEL (desktop only) -->
    <Transition name="mega">
      <div
        v-if="!isMobile && megaOpen"
        class="mega-menu"
        @mouseenter="onMegaEnter"
        @mouseleave="onMegaLeave"
      >
        <div class="mega-inner container">
          <!-- Left: category list + footer -->
          <div class="mega-left">
            <ul class="mega-cats">
              <li
                v-for="cat in categories"
                :key="cat.id"
                class="mega-cat-item"
                :class="{ active: hoveredCat?.id === cat.id }"
                @mouseenter="hoveredCat = cat"
              >
                <router-link :to="`/catalog/${cat.slug}`" @click="megaOpen = false">
                  <div class="mega-cat-thumb">
                    <img v-if="cat.image" :src="cat.image" :alt="cat.name" />
                    <svg
                      v-else
                      width="18"
                      height="18"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                    >
                      <rect x="3" y="3" width="7" height="7" />
                      <rect x="14" y="3" width="7" height="7" />
                      <rect x="3" y="14" width="7" height="7" />
                      <rect x="14" y="14" width="7" height="7" />
                    </svg>
                  </div>
                  <span class="mega-cat-name">{{ cat.name }}</span>
                  <span class="mega-cat-count">{{ cat.products_count }}</span>
                  <svg
                    class="mega-cat-arrow"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path d="M9 18l6-6-6-6" />
                  </svg>
                </router-link>
              </li>
            </ul>

            <div class="mega-left-footer">
              <router-link to="/catalog" class="mega-all-link" @click="megaOpen = false">
                <svg
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <rect x="3" y="3" width="7" height="7" />
                  <rect x="14" y="3" width="7" height="7" />
                  <rect x="3" y="14" width="7" height="7" />
                  <rect x="14" y="14" width="7" height="7" />
                </svg>
                Весь каталог
              </router-link>
            </div>
          </div>

          <!-- Right: visual scene panel -->
          <div class="mega-panel">
            <Transition name="scene" mode="out-in">
              <router-link
                v-if="hoveredCat"
                :key="hoveredCat.id"
                :to="`/catalog/${hoveredCat.slug}`"
                class="mega-scene"
                @click="megaOpen = false"
              >
                <!-- Background image -->
                <div
                  class="mega-scene-bg"
                  :style="hoveredCat.image ? `background-image:url(${hoveredCat.image})` : ''"
                ></div>
                <!-- Gradient overlay -->
                <div class="mega-scene-overlay"></div>
                <!-- Content -->
                <div class="mega-scene-content">
                  <span class="mega-scene-badge">
                    {{ hoveredCat.products_count }}
                    {{
                      hoveredCat.products_count === 1
                        ? "товар"
                        : hoveredCat.products_count < 5
                          ? "товара"
                          : "товаров"
                    }}
                  </span>
                  <h3 class="mega-scene-title">{{ hoveredCat.name }}</h3>
                  <span class="mega-scene-cta">
                    Смотреть все
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2.5"
                    >
                      <path d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                  </span>
                </div>
              </router-link>
            </Transition>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Overlay -->
    <Transition name="overlay">
      <div v-if="megaOpen && !isMobile" class="mega-overlay" @click="megaOpen = false"></div>
    </Transition>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { categoriesAPI } from "@/api";
import type { Category } from "@/types";
import { useFavoritesStore } from "@/stores/useFavoritesStore";
import { useCompareStore } from "@/stores/useCompareStore";
import { useCartStore } from "@/stores/useCartStore";

const route = useRoute();
const router = useRouter();
const headerRef = ref<HTMLElement | null>(null);

const mobileMenuOpen = ref(false);
const megaOpen = ref(false);
const accordionOpen = ref(false);
const hoveredCat = ref<Category | null>(null);
const categories = ref<Category[]>([]);
const searchQuery = ref("");

const favStore = useFavoritesStore();
const compareStore = useCompareStore();
const cartStore = useCartStore();
const favCount = computed(() => favStore.items.length);
const compareCount = computed(() => compareStore.items.length);
const cartCount = computed(() => cartStore.totalQty);

// Reactive isMobile
const isMobile = ref(window.matchMedia("(max-width: 768px)").matches);
let mq: MediaQueryList;
const onMqChange = (e: MediaQueryListEvent) => {
  isMobile.value = e.matches;
  if (!e.matches) {
    mobileMenuOpen.value = false;
    accordionOpen.value = false;
  }
};

// ---- Scrolled (compact) state ----
const scrolled = ref(false);
const SCROLL_THRESHOLD = 60;
const onScroll = () => {
  const isScrolled = window.scrollY > SCROLL_THRESHOLD;
  scrolled.value = isScrolled;
  document.body.classList.toggle("header-is-fixed", isScrolled);
};

// Hover delays for smooth feel
let openTimer: ReturnType<typeof setTimeout> | null = null;
let closeTimer: ReturnType<typeof setTimeout> | null = null;

const onCatalogEnter = () => {
  if (isMobile.value) return;
  if (closeTimer) {
    clearTimeout(closeTimer);
    closeTimer = null;
  }
  openTimer = setTimeout(() => {
    megaOpen.value = true;
  }, 80);
};
const onCatalogLeave = () => {
  if (isMobile.value) return;
  if (openTimer) {
    clearTimeout(openTimer);
    openTimer = null;
  }
  closeTimer = setTimeout(() => {
    megaOpen.value = false;
    hoveredCat.value = null;
  }, 150);
};
const onMegaEnter = () => {
  if (closeTimer) {
    clearTimeout(closeTimer);
    closeTimer = null;
  }
};
const onMegaLeave = () => {
  closeTimer = setTimeout(() => {
    megaOpen.value = false;
    hoveredCat.value = null;
  }, 150);
};

// Mobile: clicking "Каталог" button
const handleCatalogBtnClick = () => {
  if (isMobile.value) {
    accordionOpen.value = !accordionOpen.value;
  } else {
    router.push("/catalog");
    megaOpen.value = false;
  }
};

const closeMobileMenu = () => {
  mobileMenuOpen.value = false;
  megaOpen.value = false;
  accordionOpen.value = false;
};

const navigateToSearchResults = () => {
  const q = searchQuery.value.trim();
  if (q.length >= 2) {
    router.push({ path: "/catalog", query: { q } });
    searchQuery.value = "";
    closeMobileMenu();
  }
};

// Escape key
const onKeydown = (e: KeyboardEvent) => {
  if (e.key === "Escape") {
    megaOpen.value = false;
    closeMobileMenu();
  }
};

watch(
  () => route.path,
  () => {
    closeMobileMenu();
    searchQuery.value = "";
  },
);

// Auto-select first category the moment the mega menu opens
watch(megaOpen, (open) => {
  if (open && categories.value.length && !hoveredCat.value) {
    hoveredCat.value = categories.value[0];
  }
  if (!open) hoveredCat.value = null;
});

watch(mobileMenuOpen, (open) => {
  document.body.style.overflow = open ? "hidden" : "";
  if (!open) accordionOpen.value = false;
});

onMounted(async () => {
  mq = window.matchMedia("(max-width: 768px)");
  mq.addEventListener("change", onMqChange);
  document.addEventListener("keydown", onKeydown);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll(); // sync on mount in case page loads mid-scroll
  try {
    const res = await categoriesAPI.getAll(100);
    categories.value = res.data.results;
  } catch (e) {
    console.error("Ошибка загрузки каталога:", e);
  }
});

onUnmounted(() => {
  mq?.removeEventListener("change", onMqChange);
  document.removeEventListener("keydown", onKeydown);
  window.removeEventListener("scroll", onScroll);
  if (openTimer) clearTimeout(openTimer);
  if (closeTimer) clearTimeout(closeTimer);
});
</script>

<style scoped src="@/styles/components/HeaderComponent.css"></style>
