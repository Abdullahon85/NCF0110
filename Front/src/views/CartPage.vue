<template>
  <div class="cart-page">
    <div class="container">
      <!-- ── Успешный заказ ── -->
      <div v-if="orderSuccess" class="cart-success">
        <div class="cart-success__icon">
          <svg
            width="64"
            height="64"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
        </div>
        <h2>Заявка принята!</h2>
        <p>
          Мы свяжемся с вами в ближайшее время по указанному номеру телефона.
        </p>
        <p class="cart-success__order-id" v-if="createdOrderId">
          Номер заявки: <strong>#{{ createdOrderId }}</strong>
        </p>
        <router-link to="/catalog" class="btn btn-primary"
          >Продолжить покупки</router-link
        >
      </div>

      <!-- ── Пустая корзина ── -->
      <div v-else-if="cart.items.length === 0" class="cart-empty">
        <div class="cart-empty__icon">
          <svg
            width="80"
            height="80"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1"
          >
            <circle cx="9" cy="21" r="1" />
            <circle cx="20" cy="21" r="1" />
            <path
              d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"
            />
          </svg>
        </div>
        <h2>Корзина пуста</h2>
        <p>Добавьте товары из каталога</p>
        <router-link to="/catalog" class="btn btn-primary"
          >Перейти в каталог</router-link
        >
      </div>

      <!-- ── Корзина с товарами ── -->
      <div v-else class="cart-layout">
        <!-- Левая колонка: список товаров -->
        <div class="cart-items-col">
          <div class="cart-header-row">
            <h1 class="cart-title">Корзина</h1>
            <span class="cart-count"
              >{{ cart.totalQty }} {{ itemWord(cart.totalQty) }}</span
            >
          </div>

          <div class="cart-list">
            <div
              v-for="item in cart.items"
              :key="item.product.id"
              class="cart-item"
            >
              <!-- Изображение -->
              <div
                class="cart-item__img"
                @click="goToProduct(item.product.slug)"
              >
                <img
                  v-if="getImage(item.product)"
                  :src="getImage(item.product)"
                  :alt="item.product.name"
                />
                <div v-else class="cart-item__img-placeholder">
                  <svg
                    width="32"
                    height="32"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  >
                    <rect x="3" y="3" width="18" height="18" rx="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21 15 16 10 5 21" />
                  </svg>
                </div>
              </div>

              <!-- Инфо -->
              <div class="cart-item__info">
                <p
                  class="cart-item__name"
                  @click="goToProduct(item.product.slug)"
                >
                  {{ item.product.name }}
                </p>
                <p v-if="item.product.manufacturer_sku" class="cart-item__sku">
                  Арт: {{ item.product.manufacturer_sku }}
                </p>
                <p class="cart-item__price">
                  <template v-if="item.product.price">{{
                    formatPrice(item.product.price)
                  }}</template>
                  <template v-else
                    ><span class="text-muted">По запросу</span></template
                  >
                </p>
              </div>

              <!-- Количество -->
              <div class="cart-item__qty">
                <button
                  class="qty-btn"
                  @click="decQty(item)"
                  :disabled="item.quantity <= 1"
                >
                  −
                </button>
                <span class="qty-value">{{ item.quantity }}</span>
                <button class="qty-btn" @click="incQty(item)">+</button>
              </div>

              <!-- Итого по позиции -->
              <div class="cart-item__line-total">
                <template v-if="item.product.price">
                  {{
                    formatPrice((item.product.price as number) * item.quantity)
                  }}
                </template>
                <template v-else>—</template>
              </div>

              <!-- Удалить -->
              <button
                class="cart-item__remove"
                @click="cart.remove(item.product.id)"
                title="Удалить"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
          </div>

          <button class="cart-clear-btn" @click="cart.clear()">
            Очистить корзину
          </button>
        </div>

        <!-- Правая колонка: итого + форма -->
        <div class="cart-sidebar">
          <!-- Итого -->
          <div class="cart-summary">
            <h3 class="cart-summary__title">Итого</h3>
            <div class="cart-summary__row">
              <span>Позиций</span>
              <span>{{ cart.items.length }}</span>
            </div>
            <div class="cart-summary__row">
              <span>Количество</span>
              <span>{{ cart.totalQty }}</span>
            </div>
            <div
              v-if="cart.hasPrice"
              class="cart-summary__row cart-summary__total"
            >
              <span>Сумма</span>
              <span>{{ formatPrice(cart.subtotal) }}</span>
            </div>
            <div v-else class="cart-summary__note">
              Часть товаров — по запросу. Менеджер уточнит стоимость.
            </div>

            <button
              v-if="!showForm"
              class="btn btn-primary btn-block"
              @click="showForm = true"
            >
              Оформить заявку
            </button>
          </div>

          <!-- Форма оформления заказа -->
          <transition name="slide-down">
            <div v-if="showForm" class="cart-form">
              <h3 class="cart-form__title">Контактные данные</h3>

              <div v-if="formError" class="cart-form__error">
                {{ formError }}
              </div>

              <form @submit.prevent="submitOrder" novalidate>
                <div class="form-group">
                  <label>Имя <span class="req">*</span></label>
                  <input
                    v-model="form.customer_name"
                    type="text"
                    placeholder="Ваше имя"
                    :class="{ error: v.customer_name }"
                  />
                  <span v-if="v.customer_name" class="field-error">{{
                    v.customer_name
                  }}</span>
                </div>

                <div class="form-group">
                  <label>Телефон <span class="req">*</span></label>
                  <input
                    v-model="form.customer_phone"
                    type="tel"
                    placeholder="+998 __ ___ __ __"
                    :class="{ error: v.customer_phone }"
                  />
                  <span v-if="v.customer_phone" class="field-error">{{
                    v.customer_phone
                  }}</span>
                </div>

                <div class="form-group">
                  <label
                    >Email <span class="optional">(необязательно)</span></label
                  >
                  <input
                    v-model="form.customer_email"
                    type="email"
                    placeholder="email@example.com"
                  />
                </div>

                <div class="form-group">
                  <label>@Telegram <span class="optional">(необязательно)</span></label>
                  <div class="input-with-prefix">
                    <span class="input-prefix">@</span>
                    <input
                      v-model="form.telegram"
                      type="text"
                      placeholder="username"
                      autocomplete="off"
                    />
                  </div>
                </div>

                <div class="form-group">
                  <label
                    >Комментарий
                    <span class="optional">(необязательно)</span></label
                  >
                  <textarea
                    maxlength="1000"
                    v-model="form.comment"
                    rows="3"
                    placeholder="Уточнения по заказу..."
                  ></textarea>
                </div>

                <div class="cart-form__actions">
                  <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="submitting"
                  >
                    <span v-if="submitting">Отправка...</span>
                    <span v-else>Отправить заявку</span>
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline"
                    @click="showForm = false"
                  >
                    Отмена
                  </button>
                </div>
              </form>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { describeSubmitError } from "@/utils/apiError";
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useCartStore } from "@/stores/useCartStore";
import { ordersAPI, getImageUrl } from "@/api";
import type { CartItem } from "@/types";

