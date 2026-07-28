<template>
  <header class="header" :class="{ 'header--scrolled': scrolled }" ref="headerRef">
    <div class="container">
      <nav class="navbar">
        <router-link to="/" class="logo" @click="closeMobileMenu">
          <span></span>
        </router-link>

        <!-- Search Bar (desktop) -->
        <div class="search-container">
          <form @submit.prevent="navigateToSearchResults" class="search-wrapper">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="Поиск по названию или артикулу..."
              class="search-input"
            />
            <button
              type="submit"
              class="search-btn"
              :disabled="searchQuery.trim().length < 1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
            </button>
          </form>
        </div>

        <!-- Icons -->
        <div class="header-icons">
          <router-link to="/favorites" class="header-icon-btn" title="Избранное" @click="closeMobileMenu">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
            </svg>
            <span v-if="favCount > 0" class="header-icon-badge">{{ favCount }}</span>
          </router-link>
          <router-link to="/compare" class="header-icon-btn" title="Сравнение" @click="closeMobileMenu">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="20" x2="18" y2="10"/>
              <line x1="12" y1="20" x2="12" y2="4"/>
              <line x1="6" y1="20" x2="6" y2="14"/>
            </svg>
            <span v-if="compareCount > 0" class="header-icon-badge">{{ compareCount }}</span>
          </router-link>
          <router-link to="/cart" class="header-icon-btn" title="Корзина" @click="closeMobileMenu">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="9" cy="21" r="1"/>
              <circle cx="20" cy="21" r="1"/>
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
            </svg>
            <span v-if="cartCount > 0" class="header-icon-badge">{{ cartCount }}</span>
          </router-link>
        </div>

        <!-- Burger button -->
        <button
          class="mobile-menu-toggle"
          @click="mobileMenuOpen = !mobileMenuOpen"
          :aria-expanded="mobileMenuOpen"
          :aria-label="mobileMenuOpen ? 'Закрыть меню' : 'Открыть меню'"
          :class="{ open: mobileMenuOpen }"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <!-- Desktop nav links -->
        <ul class="nav-menu" :class="{ active: mobileMenuOpen }">
          <!-- Mobile search -->
          <li class="mobile-search-item">
            <form @submit.prevent="navigateToSearchResults" class="mobile-search-wrapper">
              <input
                type="text"
                v-model="searchQuery"
                placeholder="Поиск по названию или артикулу..."
                class="mobile-search-input"
              />
              <button type="submit" class="mobile-search-btn" :disabled="searchQuery.trim().length < 1">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="11" cy="11" r="8"></circle>
                  <path d="m21 21-4.35-4.35"></path>
                </svg>
              </button>
            </form>
          </li>

          <li><router-link to="/" @click="closeMobileMenu">Главная</router-link></li>

          <!-- КАТАЛОГ — desktop hover trigger -->
          <li
            class="catalog-menu"
            @mouseenter="onCatalogEnter"
            @mouseleave="onCatalogLeave"
          >
            <button class="catalog-nav-btn" @click="handleCatalogBtnClick">
              Каталог
              <svg class="catalog-chevron" :class="{ rotated: megaOpen || accordionOpen }" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </button>

            <!-- Mobile accordion -->
            <ul v-if="isMobile && accordionOpen" class="mobile-accordion">
              <li>
                <router-link to="/catalog" @click="closeMobileMenu" class="accordion-all-link">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
                  Все категории
                </router-link>
              </li>
              <li v-for="cat in categories" :key="cat.id">
                <router-link :to="`/catalog/${cat.slug}`" @click="closeMobileMenu" class="accordion-cat-link">
                  {{ cat.name }}
                </router-link>
              </li>
            </ul>
          </li>

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
          <!-- Left: category list -->
          <ul class="mega-cats">
            <li
              v-for="cat in categories"
              :key="cat.id"
              class="mega-cat-item"
              :class="{ active: hoveredCat?.id === cat.id }"
              @mouseenter="hoveredCat = cat"
            >
              <router-link :to="`/catalog/${cat.slug}`" @click="megaOpen = false">
                <span class="mega-cat-dot"></span>
                {{ cat.name }}
                <svg class="mega-cat-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
              </router-link>
            </li>
          </ul>

          <!-- Right: featured panel -->
          <div class="mega-panel">
            <div v-if="hoveredCat" class="mega-panel-content">
              <div class="mega-panel-header">
                <h3>{{ hoveredCat.name }}</h3>
                <router-link :to="`/catalog/${hoveredCat.slug}`" class="mega-see-all" @click="megaOpen = false">
                  Смотреть все →
                </router-link>
              </div>
              <div class="mega-panel-body">
                <router-link
                  :to="`/catalog/${hoveredCat.slug}`"
                  class="mega-feature-card"
                  @click="megaOpen = false"
                >
                  <div class="mega-feature-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
                  </div>
                  <div>
                    <div class="mega-feature-title">Все товары</div>
                    <div class="mega-feature-sub">в категории «{{ hoveredCat.name }}»</div>
                  </div>
                </router-link>
              </div>
            </div>
            <div v-else class="mega-panel-placeholder">
              <div class="mega-placeholder-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
              </div>
              <p>Выберите категорию</p>
            </div>

            <!-- Bottom CTA -->
            <div class="mega-panel-footer">
              <router-link to="/catalog" class="mega-all-btn" @click="megaOpen = false">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
                Весь каталог
              </router-link>
            </div>
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
  if (closeTimer) { clearTimeout(closeTimer); closeTimer = null; }
  openTimer = setTimeout(() => { megaOpen.value = true; }, 80);
};
const onCatalogLeave = () => {
  if (isMobile.value) return;
  if (openTimer) { clearTimeout(openTimer); openTimer = null; }
  closeTimer = setTimeout(() => { megaOpen.value = false; hoveredCat.value = null; }, 150);
};
const onMegaEnter = () => {
  if (closeTimer) { clearTimeout(closeTimer); closeTimer = null; }
};
const onMegaLeave = () => {
  closeTimer = setTimeout(() => { megaOpen.value = false; hoveredCat.value = null; }, 150);
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
    router.push({ path: "/catalog", query: { search: q } });
    searchQuery.value = "";
    closeMobileMenu();
  }
};

