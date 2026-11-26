<template>
  <div class="ad-dash">
    <section class="ad-attention" aria-labelledby="attention-title">
      <h2 id="attention-title" class="ad-section-title">Требует внимания</h2>
      <p v-if="loading" class="ad-attention-empty">Загрузка…</p>
      <p v-else-if="failed" class="ad-attention-empty">
        Не удалось загрузить данные. Обновите страницу.
      </p>
      <ul v-else-if="attention.length" class="ad-attention-list">
        <li v-for="item in attention" :key="item.key">
          <router-link :to="item.to" class="ad-attention-item">
            <span class="ad-attention-count">{{ item.count }}</span>
            <span class="ad-attention-label">{{ item.label }}</span>
            <AdminIcon name="arrow" />
          </router-link>
        </li>
      </ul>
      <p v-else class="ad-attention-empty is-clear">
        <AdminIcon name="check" />
        Новых заказов и сообщений нет
      </p>
    </section>

    <section aria-labelledby="figures-title">
      <h2 id="figures-title" class="ad-section-title">Сайт в цифрах</h2>
      <ul class="ad-figures">
        <li v-for="figure in figures" :key="figure.label">
          <router-link :to="figure.to" class="ad-figure">
            <span class="ad-figure-value">{{ figure.value }}</span>
            <span class="ad-figure-label">{{ figure.label }}</span>
          </router-link>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import AdminIcon from "@/components/admin/AdminIcon.vue";
import { statsAPI } from "@/api/admin";
import { attentionItems, quietFigures, type DashboardStats } from "@/components/admin/dashboard";

const stats = ref<DashboardStats>({});
const loading = ref(true);
const failed = ref(false);

const attention = computed(() => attentionItems(stats.value));
const figures = computed(() => quietFigures(stats.value));

async function loadStats() {
  loading.value = true;
  failed.value = false;
  try {
    const response = await statsAPI.getDashboard();
    stats.value = response.data;
  } catch (e) {
    console.error("Failed to load stats:", e);
    failed.value = true;
  } finally {
    loading.value = false;
  }
}

onMounted(loadStats);
</script>