const cart = useCartStore();
const router = useRouter();

const showForm = ref(false);
const submitting = ref(false);
const orderSuccess = ref(false);
const createdOrderId = ref<number | null>(null);
const formError = ref("");

const form = reactive({
  customer_name: "",
  customer_phone: "",
  customer_email: "",
  telegram: "",
  comment: "",
});

const v = reactive({
  customer_name: "",
  customer_phone: "",
});

const validateForm = () => {
  v.customer_name = "";
  v.customer_phone = "";
  let ok = true;
  if (!form.customer_name.trim()) {
    v.customer_name = "Введите ваше имя";
    ok = false;
  }
  if (!form.customer_phone.trim()) {
    v.customer_phone = "Введите номер телефона";
    ok = false;
  }
  return ok;
};

const submitOrder = async () => {
  if (!validateForm()) return;
  submitting.value = true;
  formError.value = "";

  try {
    const payload = {
      customer_name: form.customer_name.trim(),
      customer_phone: form.customer_phone.trim(),
      customer_email: form.customer_email.trim(),
      customer_telegram: form.telegram.trim() ? (form.telegram.trim().startsWith("@") ? form.telegram.trim() : "@" + form.telegram.trim()) : "",
      comment: form.comment.trim(),
      items: cart.items.map((it: CartItem) => ({
        product: it.product.id,
        product_name: it.product.name,
        product_sku: String(it.product.manufacturer_sku || ""),
        price: it.product.price ?? null,
        quantity: it.quantity,
      })),
    };

    const res = await ordersAPI.create(payload as any);
    createdOrderId.value = res.data.id ?? null;
    cart.clear();
    orderSuccess.value = true;
    showForm.value = false;
  } catch (e: any) {
    formError.value = describeSubmitError(
      e,
      "Произошла ошибка при отправке. Попробуйте ещё раз или позвоните нам.",
    );
  } finally {
    submitting.value = false;
  }
};

const getImage = (product: any): string => {
  const mainImage = product.main_image;
  if (!mainImage) return "";
  const path = typeof mainImage === "object" ? mainImage.image : mainImage;
  return getImageUrl(path);
};

const incQty = (item: CartItem) => {
  cart.setQty(item.product.id, item.quantity + 1);
};

const decQty = (item: CartItem) => {
  if (item.quantity > 1) cart.setQty(item.product.id, item.quantity - 1);
};

const goToProduct = (slug: string) => {
  router.push({ name: "ProductDetail", params: { slug } });
};

const formatPrice = (price: number) =>
  new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "UZS",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);

const itemWord = (n: number) => {
  const m = n % 10;
  if (n >= 11 && n <= 14) return "товаров";
  if (m === 1) return "товар";
  if (m >= 2 && m <= 4) return "товара";
  return "товаров";
};
</script>

<!-- Styles in main.css -->
