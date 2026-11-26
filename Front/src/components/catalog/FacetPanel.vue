<template>
  <div class="facet-panel">
    <div v-if="facets.categories.length" class="filter-group facet">
      <label class="facet-title">Подразделы</label>
      <router-link
        v-for="c in facets.categories"
        :key="c.slug"
        :to="`/catalog/${c.slug}`"
        class="facet-link"
      >
        <span class="facet-label">{{ c.name }}</span>
        <span class="facet-count">{{ c.count }}</span>
      </router-link>
    </div>

    <label class="facet-switch">
      <input type="checkbox" :checked="state.inStock" @change="set({ inStock: !state.inStock })" />
      Только в наличии <span class="facet-count">{{ facets.in_stock }}</span>
    </label>

    <template v-for="group in shownGroups" :key="group.key">
      <FacetRange
        v-if="group.kind === 'range'"
        :title="group.title"
        :unit="group.unit"
        :min="group.min"
        :max="group.max"
        :model-value="group.value"
        @change="group.apply"
      />
      <FacetList v-else :title="group.title" :items="group.items" @toggle="group.toggle" />
    </template>

    <button
      v-if="hiddenCount > 0"
      type="button"
      class="facet-all"
      :aria-expanded="showAll"
      @click="showAll = !showAll"
    >
      {{ showAll ? "Меньше фильтров" : `Все фильтры (+${hiddenCount})` }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import FacetList, { type FacetItem } from "./FacetList.vue";
import FacetRange from "./FacetRange.vue";
import type { CatalogFacets, CatalogState, Range } from "@/utils/catalogQuery";

// Like shop.nag.uz: the first 5 filter groups are open, the rest behind "Все фильтры (+N)".
const VISIBLE_GROUPS = 5;

// `hide`: filters fixed by the page itself (brand page: "brand") are not offered again.
const props = withDefaults(
  defineProps<{ facets: CatalogFacets; state: CatalogState; hide?: string[] }>(),
  { hide: () => [] },
);
const emit = defineEmits<{ (e: "update", state: CatalogState): void }>();
const showAll = ref(false);

type Group =
  | { key: string; kind: "list"; title: string; items: FacetItem[]; toggle: (key: string) => void }
  | {
      key: string;
      kind: "range";
      title: string;
      unit: string;
      min: number;
      max: number;
      value: Range;
      apply: (r: Range) => void;
    };

// Every change of a filter starts again from the first page.
function set(patch: Partial<CatalogState>) {
  emit("update", { ...structuredClone(props.state), ...patch, page: 1 });
}
const toggled = (list: string[], key: string) =>
  list.includes(key) ? list.filter((x) => x !== key) : [...list, key];

const groups = computed<Group[]>(() => {
  const { facets, state } = props;
  const out: Group[] = [];
  if (
    facets.price.min !== null &&
    facets.price.max !== null &&
    facets.price.min < facets.price.max
  ) {
    out.push({
      key: "price",
      kind: "range",
      title: "Цена",
      unit: "сум",
      min: facets.price.min,
      max: facets.price.max,
      value: { min: state.priceMin, max: state.priceMax },
      apply: (r) => set({ priceMin: r.min, priceMax: r.max }),
    });
  }
  if (facets.brands.length) {
    out.push({
      key: "brand",
      kind: "list",
      title: "Бренд",
      items: facets.brands.map((b) => ({
        key: b.slug,
        label: b.name,
        count: b.count,
        checked: state.brands.includes(b.slug),
      })),
      toggle: (key) => set({ brands: toggled(state.brands, key) }),
    });
  }
  if (facets.statuses.length) {
    out.push({
      key: "status",
      kind: "list",
      title: "Статус товара",
      items: facets.statuses.map((s) => ({
        key: s.value,
        label: s.label,
        count: s.count,
        checked: state.statuses.includes(s.value),
      })),
      toggle: (key) => set({ statuses: toggled(state.statuses, key) }),
    });
  }
  for (const f of facets.features) {
    if (f.type === "range") {
      out.push({
        key: `f${f.id}`,
        kind: "range",
        title: f.name,
        unit: f.unit,
        min: f.min,
        max: f.max,
        value: state.ranges[f.id] ?? { min: null, max: null },
        apply: (r) => {
          const ranges = { ...state.ranges };
          if (r.min === null && r.max === null) delete ranges[f.id];
          else ranges[f.id] = r;
          set({ ranges });
        },
      });
      continue;
    }
    const selected = state.lists[f.id] ?? [];
    out.push({
      key: `f${f.id}`,
      kind: "list",
      title: f.name,
      items: f.values.map((v) => ({
        key: v.ids.join("-"),
        label: v.value,
        count: v.count,
        checked: v.ids.some((id) => selected.includes(id)),
      })),
      toggle: (key) => {
        const ids = key.split("-").map(Number);
        const on = ids.some((id) => selected.includes(id));
        const next = on ? selected.filter((id) => !ids.includes(id)) : [...selected, ...ids];
        const lists = { ...state.lists };
        if (next.length) lists[f.id] = next;
        else delete lists[f.id];
        set({ lists });
      },
    });
  }
  return out;
});

// A group with a selection stays visible even when it is beyond the first five.
const isActive = (g: Group) =>
  g.kind === "range"
    ? g.value.min !== null || g.value.max !== null
    : g.items.some((i) => i.checked);
const offered = computed(() => groups.value.filter((g) => !props.hide.includes(g.key)));
const shownGroups = computed(() =>
  showAll.value ? offered.value : offered.value.filter((g, i) => i < VISIBLE_GROUPS || isActive(g)),
);
// How many groups the "Все фильтры" button opens (when collapsed).
const hiddenCount = computed(() =>
  showAll.value
    ? Math.max(0, offered.value.length - VISIBLE_GROUPS)
    : offered.value.length - shownGroups.value.length,
);
</script>
