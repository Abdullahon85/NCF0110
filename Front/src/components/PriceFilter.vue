// ======================================== // src/components/PriceFilter.vue //
========================================
<template>
  <div class="filter-group price-filter">
    <label>Цена</label>

    <div class="price-legend">
      <small>
        Мин: {{ formatPrice(min) }} — Макс: {{ formatPrice(max) }}
      </small>
    </div>

    <div class="price-inputs">
      <input
        type="number"
        :value="localMin"
        @input="onMinInput"
        :min="min"
        :max="max"
        placeholder="от"
      />
      <span>—</span>
      <input
        type="number"
        :value="localMax"
        @input="onMaxInput"
        :min="min"
        :max="max"
        placeholder="до"
      />
    </div>

    <div class="range-wrapper">
      <input
        class="range range-min"
        type="range"
        :min="min"
        :max="max"
        :step="step"
        :value="localMin"
        @input="onMinSlider"
      />
      <input
        class="range range-max"
        type="range"
        :min="min"
        :max="max"
        :step="step"
        :value="localMax"
        @input="onMaxSlider"
      />
      <div class="range-track" :style="trackStyle"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";

interface Props {
  min: number;
  max: number;
  modelValue: { min: number | null; max: number | null };
}

interface Emits {
  (
    e: "update:modelValue",
    value: { min: number | null; max: number | null },
  ): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const localMin = ref(props.modelValue.min ?? props.min);
const localMax = ref(props.modelValue.max ?? props.max);

const step = computed(() => {
  const range = props.max - props.min;
  // Более мелкий шаг для лучшей точности
  if (range > 10000) return Math.max(1, Math.round(range / 200));
  if (range > 1000) return Math.max(1, Math.round(range / 100));
  return 1;
});

const trackStyle = computed(() => {
  const range = props.max - props.min;
  const minPercent = ((localMin.value - props.min) / range) * 100;
  const maxPercent = ((localMax.value - props.min) / range) * 100;

  return {
    left: `${minPercent}%`,
    right: `${100 - maxPercent}%`,
  };
});

const formatPrice = (price: number): string => {
  return new Intl.NumberFormat("ru-RU").format(price);
};

const clamp = (value: number, min: number, max: number): number => {
  return Math.min(Math.max(value, min), max);
};

const emitUpdate = () => {
  emit("update:modelValue", {
    min: localMin.value,
    max: localMax.value,
  });
};

const onMinSlider = (e: Event) => {
  let value = Number((e.target as HTMLInputElement).value);
  value = clamp(value, props.min, props.max);
  if (value > localMax.value) {
    localMax.value = value;
  }
  localMin.value = value;
  emitUpdate();
};

const onMaxSlider = (e: Event) => {
  let value = Number((e.target as HTMLInputElement).value);

  // Если значение близко к максимуму (в пределах шага), ставим точно max
  if (value >= props.max - step.value) {
    value = props.max;
  } else {
    value = clamp(value, localMin.value, props.max);
  }
  localMax.value = value;
  emitUpdate();
};

const onMinInput = (e: Event) => {
  let value = Number((e.target as HTMLInputElement).value);
  value = clamp(value, props.min, localMax.value);
  localMin.value = value;
  emitUpdate();
};

const onMaxInput = (e: Event) => {
  let value = Number((e.target as HTMLInputElement).value);
  if (value >= props.max) {
    value = props.max;
  } else {
    value = clamp(value, localMin.value, props.max);
  }
  localMax.value = value;
  emitUpdate();
};

watch(
  () => props.modelValue,
  (newValue) => {
    localMin.value = newValue.min ?? props.min;
    localMax.value = newValue.max ?? props.max;
  },
);
</script>

<!-- Styles in main.css -->
