<template>
  <nav class="bottom-nav" v-if="!isAdminRoute">
    <router-link
      v-for="tab in tabs"
      :key="tab.to"
      :to="tab.to"
      class="bottom-nav-item"
      :class="{ active: isActive(tab) }"
      @click="handleClick(tab)"
    >
      <span class="bottom-nav-icon" v-html="tab.icon"></span>
      <span v-if="tab.badge && tab.badge() > 0" class="bottom-nav-badge">{{
        tab.badge()
      }}</span>
      <span class="bottom-nav-label">{{ tab.label }}</span>
    </router-link>
  </nav>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useCartStore } from "@/stores/useCartStore";
import { useFavoritesStore } from "@/stores/useFavoritesStore";

const route = useRoute();
const cartStore = useCartStore();
const favStore = useFavoritesStore();

const isAdminRoute = computed(() => route.path.startsWith("/admin"));

const tabs = [
  {
    to: "/",
    label: "Главная",
    icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    exact: true,
  },
  {
    to: "/catalog",
    label: "Каталог",
    icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>',
  },
  {
    to: "/cart",
    label: "Корзина",
    icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>',
    badge: () => cartStore.totalQty,
  },
  {
    to: "/favorites",
    label: "Избранное",
    icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
    badge: () => favStore.items.length,
  },
  {
    to: "/about",
    label: "Ещё",
    icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>',
  },
];

const isActive = (tab: (typeof tabs)[0]) => {
  if ("exact" in tab && tab.exact) {
    return route.path === tab.to;
  }
  return route.path.startsWith(tab.to);
};

const handleClick = (_tab: (typeof tabs)[0]) => {
  // Potential for extra mobile logic
};
</script>

<style scoped>
.bottom-nav {
  display: none;
}

@media (max-width: 768px) {
  .bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    display: flex;
    justify-content: space-around;
    align-items: center;
    height: 60px;
    background: rgba(255, 255, 255, 0.97);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    box-shadow: 0 -1px 8px rgba(0, 0, 0, 0.04);
    padding-bottom: env(safe-area-inset-bottom, 0);
    /* iOS Safari GPU layer — prevents nav from disappearing on scroll */
    transform: translate3d(0, 0, 0);
    -webkit-transform: translate3d(0, 0, 0);
    will-change: transform;
  }

  .bottom-nav-item {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    flex: 1;
    height: 100%;
    color: var(--gray-400);
    text-decoration: none;
    transition: color 0.15s ease;
    -webkit-tap-highlight-color: transparent;
  }

  .bottom-nav-item:active {
    opacity: 0.7;
  }

  .bottom-nav-item.active {
    color: var(--primary);
  }

  .bottom-nav-item.active .bottom-nav-icon :deep(svg) {
    stroke: var(--primary);
    stroke-width: 2.5;
  }

  .bottom-nav-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
  }

  .bottom-nav-label {
    font-size: 10px;
    font-weight: 500;
    line-height: 1;
  }

  .bottom-nav-badge {
    position: absolute;
    top: 4px;
    right: calc(50% - 20px);
    min-width: 17px;
    height: 17px;
    padding: 0 4px;
    border-radius: 99px;
    background: var(--error);
    color: var(--white);
    font-size: 10px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
    box-shadow: 0 1px 3px rgba(239, 68, 68, 0.3);
  }
}
</style>
