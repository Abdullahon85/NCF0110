<!-- src/views/AllBrand.vue -->
<template>
  <div class="all-brands" v-if="$route.name == 'All-Brand'">
    <div class="container">
      <!-- Mobile Filter Button -->
      <button class="mobile-filter-btn" @click="showFilters = true">
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <line x1="4" y1="6" x2="20" y2="6" />
          <line x1="4" y1="12" x2="20" y2="12" />
          <line x1="4" y1="18" x2="20" y2="18" />
        </svg>
        Фильтры
      </button>

      <!-- Overlay -->
      <transition name="fade">
        <div
          v-if="showFilters"
          class="filters-overlay show"
          @click="showFilters = false"
        ></div>
      </transition>

      <div class="page-layout">
        <!-- Фильтры -->
        <aside class="filters-column" :class="{ 'show-mobile': showFilters }">
          <div class="panel">
            <button class="mobile-filter-close" @click="showFilters = false">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
            <h3>Фильтры</h3>

            <!-- Поиск по брендам -->
            <div class="search-bar">
              <input
                type="text"
                v-model="filters.search"
                @keyup.enter="applyFilters"
                placeholder="Поиск брендов..."
              />
              <button @click="applyFilters" class="btn-search">
                <svg
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  viewBox="0 0 24 24"
                >
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
              </button>
            </div>

            <!-- Фильтр по категориям -->
            <div class="filter-group" v-if="categories.length > 0">
              <label>Категории</label>
              <div class="categories-list">
                <label
                  v-for="category in categories"
                  :key="category.slug"
                  class="category-item"
                >
                  <input
                    type="checkbox"
                    :value="category.slug"
                    v-model="filters.categories"
                    @change="applyFilters"
                  />
                  <span>{{ category.name }}</span>
                </label>
              </div>
            </div>

            <!-- Фильтр цены продуктов -->
            <div class="filter-group">
              <label>Диапазон цен</label>
              <div class="price-range">
                <input
                  type="number"
                  v-model.number="filters.priceMin"
                  placeholder="От"
                  @change="applyFilters"
                />
                <span>—</span>
                <input
                  type="number"
                  v-model.number="filters.priceMax"
                  placeholder="До"
                  @change="applyFilters"
                />
              </div>
            </div>

            <!-- Фильтр по наличию товаров -->
            <div class="filter-group">
              <label class="has-products-label">
                <input
                  type="checkbox"
                  v-model="filters.hasProducts"
                  @change="applyFilters"
                />
                <span>Только с товарами</span>
              </label>
            </div>

            <!-- Фильтр по наличию доступных товаров -->
            <div class="filter-group">
              <label class="has-available-label">
                <input
                  type="checkbox"
                  v-model="filters.hasAvailable"
                  @change="applyFilters"
                />
                <span>Только с товарами в наличии</span>
              </label>
            </div>

            <!-- Действия с фильтрами -->
            <div class="filter-actions">
              <button @click="resetFilters" class="btn muted">Сбросить</button>
              <button @click="showFilters = false" class="btn primary">
                Применить
              </button>
            </div>
          </div>
        </aside>

        <!-- Основной контент -->
        <main class="brands-column">
          <div class="topbar">
            <h1>Все бренды</h1>
            <!-- Сортировка -->
            <div class="sort">
              <label>Сортировать:</label>
              <select v-model="filters.ordering" @change="applyFilters">
                <option value="name">По названию (А-Я)</option>
                <option value="-name">По названию (Я-А)</option>
                <option value="-products_count">
                  По количеству товаров (убыв.)
                </option>
                <option value="products_count">
                  По количеству товаров (возр.)
                </option>
              </select>
            </div>
          </div>

          <!-- Состояния загрузки и ошибки -->
          <div v-if="loading" class="loading">
            <div class="spinner"></div>
            <p>Загрузка брендов...</p>
          </div>
          <div v-else-if="error" class="error-state">
            <p>{{ error }}</p>
            <button @click="loadBrands" class="btn primary">Повторить</button>
          </div>
          <div v-else-if="brands.length === 0" class="empty-state">
            <p>Бренды не найдены</p>
            <button @click="resetFilters" class="btn muted">
              Сбросить фильтры
            </button>
          </div>

          <!-- Сетка брендов -->
          <div v-else class="brands-grid">
            <div v-for="brand in brands" :key="brand.id" class="brand-card">
              <router-link :to="`/brands/${brand.slug}`">
                <img
                  v-if="brand.image"
                  :src="getImageUrl(brand.image)"
                  :alt="brand.name"
                />
                <h3>{{ brand.name }}</h3>
                <p class="products-count" v-if="brand.products_count">
                  {{ brand.products_count }} товар{{
                    getProductsCountSuffix(brand.products_count)
                  }}
                </p>
              </router-link>
            </div>
          </div>

          <!-- Пагинация -->
          <Pagination
            v-if="pagination.totalPages > 1"
            :current-page="pagination.page"
            :total-pages="pagination.totalPages"
            @change="changePage"
          />
        </main>
      </div>
    </div>
  </div>
  <div class="clients-slider" v-else-if="$route.name == 'Home'" ref="sliderRef">
    <div class="clients-viewport">
      <div
        class="clients-track"
        :style="{ transform: `translateX(${position}px)` }"
        :class="{ 'no-transition': isDragging }"
        @mousedown="startDrag"
        @mousemove="onDrag"
        @mouseup="endDrag"
        @mouseleave="endDrag"
        @touchstart="startDrag"
        @touchmove="onDrag"
        @touchend="endDrag"
      >
        <div
          v-for="brand in clonedBrands"
          :key="brand.id + '-' + brand.clone"
          class="client-logo"
          :class="{ 'logo-clone': brand.clone }"
        >
          <router-link :to="`/brands/${brand.slug}`" @click="handleLogoClick">
            <template v-if="brand.image">
              <img
                :src="getImageUrl(brand.image)"
                :alt="brand.name"
                loading="lazy"
                draggable="false"
              />
            </template>
            <template v-else>
              <div class="brand-placeholder">
                {{ brand.name ? brand.name.charAt(0).toUpperCase() : "?" }}
              </div>
            </template>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, reactive } from "vue";
