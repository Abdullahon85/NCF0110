<template>
  <svg
    class="ad-icon"
    viewBox="0 0 24 24"
    width="20"
    height="20"
    fill="none"
    stroke="currentColor"
    stroke-width="1.75"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
    v-html="ICON_PATHS[name]"
  ></svg>
</template>

<script setup lang="ts">
import { ICON_PATHS } from "./icons";

defineProps<{ name: string }>();
</script>
