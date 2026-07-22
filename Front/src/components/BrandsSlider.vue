<template>
  <div class="clients-section">
    <div class="slider-wrapper" @mouseenter="pause" @mouseleave="resume">
      <button class="nav-btn left" @click="prev" aria-label="Предыдущий">
        ‹
      </button>

      <div class="clients-track" :style="trackStyle">
        <div
          v-for="(brand, index) in loopedBrands"
          :key="`${brand.id || brand.slug}-${index}`"
          class="client-logo"
        >
          <router-link :to="`/brands/${brand.slug}`">
            <template v-if="brand.image">
              <img
                :src="getImageUrl(brand.image)"
                :alt="brand.name"
                loading="lazy"
              />
            </template>
            <template v-else>
              <div class="brand-placeholder">
                {{ brand.name ? brand.name.charAt(0).toUpperCase() : "?" }}
              </div>
            </template>
          </router-link>
        </div>
      </div>

      <button class="nav-btn right" @click="next" aria-label="Следующий">
        ›
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import type { Brand } from "@/types";
import { getImageUrl } from "@/api";

const props = defineProps<{ brands: Brand[] }>();

// Дублируем для бесконечной прокрутки
const loopedBrands = computed(() => {
  if (props.brands.length === 0) return [];
  return [...props.brands, ...props.brands, ...props.brands];
});

const current = ref(0);
const autoplaySpeed = 3000;
let interval: any = null;
let isTransitioning = false;

// On mobile we use native CSS scroll — JS transform must be disabled
const isMobile = () => window.matchMedia("(max-width: 768px)").matches;

// Стиль смещения - используем calc для точного позиционирования
const trackStyle = computed(() => {
  if (isMobile()) return {}; // let CSS handle it
  const itemWidth = `calc((100% / 6))`;
  return {
    transform: `translateX(calc(-${current.value} * ${itemWidth}))`,
    transition: isTransitioning
      ? "transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)"
      : "none",
  };
});

function next() {
  if (props.brands.length === 0) return;

  isTransitioning = true;
  current.value++;

  // Когда доходим до конца первой копии, возвращаемся к началу
  if (current.value >= props.brands.length) {
    setTimeout(() => {
      isTransitioning = false;
      current.value = 0;
    }, 500);
  }
}

function prev() {
  if (props.brands.length === 0) return;

  if (current.value === 0) {
    isTransitioning = false;
    current.value = props.brands.length;
    setTimeout(() => {
      isTransitioning = true;
      current.value--;
    }, 10);
  } else {
    isTransitioning = true;
    current.value--;
  }
}

function startAutoplay() {
  if (props.brands.length === 0) return;
  if (isMobile()) return; // native scroll on mobile — no JS autoplay needed
  interval = setInterval(next, autoplaySpeed);
}

function pause() {
  clearInterval(interval);
}

function resume() {
  startAutoplay();
}

onMounted(() => {
  startAutoplay();
});

onUnmounted(() => {
  clearInterval(interval);
});
</script>

<!-- Styles in main.css -->
