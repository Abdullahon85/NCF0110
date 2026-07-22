<template>
  <div class="news-page">
    <div class="container">
      <h1>Новости</h1>

      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
      </div>

      <div v-else-if="error" class="error-message">
        {{ error }}
      </div>

      <div v-else-if="news.length" class="news-grid">
        <NewsCardComponent
          v-for="item in news"
          :key="item.id"
          :news-item="item"
        />
      </div>

      <div v-else class="empty-news">
        <p>Новостей пока нет</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { newsAPI } from "@/api";
import NewsCardComponent from "@/components/NewsCardComponent.vue";
import type { NewsItem } from "@/types";

const news = ref<NewsItem[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    loading.value = true;
    const response = await newsAPI.getAll();
    news.value =
      "results" in response.data ? response.data.results : response.data;
  } catch (err) {
    error.value = "Ошибка загрузки новостей";
    console.error("Failed to load news:", err);
  } finally {
    loading.value = false;
  }
});
</script>

<!-- Styles in main.css -->
