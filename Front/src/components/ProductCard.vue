<template>
  <div
    class="product-card"
    role="link"
    tabindex="0"
    @click="goToProduct"
    @keydown.enter="goToProduct"
    @keydown.space.prevent="goToProduct"
  >
    <!-- Action buttons overlay (top-right) -->
    <div class="pc-actions" @click.stop>
      <button
        class="card-action-btn"
        :class="{ active: isFav }"
        :title="isFav ? 'Убрать из избранного' : 'В избранное'"
        @click.stop="toggleFav"
      >
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
          />
        </svg>
      </button>
      <button
        class="card-action-btn"
        :class="{
          active: isInCompare,
          disabled: compareStore.isFull && !isInCompare,
        }"
        :title="
          isInCompare
            ? 'Убрать из сравнения'
            : compareStore.isFull
              ? 'Список сравнения полон (максимум 4)'
              : 'К сравнению'
        "
        @click.stop="toggleCompare"
      >
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <line x1="18" y1="20" x2="18" y2="10" />
          <line x1="12" y1="20" x2="12" y2="4" />
          <line x1="6" y1="20" x2="6" y2="14" />
        </svg>
      </button>
    </div>

    <div class="product-image-wrapper">
      <img
        v-if="imageUrl"
        :src="imageUrl"
        :alt="props.product.name"
        class="product-image"
        :loading="priority ? 'eager' : 'lazy'"
        :fetchpriority="priority ? 'high' : 'auto'"
        decoding="async"
        @error="handleImageError"
      />
      <div v-else class="product-image-placeholder">
        <svg
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <polyline points="21 15 16 10 5 21" />
        </svg>
      </div>

      <!-- Availability badge -->
      <div v-if="!props.product.is_available" class="badge out-of-stock">
        Нет в наличии
      </div>
    </div>

    <div class="product-info">
      <!-- Name with copy -->
      <div class="product-name-row">
        <h4 class="product-name">{{ props.product.name }}</h4>
        <button
          class="copy-btn"
          title="Копировать название"
          @click.stop="copyText(props.product.name, 'name')"
        >
          <svg
            v-if="copied === 'name'"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
          <svg
            v-else
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
        </button>
      </div>

      <!-- Brand -->
      <p v-if="props.product.brand" class="product-brand">
        {{
          typeof props.product.brand === "object"
            ? props.product.brand.name
            : props.product.brand
        }}
      </p>

      <!-- Tags -->
      <div v-if="firstGroupTags.length > 0" class="product-tags">
        <span v-for="tag in firstGroupTags" :key="tag.id" class="product-tag-chip">{{ tag.name }}</span>
      </div>

      <!-- SKU / Article with copy -->
      <div
        v-if="props.product.manufacturer_sku"
        class="product-sku-row"
        @click.stop
      >
        <span class="product-sku"
          >Арт: {{ props.product.manufacturer_sku }}</span
        >
        <button
          class="copy-btn"
          title="Копировать артикул"
          @click.stop="copyText(String(props.product.manufacturer_sku), 'sku')"
        >
          <svg
            v-if="copied === 'sku'"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
          <svg
            v-else
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
        </button>
      </div>

      <!-- Price -->
      <div class="product-footer">
        <p v-if="props.product.price" class="product-price">
          {{ formatPrice(props.product.price) }}
        </p>
        <p v-else class="product-price text-muted">По запросу</p>

        <div class="product-footer-actions">
          <!-- Если в корзине: inline qty controls -->
          <transition name="cart-qty-fade" mode="out-in">
            <div v-if="inCart" class="card-qty-control" @click.stop key="qty">
              <button
                class="card-qty-btn"
                @click.stop="decCartQty"
                title="Уменьшить"
              >
                −
              </button>
              <span class="card-qty-value">{{ cartQty }}</span>
              <button
                class="card-qty-btn"
                @click.stop="incCartQty"
                title="Увеличить"
              >
                +
              </button>
            </div>
            <!-- Если не в корзине: кнопка добавить -->
            <button
              v-else
              key="add"
              class="btn-cart"
              title="В корзину"
              @click.stop="cartStore.add(props.product, 1)"
            >
              <svg
                width="17"
                height="17"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <circle cx="9" cy="21" r="1" />
                <circle cx="20" cy="21" r="1" />
                <path
                  d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"
                />
              </svg>
            </button>
          </transition>

          <button class="btn-view" @click.stop="goToProduct">
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M9 18l6-6-6-6" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import type { PropType } from "vue";
import type { Product } from "@/types";
import { getImageUrl } from "@/api";
import { useFavoritesStore } from "@/stores/useFavoritesStore";
import { useCompareStore } from "@/stores/useCompareStore";
import { useCartStore } from "@/stores/useCartStore";

const props = defineProps({
  product: {
    type: Object as PropType<Product>,
    required: true,
  },
  priority: {
    type: Boolean,
    default: false,
  },
});

const router = useRouter();
const imageError = ref(false);
const copied = ref<"name" | "sku" | null>(null);

const favStore = useFavoritesStore();
const compareStore = useCompareStore();
const cartStore = useCartStore();

const isFav = computed(() => favStore.isFavorite(props.product.id));

const firstGroupTags = computed(() => {
  const groups = props.product.tag_groups;
  if (!groups || groups.length === 0) return [];
  return groups[0].tags.slice(0, 3);
});
const isInCompare = computed(() =>
  compareStore.items.some((p) => p.id === props.product.id),
);
const inCart = computed(() => cartStore.isInCart(props.product.id));
const cartQty = computed(
  () =>
    cartStore.items.find((i) => i.product.id === props.product.id)?.quantity ??
    0,
);

const toggleFav = () => {
  favStore.toggle(props.product);
};

const toggleCompare = () => {
  if (isInCompare.value) {
    compareStore.remove(props.product.id);
  } else if (!compareStore.isFull) {
    compareStore.add(props.product);
  }
};

const incCartQty = () => {
  cartStore.setQty(props.product.id, cartQty.value + 1);
};

const decCartQty = () => {
  if (cartQty.value <= 1) {
    cartStore.remove(props.product.id);
  } else {
    cartStore.setQty(props.product.id, cartQty.value - 1);
  }
};

const copyText = async (text: string, field: "name" | "sku") => {
  try {
    await navigator.clipboard.writeText(text);
    copied.value = field;
    setTimeout(() => {
      copied.value = null;
    }, 1500);
  } catch {
    // fallback
    const el = document.createElement("textarea");
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand("copy");
    document.body.removeChild(el);
    copied.value = field;
    setTimeout(() => {
      copied.value = null;
    }, 1500);
  }
};

const imageUrl = computed(() => {
  if (imageError.value) return null;

  const mainImage = props.product.main_image;
  if (!mainImage) return null;

  const imgPath = typeof mainImage === "object" ? mainImage.image : mainImage;
  return getImageUrl(imgPath);
});

const handleImageError = () => {
  imageError.value = true;
};

const formatPrice = (price: number) => {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "UZS",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
};

const goToProduct = () => {
  const slug = props.product?.slug;
  if (!slug) return;
  router.push({ name: "ProductDetail", params: { slug } });
};
</script>

<!-- Styles in main.css -->
