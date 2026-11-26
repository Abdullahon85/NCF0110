<template>
  <div class="filter-group facet">
    <label class="facet-title">{{ title }}</label>
    <div class="facet-items">
      <label
        v-for="item in visible"
        :key="item.key"
        class="facet-item"
        :class="{ 'is-empty': item.count === 0 && !item.checked }"
      >
        <input
          type="checkbox"
          :checked="item.checked"
          :disabled="item.count === 0 && !item.checked"
          @change="emit('toggle', item.key)"
        />
        <span class="facet-label">{{ item.label }}</span>
        <span class="facet-count">{{ item.count }}</span>
      </label>
    </div>
    <button
      v-if="items.length > limit"
      type="button"
      class="facet-more"
      @click="expanded = !expanded"
    >
      {{ expanded ? "Свернуть" : `Ещё ${items.length - limit}` }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

export type FacetItem = { key: string; label: string; count: number; checked: boolean };

const props = withDefaults(defineProps<{ title: string; items: FacetItem[]; limit?: number }>(), {
  limit: 6,
});
const emit = defineEmits<{ (e: "toggle", key: string): void }>();

const expanded = ref(false);
// Selected values always stay visible, even beyond the first `limit`.
const visible = computed(() =>
  expanded.value ? props.items : props.items.filter((item, i) => i < props.limit || item.checked),
);
</script>
