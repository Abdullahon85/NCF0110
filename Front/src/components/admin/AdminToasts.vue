<template>
  <div class="admin-toasts" role="status" aria-live="polite">
    <div v-for="t in toasts" :key="t.id" class="admin-toast" :class="`is-${t.tone}`">
      <span class="admin-toast-text">{{ t.text }}</span>
      <button type="button" class="admin-toast-close" aria-label="Закрыть" @click="dismiss(t.id)">
        ×
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { dismiss, toasts } from "./toast";
</script>