import { brandsAPI, categoriesAPI, getImageUrl } from "@/api";
import type { Brand, Category, BrandFilters } from "@/types";
import Pagination from "@/components/Pagination.vue";

const brands = ref<Brand[]>([]);
const categories = ref<Category[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
const showFilters = ref(false);

const pagination = reactive({
  page: 1,
  pageSize: 12,
  totalPages: 1,
  total: 0,
});

const filters = reactive({
  search: "",
  categories: [] as string[],
  hasProducts: false,
  hasAvailable: false,
  priceMin: null as number | null,
  priceMax: null as number | null,
  ordering: "name",
});

const loadBrands = async () => {
  loading.value = true;
  error.value = null;

  try {
    const params: BrandFilters = {
      page: pagination.page,
      page_size: pagination.pageSize,
      search: filters.search,
      category: filters.categories.join(","),
      // only send these flags when true — sending 'false' string caused backend to treat as present
      has_products: filters.hasProducts ? true : undefined,
      has_available: filters.hasAvailable ? true : undefined,
      price_min: filters.priceMin ?? undefined,
      price_max: filters.priceMax ?? undefined,
      ordering: filters.ordering,
    };

    const response = await brandsAPI.getAll(params);
    brands.value = response.data.results;
    pagination.total = response.data.count;
    pagination.totalPages = Math.ceil(pagination.total / pagination.pageSize);
  } catch (err) {
    error.value = "Ошибка загрузки брендов";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const loadCategories = async () => {
  try {
    const response = await categoriesAPI.getAll();
    categories.value = response.data.results;
  } catch (err) {
    console.error("Ошибка загрузки категорий:", err);
  }
};

const applyFilters = () => {
  pagination.page = 1;
  loadBrands();
};

const resetFilters = () => {
  filters.search = "";
  filters.categories = [];
  filters.hasProducts = false;
  filters.hasAvailable = false;
  filters.priceMin = null;
  filters.priceMax = null;
  filters.ordering = "name";
  applyFilters();
};

const changePage = (page: number) => {
  pagination.page = page;
  loadBrands();
};

const getProductsCountSuffix = (count: number): string => {
  const cases = [2, 0, 1, 1, 1, 2];
  const titles = ["", "а", "ов"];
  return titles[
    count % 100 > 4 && count % 100 < 20
      ? 2
      : cases[count % 10 < 5 ? count % 10 : 5]
  ];
};

onMounted(async () => {
  await Promise.all([loadBrands(), loadCategories()]);
});

// Слайдер брендов для главной страницы
const sliderRef = ref<HTMLElement | null>(null);
const isDragging = ref(false);
const position = ref(0);
const startX = ref(0);
const dragStartPosition = ref(0);
const itemWidth = ref(0);
const dragThreshold = 5;
let dragDistance = 0;
let animationFrame: number | null = null;
let autoplayTimeout: number | null = null;

// Создаем клонированные бренды для бесконечной прокрутки
const clonedBrands = computed(() => {
  const brandsWithClone = brands.value.map((brand) => ({
    ...brand,
    clone: false,
  }));
  const clones = brands.value.map((brand) => ({ ...brand, clone: true }));
  return [...brandsWithClone, ...clones];
});

function getClientX(event: MouseEvent | TouchEvent): number {
  if ("touches" in event) {
    return event.touches[0].clientX;
  }
  return event.clientX;
}

function startDrag(event: MouseEvent | TouchEvent) {
  stopAutoplay();
  isDragging.value = true;
  startX.value = getClientX(event);
  dragStartPosition.value = position.value;
  dragDistance = 0;
  event.preventDefault();

  // Остановить текущую анимацию
  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
    animationFrame = null;
  }
}

function onDrag(event: MouseEvent | TouchEvent) {
  if (!isDragging.value) return;

  const currentX = getClientX(event);
  const delta = currentX - startX.value;
  dragDistance = Math.abs(delta);

  // Плавное перемещение
  position.value = dragStartPosition.value + delta;
  event.preventDefault();
}

function endDrag() {
  if (!isDragging.value) return;

  isDragging.value = false;

  // Определяем ближайшую позицию для snap эффекта
  const itemCount = brands.value.length;
  const totalWidth = itemWidth.value * itemCount;
  const currentPosition = position.value;

  let targetPosition =
    Math.round(currentPosition / itemWidth.value) * itemWidth.value;

  // Если перетащили за пределы, возвращаемся к началу/концу
  if (targetPosition > 0) {
    targetPosition = -totalWidth + itemWidth.value;
  } else if (targetPosition < -totalWidth) {
    targetPosition = 0;
  }

  // Плавная анимация к целевой позиции
  animateToPosition(targetPosition);
  startAutoplay();
}

function handleLogoClick(event: MouseEvent) {
  if (dragDistance > dragThreshold) {
    event.preventDefault();
    event.stopPropagation();
  }
}

function animateToPosition(target: number) {
  const start = position.value;
  const distance = target - start;
  const duration = 500;
  const startTime = performance.now();

  function animate(currentTime: number) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Функция плавности (easeOutCubic)
    const eased = 1 - Math.pow(1 - progress, 3);

    position.value = start + distance * eased;

    if (progress < 1) {
      animationFrame = requestAnimationFrame(animate);
    } else {
      animationFrame = null;
      // Проверяем, нужно ли перепрыгнуть в начало
      checkAndResetPosition();
    }
  }

  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
  }
  animationFrame = requestAnimationFrame(animate);
}

