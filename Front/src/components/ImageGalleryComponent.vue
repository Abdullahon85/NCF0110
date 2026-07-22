<template>
  <div class="image-gallery">
    <!-- Main Image Display -->
    <div class="gallery-main" @click="toggleFullscreen">
      <transition name="fade-scale" mode="out-in">
        <img
          v-if="selectedImageUrl"
          :src="selectedImageUrl"
          :alt="alt"
          class="main-image"
          :key="selectedImageUrl"
          loading="eager"
        />
        <div v-else class="image-placeholder" :key="'placeholder'">
          <svg
            width="80"
            height="80"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <polyline points="21 15 16 10 5 21" />
          </svg>
          <span>Нет изображения</span>
        </div>
      </transition>

      <!-- Zoom Hint -->
      <div v-if="selectedImageUrl" class="zoom-hint">
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
          <line x1="11" y1="8" x2="11" y2="14" />
          <line x1="8" y1="11" x2="14" y2="11" />
        </svg>
        Нажмите для увеличения
      </div>
    </div>

    <!-- Thumbnails -->
    <div v-if="sortedImages.length > 1" class="gallery-thumbnails">
      <button
        v-for="(image, index) in sortedImages"
        :key="image.id"
        class="thumbnail"
        :class="{ active: selectedImageUrl === getImageUrl(image.image) }"
        @click="selectImage(getImageUrl(image.image))"
        :aria-label="`Изображение ${index + 1}`"
      >
        <img
          :src="getImageUrl(image.image)"
          :alt="`${alt} - превью ${index + 1}`"
          loading="lazy"
        />
      </button>
    </div>

    <!-- Fullscreen Modal -->
    <transition name="modal">
      <div
        v-if="fullscreenMode"
        class="fullscreen-overlay"
        @click="closeFullscreen"
      >
        <button
          class="fullscreen-close"
          @click="closeFullscreen"
          aria-label="Закрыть"
        >
          <svg
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        <img
          :src="selectedImageUrl"
          :alt="alt"
          class="fullscreen-image"
          @click.stop
        />

        <!-- Navigation Arrows -->
        <button
          v-if="sortedImages.length > 1"
          class="nav-arrow prev"
          @click.stop="navigateImage(-1)"
          aria-label="Предыдущее изображение"
        >
          <svg
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>

        <button
          v-if="sortedImages.length > 1"
          class="nav-arrow next"
          @click.stop="navigateImage(1)"
          aria-label="Следующее изображение"
        >
          <svg
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from "vue";
import type { Image } from "@/types";
import { getImageUrl } from "@/api";

interface Props {
  images?: Image[];
  alt: string;
}

const props = defineProps<Props>();
const selectedImageUrl = ref<string>("");
const fullscreenMode = ref(false);

const sortedImages = computed(() => {
  if (!props.images) return [];
  return [...props.images].sort((a, b) => {
    if (a.is_main && !b.is_main) return -1;
    if (!a.is_main && b.is_main) return 1;
    return (a.order || 0) - (b.order || 0);
  });
});

const selectImage = (url: string) => {
  selectedImageUrl.value = url;
};

const toggleFullscreen = () => {
  if (selectedImageUrl.value) {
    fullscreenMode.value = true;
  }
};

const closeFullscreen = () => {
  fullscreenMode.value = false;
};

const navigateImage = (direction: number) => {
  const currentIndex = sortedImages.value.findIndex(
    (img) => getImageUrl(img.image) === selectedImageUrl.value
  );

  if (currentIndex === -1) return;

  let newIndex = currentIndex + direction;

  // Wrap around
  if (newIndex < 0) newIndex = sortedImages.value.length - 1;
  if (newIndex >= sortedImages.value.length) newIndex = 0;

  selectedImageUrl.value = getImageUrl(sortedImages.value[newIndex].image);
};

const handleKeydown = (e: KeyboardEvent) => {
  if (!fullscreenMode.value) return;

  if (e.key === "Escape") {
    closeFullscreen();
  } else if (e.key === "ArrowLeft") {
    navigateImage(-1);
  } else if (e.key === "ArrowRight") {
    navigateImage(1);
  }
};

const initializeImage = () => {
  const imgs = props.images || [];
  const main = imgs.find((img) => img.is_main);
  const first = sortedImages.value[0];
  selectedImageUrl.value = getImageUrl(main?.image || first?.image || "");
};

onMounted(() => {
  initializeImage();
  window.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeydown);
});

watch(() => props.images, initializeImage, { deep: true });
</script>
