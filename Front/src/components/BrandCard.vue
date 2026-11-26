<!-- src/components/BrandCard.vue -->
<template>
  <div class="bc-card" @click="navigateToBrand">
    <!-- Logo area -->
    <div class="bc-logo-wrap">
      <img
        v-if="brand.image"
        :src="brand.image"
        :alt="brand.name"
        class="bc-logo-img"
        loading="lazy"
        decoding="async"
      />
      <div v-else class="bc-logo-placeholder">
        {{ brand.name[0] }}
      </div>

      <!-- Product count badge -->
      <span class="bc-badge">{{ brand.products_count }} тов.</span>
    </div>

    <!-- Info area -->
    <div class="bc-body">
      <div class="bc-name-row">
        <h3 class="bc-name">{{ brand.name }}</h3>
        <svg class="bc-arrow" viewBox="0 0 20 20" fill="none">
          <path
            d="M4 10h12M11 5l5 5-5 5"
            stroke="currentColor"
            stroke-width="1.6"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </div>

      <p v-if="brand.description" class="bc-desc">{{ brand.description }}</p>
      <p v-else class="bc-desc bc-desc--empty">Продукция бренда</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import type { Brand } from "@/types";

const props = defineProps<{ brand: Brand }>();
const router = useRouter();
const navigateToBrand = () => router.push(`/brands/${props.brand.slug}`);
</script>

<style scoped src="@/styles/components/BrandCard.css"></style>