function checkAndResetPosition() {
  const itemCount = brands.value.length;
  const totalWidth = itemWidth.value * itemCount;

  // Если достигли конца клонированных элементов, мгновенно перепрыгиваем в начало
  if (position.value <= -totalWidth) {
    position.value = 0;
  }
}

function startAutoplay() {
  if (autoplayTimeout) return;

  function autoplay() {
    const nextPosition = position.value - itemWidth.value;

    animateToPosition(nextPosition);
    autoplayTimeout = window.setTimeout(autoplay, 1000);
  }

  autoplayTimeout = window.setTimeout(autoplay, 1000);
}

function stopAutoplay() {
  if (autoplayTimeout) {
    clearTimeout(autoplayTimeout);
    autoplayTimeout = null;
  }
}

// Инициализация и очистка
onMounted(() => {
  // Получаем ширину элемента для правильного позиционирования
  if (sliderRef.value) {
    const logoElement = sliderRef.value.querySelector(".client-logo");
    if (logoElement) {
      const styles = window.getComputedStyle(logoElement);
      const width = logoElement.clientWidth;
      const marginRight = parseInt(styles.marginRight || "0");
      itemWidth.value = width + marginRight;
    }
  }

  // Запускаем автопрокрутку
  startAutoplay();

  // Обновляем размеры при изменении окна
  window.addEventListener("resize", () => {
    if (sliderRef.value) {
      const logoElement = sliderRef.value.querySelector(".client-logo");
      if (logoElement) {
        const styles = window.getComputedStyle(logoElement);
        const width = logoElement.clientWidth;
        const marginRight = parseInt(styles.marginRight || "0");
        itemWidth.value = width + marginRight;
      }
    }
  });
});

onUnmounted(() => {
  stopAutoplay();
  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
  }
});
</script>

<!-- Styles in main.css -->
