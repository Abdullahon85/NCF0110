<template>
  <nav v-if="!isAdminRoute" class="bottom-nav">
    <router-link
      v-for="tab in tabs"
      :key="tab.to"
      :to="tab.to"
      class="bottom-nav-item"
      :class="{ active: isActive(tab) }"
      @click="handleClick(tab)"
    >
      <span class="bottom-nav-icon" v-html="tab.icon"></span>
      <span v-if="tab.badge && tab.badge() > 0" class="bottom-nav-badge">{{ tab.badge() }}</span>
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

<style scoped src="@/styles/components/BottomNav.css"></style>
