<!-- src/components/BrandCard.vue -->
<template>
  <div class="bc-card" @click="navigateToBrand">
    <!-- Logo area -->
    <div class="bc-logo-wrap">
      <img
        v-if="brand.image"
        :src="brand.image"
        :alt="brand.name"
        class="bc-logo-img"
        loading="lazy"
        decoding="async"
      />
      <div v-else class="bc-logo-placeholder">
        {{ brand.name[0] }}
      </div>

      <!-- Product count badge -->
      <span class="bc-badge">{{ brand.products_count }} тов.</span>
    </div>

    <!-- Info area -->
    <div class="bc-body">
      <div class="bc-name-row">
        <h3 class="bc-name">{{ brand.name }}</h3>
        <svg class="bc-arrow" viewBox="0 0 20 20" fill="none">
          <path d="M4 10h12M11 5l5 5-5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <p v-if="brand.description" class="bc-desc">{{ brand.description }}</p>
      <p v-else class="bc-desc bc-desc--empty">Продукция бренда</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import type { Brand } from "@/types";

const props = defineProps<{ brand: Brand }>();
const router = useRouter();
const navigateToBrand = () => router.push(`/brands/${props.brand.slug}`);
</script>

<style scoped>
/* ── Card shell ── */
.bc-card {
  background: var(--white);
  border-radius: 20px;
  border: 1px solid var(--gray-100);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.bc-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 32px rgba(27, 67, 50, 0.13);
  border-color: rgba(27, 67, 50, 0.25);
}

/* ── Logo area ── */
.bc-logo-wrap {
  position: relative;
  height: 140px;
  background: linear-gradient(145deg, #f8faf8 0%, #eef3ef 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--gray-100);
  flex-shrink: 0;
}

.bc-logo-img {
  max-width: 65%;
  max-height: 65%;
  object-fit: contain;
  transition: transform 0.28s ease;
}

.bc-card:hover .bc-logo-img {
  transform: scale(1.07);
}

.bc-logo-placeholder {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  background: var(--primary-gradient);
  color: #fff;
  font-size: 2rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.28s ease;
}

.bc-card:hover .bc-logo-placeholder {
  transform: scale(1.07);
}

/* Badge */
.bc-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(27, 67, 50, 0.08);
  color: var(--primary, #1b4332);
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 999px;
  border: 1px solid rgba(27, 67, 50, 0.12);
  letter-spacing: 0.03em;
}

/* ── Body ── */
.bc-body {
  padding: 16px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.bc-name-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.bc-name {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: var(--gray-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.18s ease;
}

.bc-card:hover .bc-name {
  color: var(--primary, #1b4332);
}

/* Arrow icon */
.bc-arrow {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  color: var(--gray-300);
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity 0.2s ease, transform 0.2s ease, color 0.2s ease;
}

.bc-card:hover .bc-arrow {
  opacity: 1;
  transform: translateX(0);
  color: var(--primary, #1b4332);
}

/* Description */
.bc-desc {
  margin: 0;
  font-size: 12.5px;
  color: var(--gray-500);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bc-desc--empty {
  color: var(--gray-400);
  font-style: italic;
}

/* ── Mobile ── */
@media (max-width: 640px) {
  .bc-logo-wrap {
    height: 110px;
  }

  .bc-body {
    padding: 12px 14px 14px;
  }

  .bc-name {
    font-size: 13px;
  }
}
</style>
