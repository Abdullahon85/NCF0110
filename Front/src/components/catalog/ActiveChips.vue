<template>
  <div v-if="chips.length" class="active-chips" aria-label="Выбранные фильтры">
    <button
      v-for="chip in chips"
      :key="chip.key"
      type="button"
      class="active-chip"
      :aria-label="`Убрать фильтр: ${chip.label}`"
      @click="emit('remove', chip.key)"
    >
      {{ chip.label }} <span aria-hidden="true">×</span>
    </button>
    <button type="button" class="active-chips-clear" @click="emit('clear')">Сбросить все</button>
  </div>
</template>

<script setup lang="ts">
import type { Chip } from "@/utils/catalogQuery";

defineProps<{ chips: Chip[] }>();
const emit = defineEmits<{ (e: "remove", key: string): void; (e: "clear"): void }>();
</script>
