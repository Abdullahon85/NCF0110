<template>
  <div v-if="banners.length || loading" class="banner-slider">
    <!-- Skeleton Loading -->
    <div v-if="loading" class="banner-skeleton skeleton">
      <div class="skeleton-image"></div>
      <div class="skeleton-content">
        <div class="skeleton-title"></div>
        <div class="skeleton-text"></div>
      </div>
    </div>

    <!-- Slider Content -->
    <template v-else>
      <div ref="sliderRef" class="slider-container">
        <div class="slides-wrapper" :style="{ transform: `translateX(-${currentIndex * 100}%)` }">
          <div v-for="banner in banners" :key="banner.id" class="slide">
            <img :src="banner.image" :alt="banner.title" class="slide-image" loading="lazy" />
            <div class="slide-overlay"></div>
            <div class="slide-content">
              <h2 class="slide-title">{{ banner.title }}</h2>
              <p v-if="banner.description" class="slide-description">
                {{ banner.description }}
              </p>
              <a
                v-if="banner.link"
                :href="banner.link"
                class="slide-link"
                target="_blank"
                rel="noopener noreferrer"
              >
                Подробнее
                <svg
                  width="16"
                  height="16"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  viewBox="0 0 24 24"
                >
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Arrows -->
      <button
        v-if="banners.length > 1"
        class="nav-button nav-prev"
        aria-label="Предыдущий баннер"
        @click="prev"
      >
        <svg
          width="24"
          height="24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          viewBox="0 0 24 24"
        >
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>
      <button
        v-if="banners.length > 1"
        class="nav-button nav-next"
        aria-label="Следующий баннер"
        @click="next"
      >
        <svg
          width="24"
          height="24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          viewBox="0 0 24 24"
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </button>

      <!-- Dots Pagination -->
      <div v-if="banners.length > 1" class="dots-container">
        <button
          v-for="(_, index) in banners"
          :key="index"
          class="dot"
          :class="{ active: index === currentIndex }"
          :aria-label="`Перейти к баннеру ${index + 1}`"
          @click="goTo(index)"
        />
      </div>
    </template>
  </div>

  <!-- Empty State -->
  <div v-else-if="!loading && !banners.length" class="banner-empty">
    <!-- Можно показать placeholder или ничего -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import type { Banner } from "@/types";

interface Props {
  banners: Banner[];
  loading?: boolean;
  autoplayInterval?: number; // в миллисекундах
  pauseOnHover?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  autoplayInterval: 5000,
  pauseOnHover: true,
});

const currentIndex = ref(0);
const sliderRef = ref<HTMLElement | null>(null);
let autoplayTimer: ReturnType<typeof setInterval> | null = null;
let isPaused = false;

const next = () => {
  currentIndex.value = (currentIndex.value + 1) % props.banners.length;
  resetAutoplay();
};

const prev = () => {
  currentIndex.value = (currentIndex.value - 1 + props.banners.length) % props.banners.length;
  resetAutoplay();
};

const goTo = (index: number) => {
  currentIndex.value = index;
  resetAutoplay();
};

const startAutoplay = () => {
  if (props.banners.length <= 1) return;
  stopAutoplay();
  autoplayTimer = setInterval(() => {
    if (!isPaused) {
      currentIndex.value = (currentIndex.value + 1) % props.banners.length;
    }
  }, props.autoplayInterval);
};

const stopAutoplay = () => {
  if (autoplayTimer) {
    clearInterval(autoplayTimer);
    autoplayTimer = null;
  }
};

const resetAutoplay = () => {
  stopAutoplay();
  startAutoplay();
};

const handleMouseEnter = () => {
  if (props.pauseOnHover) isPaused = true;
};

const handleMouseLeave = () => {
  if (props.pauseOnHover) isPaused = false;
};

// Touch/Swipe support
let touchStartX = 0;
let touchEndX = 0;

const handleTouchStart = (e: TouchEvent) => {
  touchStartX = e.changedTouches[0].screenX;
};

const handleTouchEnd = (e: TouchEvent) => {
  touchEndX = e.changedTouches[0].screenX;
  handleSwipe();
};

const handleSwipe = () => {
  const swipeThreshold = 50;
  const diff = touchStartX - touchEndX;

  if (Math.abs(diff) > swipeThreshold) {
    if (diff > 0) {
      next();
    } else {
      prev();
    }
  }
};

watch(
  () => props.banners,
  (newBanners) => {
    if (newBanners.length) {
      currentIndex.value = 0;
      startAutoplay();
    }
  },
  { immediate: true },
);

onMounted(() => {
  if (sliderRef.value) {
    sliderRef.value.addEventListener("mouseenter", handleMouseEnter);
    sliderRef.value.addEventListener("mouseleave", handleMouseLeave);
    sliderRef.value.addEventListener("touchstart", handleTouchStart, {
      passive: true,
    });
    sliderRef.value.addEventListener("touchend", handleTouchEnd, {
      passive: true,
    });
  }
});

onUnmounted(() => {
  stopAutoplay();
  if (sliderRef.value) {
    sliderRef.value.removeEventListener("mouseenter", handleMouseEnter);
    sliderRef.value.removeEventListener("mouseleave", handleMouseLeave);
    sliderRef.value.removeEventListener("touchstart", handleTouchStart);
    sliderRef.value.removeEventListener("touchend", handleTouchEnd);
  }
});
</script>

<style scoped src="@/styles/components/BannerSlider.css"></style>
