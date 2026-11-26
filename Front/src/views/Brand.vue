<!-- src/views/Brand.vue -->
<template>
  <div class="brand-page">
    <!-- ── Loading ── -->
    <div v-if="loading" class="brand-loading">
      <div class="brand-loading-spinner"></div>
      <p>Загрузка бренда...</p>
    </div>

    <!-- ── Error ── -->
    <div v-else-if="error" class="brand-error">
      <svg
        width="56"
        height="56"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
      >
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <h3>{{ error }}</h3>
      <router-link to="/brands" class="brand-back-btn">← Все бренды</router-link>
    </div>

    <!-- ── Content ── -->
    <template v-else-if="brand">
      <!-- Hero -->
      <div class="brand-hero">
        <div class="brand-hero-inner container">
          <router-link to="/brands" class="brand-hero-back">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <polyline points="15 18 9 12 15 6" />
            </svg>
            Бренды
          </router-link>
          <div class="brand-hero-card">
            <div v-if="brand.image" class="brand-hero-logo">
              <img :src="getImageUrl(brand.image)" :alt="brand.name" />
            </div>
            <div v-else class="brand-hero-logo brand-hero-logo--placeholder">
              {{ brand.name?.charAt(0) }}
            </div>
            <div class="brand-hero-info">
              <h1>{{ brand.name }}</h1>
              <p
                v-if="brand.description"
                class="brand-hero-desc"
                v-html="formatContent(brand.description)"
              ></p>
            </div>
          </div>
        </div>
      </div>

      <div class="container brand-container">
        <ProductListing :fixed="{ brand: brand.slug }" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import { brandsAPI, getImageUrl } from "@/api";
import type { Brand } from "@/types";
import { textToHtml } from "@/utils/richText";
import ProductListing from "@/components/catalog/ProductListing.vue";

const route = useRoute();
const brand = ref<Brand | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const formatContent = textToHtml; // escapes HTML, keeps line breaks

watch(
  () => route.params.slug,
  async (slug) => {
    if (!slug) return;
    loading.value = true;
    error.value = null;
    try {
      brand.value = (await brandsAPI.getBySlug(String(slug))).data;
    } catch (err: any) {
      brand.value = null;
      error.value =
        err?.response?.status === 404 ? "Бренд не найден" : "Не удалось загрузить бренд";
    } finally {
      loading.value = false;
    }
  },
  { immediate: true },
);
</script>

<style scoped src="@/styles/views/Brand.css"></style>
