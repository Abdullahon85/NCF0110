<template>
  <div class="banner-slider" v-if="banners.length || loading">
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
      <div class="slider-container" ref="sliderRef">
        <div
          class="slides-wrapper"
          :style="{ transform: `translateX(-${currentIndex * 100}%)` }"
        >
          <div v-for="banner in banners" :key="banner.id" class="slide">
            <img
              :src="banner.image"
              :alt="banner.title"
              class="slide-image"
              loading="lazy"
            />
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
        @click="prev"
        aria-label="Предыдущий баннер"
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
        @click="next"
        aria-label="Следующий баннер"
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
          @click="goTo(index)"
          :aria-label="`Перейти к баннеру ${index + 1}`"
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
  currentIndex.value =
    (currentIndex.value - 1 + props.banners.length) % props.banners.length;
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

<style scoped>
.banner-slider {
  position: relative;
  width: 100%;
  overflow: hidden;
  border-radius: 16px;
  background: var(--gray-100);
}

.slider-container {
  position: relative;
  width: 100%;
  aspect-ratio: 21 / 9;
  overflow: hidden;
}

.slides-wrapper {
  display: flex;
  height: 100%;
  transition: transform 0.5s ease-in-out;
  will-change: transform;
}

.slide {
  position: relative;
  flex-shrink: 0;
  width: 100%;
  height: 100%;
}

.slide-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.slide-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to right,
    rgba(0, 0, 0, 0.6) 0%,
    rgba(0, 0, 0, 0.2) 50%,
    transparent 100%
  );
}

.slide-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 32px 48px;
  color: white;
  max-width: 600px;
}

.slide-title {
  font-size: clamp(1.25rem, 4vw, 2.5rem);
  font-weight: 700;
  margin: 0 0 12px;
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  color: var(--white);
}

.slide-description {
  font-size: clamp(0.875rem, 2vw, 1.125rem);
  margin: 0 0 20px;
  line-height: 1.5;
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: var(--white);
}

.slide-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--primary-color, #3bf6446e);
  color: white;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9375rem;
  text-decoration: none;
  transition: all 0.2s ease;
}

.slide-link:hover {
  background: var(--primary-hover, #2563eb);
  transform: translateX(4px);
}

.slide-link svg {
  transition: transform 0.2s ease;
}

.slide-link:hover svg {
  transform: translateX(4px);
}

/* Navigation Buttons */
.nav-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: var(--gray-800);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.nav-button:hover {
  background: white;
  transform: translateY(-50%) scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.nav-button:active {
  transform: translateY(-50%) scale(0.95);
}

.nav-prev {
  left: 16px;
}

.nav-next {
  right: 16px;
}

/* Dots Pagination */
.dots-container {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 10;
}

.dot {
  width: 10px;
  height: 10px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  padding: 0;
  transition: all 0.2s ease;
}

.dot:hover {
  background: rgba(255, 255, 255, 0.75);
}

.dot.active {
  background: white;
  transform: scale(1.2);
}

/* Skeleton Loading */
.banner-skeleton {
  aspect-ratio: 21 / 9;
  background: var(--gray-100);
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}

.skeleton-image {
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    var(--gray-200) 25%,
    var(--gray-100) 50%,
    var(--gray-200) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

.skeleton-content {
  position: absolute;
  bottom: 32px;
  left: 48px;
  right: 50%;
}

.skeleton-title {
  height: 32px;
  width: 60%;
  background: var(--gray-300);
  border-radius: 4px;
  margin-bottom: 12px;
}

.skeleton-text {
  height: 20px;
  width: 80%;
  background: var(--gray-300);
  border-radius: 4px;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Empty State */
.banner-empty {
  display: none;
}
</style>
