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

      <!-- Label and discount, like shop.nag.uz cards -->
      <div v-if="props.product.status_label || price.discount" class="pc-badges">
        <span v-if="price.discount" class="badge pc-discount">{{ price.discount }}</span>
        <span
          v-if="props.product.status_label"
          class="badge pc-status"
          :class="`is-${props.product.status}`"
        >
          {{ props.product.status_label }}
        </span>
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
          typeof props.product.brand === "object" ? props.product.brand.name : props.product.brand
        }}
      </p>

      <!-- SKU / Article with copy -->
      <div v-if="props.product.manufacturer_sku" class="product-sku-row" @click.stop>
        <span class="product-sku">Арт: {{ props.product.manufacturer_sku }}</span>
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

      <!-- Stock, price and the cart button -->
      <div class="product-footer">
        <p class="pc-stock" :class="`is-${stock.tone}`">{{ stock.text }}</p>
        <div class="pc-prices">
          <p class="product-price" :class="{ 'text-muted': props.product.price == null }">
            {{ price.price }}
          </p>
          <s v-if="price.old" class="old-price">{{ price.old }}</s>
        </div>

        <div class="product-footer-actions">
          <transition name="cart-qty-fade" mode="out-in">
            <!-- Already in the cart: change the quantity right on the card -->
            <div v-if="inCart" key="qty" class="card-qty-control" @click.stop>
              <button
                class="card-qty-btn"
                :aria-label="cartQty <= 1 ? 'Убрать из корзины' : 'Уменьшить количество'"
                :title="cartQty <= 1 ? 'Убрать из корзины' : 'Уменьшить количество'"
                @click.stop="decCartQty"
              >
                <svg
                  v-if="cartQty <= 1"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <polyline points="3 6 5 6 21 6" />
                  <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                  <path d="M10 11v6M14 11v6M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
                </svg>
                <span v-else aria-hidden="true">−</span>
              </button>
              <span class="card-qty-value" aria-live="polite">{{ cartQty }} шт</span>
              <button
                class="card-qty-btn"
                aria-label="Увеличить количество"
                title="Увеличить количество"
                @click.stop="incCartQty"
              >
                <span aria-hidden="true">+</span>
              </button>
            </div>
            <button v-else key="add" class="btn-cart" @click.stop="cartStore.add(props.product, 1)">
              <svg
                width="17"
                height="17"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                aria-hidden="true"
              >
                <circle cx="9" cy="21" r="1" />
                <circle cx="20" cy="21" r="1" />
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
              </svg>
              <span>{{ cartText }}</span>
            </button>
          </transition>
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
import { cartButtonText, priceView, stockLabel } from "@/utils/productView";
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

const isInCompare = computed(() => compareStore.items.some((p) => p.id === props.product.id));
const inCart = computed(() => cartStore.isInCart(props.product.id));
const cartQty = computed(
  () => cartStore.items.find((i) => i.product.id === props.product.id)?.quantity ?? 0,
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

const price = computed(() => priceView(props.product));
const stock = computed(() => stockLabel(props.product));
const cartText = computed(() => cartButtonText(props.product));

const goToProduct = () => {
  const slug = props.product?.slug;
  if (!slug) return;
  router.push({ name: "ProductDetail", params: { slug } });
};
</script>

<!-- Styles in styles/site/ -->
