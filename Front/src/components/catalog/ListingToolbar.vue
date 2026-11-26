<template>
  <div class="topbar listing-toolbar">
    <span class="listing-total">{{ total }} {{ itemWord(total) }}</span>
    <label class="sort">
      <span>Сортировка:</span>
      <select
        :value="sort"
        @change="emit('sort', ($event.target as HTMLSelectElement).value as Sort)"
      >
        <option v-for="(label, value) in SORT_LABELS" :key="value" :value="value">
          {{ label }}
        </option>
      </select>
    </label>
    <label class="sort">
      <span>На странице:</span>
      <select
        :value="perPage"
        @change="emit('per-page', Number(($event.target as HTMLSelectElement).value) as PerPage)"
      >
        <option v-for="n in PER_PAGE" :key="n" :value="n">{{ n }}</option>
      </select>
    </label>
    <div class="view-switch" role="group" aria-label="Вид списка">
      <button
        type="button"
        :aria-pressed="view === 'grid'"
        title="Плиткой"
        @click="emit('view', 'grid')"
      >
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          aria-hidden="true"
        >
          <rect x="3" y="3" width="7" height="7" />
          <rect x="14" y="3" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" />
          <rect x="14" y="14" width="7" height="7" />
        </svg>
      </button>
      <button
        type="button"
        :aria-pressed="view === 'list'"
        title="Списком"
        @click="emit('view', 'list')"
      >
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          aria-hidden="true"
        >
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PER_PAGE, SORT_LABELS, type PerPage, type Sort } from "@/utils/catalogQuery";
import { itemWord } from "@/utils/cartOrder";

defineProps<{ total: number; sort: Sort; perPage: PerPage; view: "grid" | "list" }>();
const emit = defineEmits<{
  (e: "sort", value: Sort): void;
  (e: "per-page", value: PerPage): void;
  (e: "view", value: "grid" | "list"): void;
}>();
</script>