// Escape key
const onKeydown = (e: KeyboardEvent) => {
  if (e.key === "Escape") { megaOpen.value = false; closeMobileMenu(); }
};

watch(() => route.path, () => { closeMobileMenu(); searchQuery.value = ""; });

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

<style scoped>
/* ---- Catalog nav button (replaces plain link) ---- */
.catalog-nav-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  background: none;
  border: none;
  padding: var(--space-2) 0;
  color: rgba(255,255,255,0.8);
  font-weight: 500;
  font-size: var(--text-sm);
  letter-spacing: var(--tracking-wide);
  text-transform: uppercase;
  cursor: pointer;
  transition: color var(--transition-base);
  position: relative;
}
.catalog-nav-btn::before {
  content: "";
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--accent-gradient);
  border-radius: var(--radius-full);
  transition: width var(--transition-base);
}
.catalog-menu:hover .catalog-nav-btn,
.catalog-nav-btn:hover {
  color: var(--white);
}
.catalog-menu:hover .catalog-nav-btn::before {
  width: 100%;
}
.catalog-chevron {
  transition: transform 0.2s ease;
  opacity: 0.7;
}
.catalog-chevron.rotated {
  transform: rotate(180deg);
}

/* ---- MEGA MENU ---- */
.mega-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border-top: 2px solid var(--accent);
  box-shadow: 0 20px 60px rgba(0,0,0,0.18);
  z-index: 999;
}
.mega-inner {
  display: flex;
  min-height: 320px;
  max-height: 480px;
}

