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
                    <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
                  </div>
                  <span class="mega-cat-name">{{ cat.name }}</span>
                  <span class="mega-cat-count">{{ cat.products_count }}</span>
                  <svg class="mega-cat-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
                </router-link>
              </li>
            </ul>

            <div class="mega-left-footer">
              <router-link to="/catalog" class="mega-all-link" @click="megaOpen = false">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
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
                    {{ hoveredCat.products_count === 1 ? 'товар' : hoveredCat.products_count < 5 ? 'товара' : 'товаров' }}
                  </span>
                  <h3 class="mega-scene-title">{{ hoveredCat.name }}</h3>
                  <span class="mega-scene-cta">
                    Смотреть все
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
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
  background: #0e1813;
  border-top: 1px solid rgba(212,165,116,0.2);
  box-shadow: 0 24px 64px rgba(0,0,0,0.55), 0 4px 12px rgba(0,0,0,0.3);
  z-index: 999;
}
.mega-inner {
  display: flex;
  height: 340px;
}

/* ---- Left column ---- */
.mega-left {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255,255,255,0.06);
  background: rgba(0,0,0,0.2);
}
.mega-cats {
  flex: 1;
  list-style: none;
  padding: 10px 0;
  margin: 0;
  overflow-y: auto;
}
.mega-cats::-webkit-scrollbar { width: 3px; }
.mega-cats::-webkit-scrollbar-track { background: transparent; }
.mega-cats::-webkit-scrollbar-thumb { background: rgba(212,165,116,0.25); border-radius: 3px; }

.mega-cat-item a {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 10px 16px;
  color: rgba(255,255,255,0.65) !important;
  font-size: 13.5px;
  font-weight: 500;
  text-transform: none !important;
  letter-spacing: normal !important;
  text-decoration: none;
  transition: background 0.18s, color 0.18s;
  position: relative;
}
.mega-cat-item a::before { display: none !important; }

.mega-cat-item.active a,
.mega-cat-item a:hover {
  background: rgba(212,165,116,0.08);
  color: #fff !important;
}
.mega-cat-item.active a {
  color: var(--accent) !important;
}

/* Accent bar on active item */
.mega-cat-item.active a::after {
  content: "";
  position: absolute;
  left: 0; top: 50%;
  transform: translateY(-50%);
  width: 3px; height: 60%;
  background: var(--accent-gradient);
  border-radius: 0 2px 2px 0;
}

.mega-cat-thumb {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: rgba(255,255,255,0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(212,165,116,0.6);
  transition: opacity 0.18s;
}
.mega-cat-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.mega-cat-item.active .mega-cat-thumb,
.mega-cat-item a:hover .mega-cat-thumb {
  opacity: 1;
}

.mega-cat-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mega-cat-count {
  font-size: 11px;
  font-weight: 600;
  color: rgba(212,165,116,0.7);
  background: rgba(212,165,116,0.1);
  border-radius: 20px;
  padding: 1px 7px;
  flex-shrink: 0;
  transition: background 0.18s, color 0.18s;
}
.mega-cat-item.active .mega-cat-count,
.mega-cat-item a:hover .mega-cat-count {
  background: rgba(212,165,116,0.18);
  color: var(--accent);
}

.mega-cat-arrow {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.15s, transform 0.15s;
  color: rgba(255,255,255,0.4);
}
.mega-cat-item.active .mega-cat-arrow,
.mega-cat-item a:hover .mega-cat-arrow {
  opacity: 1;
  transform: translateX(2px);
}

/* Left footer */
.mega-left-footer {
  padding: 12px 16px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.mega-all-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  width: 100%;
  background: rgba(212,165,116,0.1);
  border: 1px solid rgba(212,165,116,0.2);
  color: var(--accent) !important;
  font-size: 13px;
  font-weight: 600;
  border-radius: 8px;
  text-decoration: none;
  text-transform: none !important;
  letter-spacing: normal !important;
  transition: background 0.18s, border-color 0.18s;
  box-sizing: border-box;
}
.mega-all-link::before { display: none !important; }
.mega-all-link:hover {
  background: rgba(212,165,116,0.18);
  border-color: rgba(212,165,116,0.35);
}

/* ---- Right scene panel ---- */
.mega-panel {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.mega-scene {
  position: absolute;
  inset: 0;
  display: block;
  text-decoration: none;
  cursor: pointer;
  overflow: hidden;
}
.mega-scene::before { display: none !important; }

.mega-scene-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  background-color: #1a2e22;
  transition: transform 0.5s cubic-bezier(0.4,0,0.2,1);
}
.mega-scene:hover .mega-scene-bg {
  transform: scale(1.04);
}

.mega-scene-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(6,10,8,0.78) 0%,
    rgba(10,18,13,0.55) 50%,
    rgba(6,10,8,0.3) 100%
  );
}

.mega-scene-content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 28px 32px;
  gap: 10px;
}

.mega-scene-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--accent);
  background: rgba(212,165,116,0.14);
  border: 1px solid rgba(212,165,116,0.25);
  border-radius: 20px;
  padding: 3px 10px;
  width: fit-content;
}

.mega-scene-title {
  font-size: 26px;
  font-weight: 800;
  color: #fff;
  margin: 0;
  line-height: 1.15;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 16px rgba(0,0,0,0.5);
}

.mega-scene-cta {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255,255,255,0.75);
  transition: color 0.2s, gap 0.2s;
  width: fit-content;
}
.mega-scene:hover .mega-scene-cta {
  color: #fff;
  gap: 10px;
}

/* Scene crossfade transition */
.scene-enter-active { transition: opacity 0.22s ease, transform 0.22s ease; }
.scene-leave-active { transition: opacity 0.15s ease; }
.scene-enter-from   { opacity: 0; transform: scale(1.03); }
.scene-leave-to     { opacity: 0; }

/* Overlay */
.mega-overlay {
  position: fixed;
  inset: 0;
  top: var(--header-height, 72px);
  background: rgba(0,0,0,0.4);
  z-index: 998;
  backdrop-filter: blur(3px);
}

/* Mega open/close transitions */
.mega-enter-active,
.mega-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}
.mega-enter-from,
.mega-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
.overlay-enter-active,
.overlay-leave-active { transition: opacity 0.22s ease; }
.overlay-enter-from,
.overlay-leave-to     { opacity: 0; }

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
