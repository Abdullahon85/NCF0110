<template>
  <div class="filter-group price-filter facet">
    <label class="facet-title"
      >{{ title }}<span v-if="unit">, {{ unit }}</span></label
    >
    <div class="price-inputs">
      <input
        type="number"
        :value="low"
        :min="min"
        :max="max"
        :placeholder="`от ${format(min)}`"
        :aria-label="`${title}: от`"
        @input="onInput('min', $event)"
      />
      <span>—</span>
      <input
        type="number"
        :value="high"
        :min="min"
        :max="max"
        :placeholder="`до ${format(max)}`"
        :aria-label="`${title}: до`"
        @input="onInput('max', $event)"
      />
    </div>
    <div class="range-wrapper">
      <input
        class="range range-min"
        type="range"
        :min="min"
        :max="max"
        :step="step"
        :value="low ?? min"
        :aria-label="`${title}: от`"
        @input="onInput('min', $event)"
      />
      <input
        class="range range-max"
        type="range"
        :min="min"
        :max="max"
        :step="step"
        :value="high ?? max"
        :aria-label="`${title}: до`"
        @input="onInput('max', $event)"
      />
      <div class="range-track" :style="trackStyle"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from "vue";
import { rangeFromInputs, type Range } from "@/utils/catalogQuery";

// A numeric range (price or a characteristic). A bound equal to the edge of the range means
// "not limited" and is sent as null; changes are applied 600 ms after the last input.
const props = defineProps<{
  title: string;
  unit?: string;
  min: number;
  max: number;
  modelValue: Range;
}>();
const emit = defineEmits<{ (e: "change", value: Range): void }>();

const low = ref<number | null>(props.modelValue.min);
const high = ref<number | null>(props.modelValue.max);
watch(
  () => props.modelValue,
  (v) => {
    low.value = v.min;
    high.value = v.max;
  },
);

const step = computed(() => {
  const span = props.max - props.min;
  if (span > 10000) return Math.max(1, Math.round(span / 200));
  if (span > 1000) return Math.max(1, Math.round(span / 100));
  return span > 20 ? 1 : 0.1;
});
const pct = (v: number) =>
  props.max === props.min ? 0 : ((v - props.min) / (props.max - props.min)) * 100;
const trackStyle = computed(() => ({
  left: `${pct(low.value ?? props.min)}%`,
  right: `${100 - pct(high.value ?? props.max)}%`,
}));
const format = (n: number) => new Intl.NumberFormat("ru-RU").format(n);

let timer: ReturnType<typeof setTimeout> | null = null;
onUnmounted(() => timer && clearTimeout(timer));

function onInput(side: "min" | "max", e: Event) {
  const raw = (e.target as HTMLInputElement).value;
  const n = raw === "" ? null : Number(raw);
  if (side === "min") low.value = n;
  else high.value = n;
  if (timer) clearTimeout(timer);
  timer = setTimeout(() => {
    emit("change", rangeFromInputs(low.value, high.value, props.min, props.max, step.value));
  }, 600);
}
</script>
