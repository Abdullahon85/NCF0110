<template>
  <div class="news-detail-page">
    <div class="container">
      <nav class="breadcrumb">
        <router-link to="/">Главная</router-link>
        <span>/</span>
        <router-link to="/news">Новости</router-link>
        <span>/</span>
        <span>{{ newsItem?.title || "Загрузка..." }}</span>
      </nav>

      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
      </div>

      <div v-else-if="error" class="error-message">
        {{ error }}
      </div>

      <article v-else-if="newsItem" class="news-article">
        <header>
          <h1>{{ newsItem.title }}</h1>
          <time :datetime="newsItem.pub_date" class="publish-date">
            {{ formatDate(newsItem.pub_date) }}
          </time>
        </header>

        <div v-if="newsItem.image" class="article-image">
          <img :src="newsItem.image" :alt="newsItem.title" />
        </div>

        <div
          v-if="newsItem && newsItem.content"
          class="article-content"
          v-html="formatContent(newsItem.content)"
        ></div>

        <div class="article-footer">
          <router-link to="/news" class="back-link">
            ← Вернуться к новостям
          </router-link>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { newsAPI } from "@/api";
import type { NewsItem } from "@/types";

const route = useRoute();

const newsItem = ref<NewsItem | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString("ru-RU", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

const formatContent = (content: string) => {
  // Простая обработка переносов строк
  return content.replace(/\n/g, "<br>");
};

onMounted(async () => {
  const slug = route.params.slug;
  if (!slug || typeof slug !== "string") {
    error.value = "Новость не найдена";
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    const response = await newsAPI.getBySlug(slug);
    newsItem.value = response.data;
  } catch (err) {
    error.value = "Ошибка загрузки новости";
    console.error("Failed to load news item:", err);
  } finally {
    loading.value = false;
  }
});
</script>

<!-- Styles in main.css -->
