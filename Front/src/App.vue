//App.vue
<template>
  <div id="app">
    <HeaderComponent v-if="!isAdminRoute" />
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <FooterComponent v-if="!isAdminRoute" />
    <BottomNav />

    <!-- Scroll to Top Button -->
    <transition name="fade-up">
      <button
        v-show="showScrollTop"
        @click="scrollToTop"
        class="scroll-to-top"
        aria-label="Tepaga qaytish"
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="18 15 12 9 6 15"></polyline>
        </svg>
      </button>
    </transition>
  </div>
</template>

<script setup lang="ts">
import {
  ref,
  computed,
  onMounted,
  onBeforeUnmount,
  defineAsyncComponent,
} from "vue";
import { useRoute } from "vue-router";

// Lazy load Header, Footer, and BottomNav
const HeaderComponent = defineAsyncComponent(
  () => import("@/components/HeaderComponent.vue"),
);
const FooterComponent = defineAsyncComponent(
  () => import("@/components/FooterComponent.vue"),
);
const BottomNav = defineAsyncComponent(
  () => import("@/components/BottomNav.vue"),
);

const route = useRoute();
const showScrollTop = ref(false);

const isAdminRoute = computed(() => {
  return route.path.startsWith("/admin");
});

const handleScroll = () => {
  showScrollTop.value = window.scrollY > 300;
};

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
};

onMounted(() => {
  window.addEventListener("scroll", handleScroll, { passive: true });
});

onBeforeUnmount(() => {
  window.removeEventListener("scroll", handleScroll);
});
</script>

<!-- All styles are in main.css -->
