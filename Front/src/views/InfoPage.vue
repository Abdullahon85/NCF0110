<template>
  <div class="container info-page">
    <nav class="breadcrumb" aria-label="Навигация">
      <router-link to="/">Главная</router-link>
      <span class="separator">›</span>
      <span class="current">{{ page?.title ?? "" }}</span>
    </nav>
    <div v-if="loading" class="loading"><div class="spinner"></div></div>
    <div v-else-if="!page" class="empty-state">
      <p>Страница не найдена</p>
      <router-link to="/" class="btn primary">На главную</router-link>
    </div>
    <article v-else>
      <h1 class="cp-title">{{ page.title }}</h1>
      <div class="info-page-text" v-html="textToHtml(page.content)"></div>
    </article>
  </div>
</template>

<script setup lang="ts">
// Page for buyers written in the admin panel (plain text, line breaks kept, HTML escaped).
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import { pagesAPI } from "@/api";
import { textToHtml } from "@/utils/richText";

const route = useRoute();
const page = ref<{ title: string; content: string } | null>(null);
const loading = ref(true);

watch(
  () => route.params.slug,
  async (slug) => {
    if (!slug) return;
    loading.value = true;
    try {
      page.value = (await pagesAPI.get(String(slug))).data;
    } catch {
      page.value = null;
    } finally {
      loading.value = false;
    }
  },
  { immediate: true },
);
</script>
