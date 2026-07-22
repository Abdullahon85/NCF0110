<template>
  <article class="news-card">
    <router-link :to="`/news/${newsItem.slug}`" class="card-link">
      <div v-if="newsItem.image" class="card-image">
        <img :src="newsItem.image" :alt="newsItem.title" />
      </div>

      <div class="card-content">
        <time :datetime="newsItem.pub_date" class="card-date">
          {{ formatDate(newsItem.pub_date) }}
        </time>

        <h3 class="card-title">{{ newsItem.title }}</h3>

        <p class="card-preview">
          {{ newsItem.preview }}
        </p>

        <span class="card-more">Читать далее →</span>
      </div>
    </router-link>
  </article>
</template>

<script setup lang="ts">
import type { NewsItem } from "@/types";

defineProps<{ newsItem: NewsItem }>();

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString("ru-RU", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};
</script>

<!-- Styles in main.css -->
