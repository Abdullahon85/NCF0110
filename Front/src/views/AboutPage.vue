<template>
  <div class="about-page">
    <div class="container">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
      </div>

      <div v-else-if="error" class="error-message">
        {{ error }}
      </div>

      <div v-else-if="aboutContent" class="about-content">
        <h1>{{ aboutContent.title }}</h1>

        <div v-if="aboutContent.image" class="about-image">
          <img :src="aboutContent.image" :alt="aboutContent.title" />
        </div>

        <div
          class="content-text"
          v-html="formatContent(aboutContent.content)"
        ></div>
      </div>

      <div v-else class="empty-content">
        <p>Информация о компании скоро появится</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { aboutAPI } from "@/api";
import type { AboutContent } from "@/types";

const aboutContent = ref<AboutContent | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

const formatContent = (content: string) => {
  return content.replace(/\n/g, "<br>");
};

onMounted(async () => {
  try {
    loading.value = true;
    const response = await aboutAPI.get();
    aboutContent.value = response.data;
  } catch (err) {
    error.value = "Ошибка загрузки информации";
    console.error("Failed to load about content:", err);
  } finally {
    loading.value = false;
  }
});
</script>

<!-- Styles in main.css -->