/* Left column: category list */
.mega-cats {
  width: 260px;
  flex-shrink: 0;
  border-right: 1px solid #f0f0f0;
  padding: 12px 0;
  overflow-y: auto;
}
.mega-cat-item a {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 20px;
  color: #333 !important;
  font-size: 14px;
  font-weight: 500;
  text-transform: none !important;
  letter-spacing: normal !important;
  transition: background 0.15s, color 0.15s, padding-left 0.15s;
  border-radius: 0;
}
.mega-cat-item a::before { display: none !important; }
.mega-cat-item.active a,
.mega-cat-item a:hover {
  background: #f8f4ef;
  color: var(--primary) !important;
  padding-left: 26px;
}
.mega-cat-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.15s;
}
.mega-cat-item.active .mega-cat-dot,
.mega-cat-item a:hover .mega-cat-dot {
  opacity: 1;
}
.mega-cat-arrow {
  margin-left: auto;
  opacity: 0;
  transition: opacity 0.15s;
}
.mega-cat-item.active .mega-cat-arrow,
.mega-cat-item a:hover .mega-cat-arrow {
  opacity: 0.5;
}

/* Right panel */
.mega-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px 28px;
}
.mega-panel-content {
  flex: 1;
}
.mega-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}
.mega-panel-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}
.mega-see-all {
  font-size: 13px;
  color: var(--accent) !important;
  font-weight: 500;
  text-transform: none !important;
  letter-spacing: normal !important;
  transition: opacity 0.15s;
}
.mega-see-all:hover { opacity: 0.7; }
.mega-see-all::before { display: none !important; }
.mega-panel-body {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}
.mega-feature-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border: 1.5px solid #f0f0f0;
  border-radius: 12px;
  text-decoration: none;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
  color: #333 !important;
  text-transform: none !important;
  letter-spacing: normal !important;
}
.mega-feature-card::before { display: none !important; }
.mega-feature-card:hover {
  border-color: var(--accent);
  box-shadow: 0 4px 16px rgba(212,165,116,0.15);
  transform: translateY(-2px);
}
.mega-feature-icon {
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, #f8f4ef 0%, #f0e8dc 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--accent);
}
.mega-feature-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1.3;
}
.mega-feature-sub {
  font-size: 12px;
  color: #888;
  margin-top: 2px;
  line-height: 1.4;
}
.mega-panel-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #bbb;
  gap: 12px;
  font-size: 14px;
}
.mega-placeholder-icon { opacity: 0.3; }
.mega-panel-footer {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}
.mega-all-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--accent-gradient);
  color: #fff !important;
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  text-decoration: none;
  text-transform: none !important;
  letter-spacing: normal !important;
  transition: opacity 0.15s, transform 0.15s;
}
.mega-all-btn::before { display: none !important; }
.mega-all-btn:hover { opacity: 0.9; transform: translateY(-1px); }

/* Overlay */
.mega-overlay {
  position: fixed;
  inset: 0;
  top: var(--header-height, 72px);
  background: rgba(0,0,0,0.35);
  z-index: 998;
  backdrop-filter: blur(2px);
}

/* Transitions */
.mega-enter-active,
.mega-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.mega-enter-from,
.mega-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
.overlay-enter-active,
.overlay-leave-active {
  transition: opacity 0.2s ease;
}
.overlay-enter-from,
.overlay-leave-to {
  opacity: 0;
}

/* ---- MOBILE ACCORDION ---- */
.mobile-accordion {
  list-style: none;
  padding: 0;
  margin: 4px 0 8px 0;
  background: rgba(255,255,255,0.05);
  border-radius: 8px;
  overflow: hidden;
  animation: accordionSlide 0.25s ease;
}
@keyframes accordionSlide {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.accordion-all-link,
.accordion-cat-link {
  display: flex !important;
  align-items: center;
  gap: 10px;
  padding: 12px 16px !important;
  color: rgba(255,255,255,0.75) !important;
  font-size: 14px !important;
  font-weight: 400 !important;
  text-transform: none !important;
  letter-spacing: normal !important;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  transition: background 0.15s, color 0.15s, padding-left 0.15s !important;
}
.accordion-all-link::before,
.accordion-cat-link::before { display: none !important; }
.accordion-all-link:hover,
.accordion-cat-link:hover,
.accordion-all-link.router-link-active,
.accordion-cat-link.router-link-active {
  background: rgba(212,165,116,0.12) !important;
  color: var(--accent) !important;
  padding-left: 22px !important;
}
.accordion-all-link {
  font-weight: 600 !important;
  color: rgba(255,255,255,0.9) !important;
}
</style>
