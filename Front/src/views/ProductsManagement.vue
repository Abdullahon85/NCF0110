<template>
  <div class="products-management">
    <!-- Заголовок страницы -->
    <div class="page-header">
      <h1>📦 Управление товарами</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        ➕ Добавить товар
      </button>
    </div>

    <!-- Фильтры -->
    <div class="filters-bar">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="🔍 Поиск по названию или SKU..."
        class="search-input"
        @input="debouncedSearch"
      />
      <select
        v-model="selectedCategory"
        @change="applyFilters"
        class="filter-select"
      >
        <option value="">Весь каталог</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">
          {{ cat.name }}
        </option>
      </select>
      <select
        v-model="selectedBrand"
        @change="applyFilters"
        class="filter-select"
      >
        <option value="">Все бренды</option>
        <option v-for="brand in brands" :key="brand.id" :value="brand.id">
          {{ brand.name }}
        </option>
      </select>
      <select
        v-model="availabilityFilter"
        @change="applyFilters"
        class="filter-select"
      >
        <option value="">Все товары</option>
        <option value="true">В наличии</option>
        <option value="false">Нет в наличии</option>
      </select>
      <button @click="resetFilters" class="btn btn-secondary">Сбросить</button>
    </div>

    <!-- Таблица товаров -->
    <div class="table-container">
      <div v-if="loading" class="loading">Загрузка...</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th style="width: 50px">ID</th>
            <th style="width: 70px">Фото</th>
            <th>Название</th>
            <th>SKU</th>
            <th>Каталог</th>
            <th>Бренд</th>
            <th>Цена</th>
            <th>Статус</th>
            <th style="width: 100px">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id">
            <td data-label="ID">{{ product.id }}</td>
            <td data-label="Фото">
              <img
                v-if="product.images && product.images[0]"
                :src="getImageUrl(product.images[0].image) || undefined"
                class="product-thumb"
                alt=""
              />
              <span v-else class="no-image">📷</span>
            </td>
            <td data-label="Название" class="name-cell">{{ product.name }}</td>
            <td data-label="SKU">{{ product.internal_sku || "—" }}</td>
            <td data-label="Каталог">{{ product.category_name || "—" }}</td>
            <td data-label="Бренд">{{ (product.brand as any)?.name || (product as any).brand_name || "—" }}</td>
            <td data-label="Цена">{{ formatPrice(product.price) }}</td>
            <td data-label="Статус">
              <span
                :class="[
                  'badge',
                  product.is_available ? 'badge-success' : 'badge-warning',
                ]"
              >
                {{ product.is_available ? "В наличии" : "Нет" }}
              </span>
            </td>
            <td data-label="Действия">
              <div class="actions">
                <button
                  @click="editProduct(product)"
                  class="btn-icon"
                  title="Редактировать"
                >
                  ✏️
                </button>
                <button
                  @click="confirmDelete(product)"
                  class="btn-icon delete"
                  title="Удалить"
                >
                  🗑️
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="products.length === 0">
            <td colspan="9" class="empty">Товары не найдены</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Пагинация -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        @click="goToPage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="btn btn-secondary"
      >
        ← Назад
      </button>
      <span class="page-info"
        >Страница {{ currentPage }} из {{ totalPages }}</span
      >
      <button
        @click="goToPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="btn btn-secondary"
      >
        Далее →
      </button>
    </div>

    <!-- =============== МОДАЛЬНОЕ ОКНО СОЗДАНИЯ/РЕДАКТИРОВАНИЯ =============== -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal modal-xl">
        <div class="modal-header">
          <h2>
            {{ editingProduct ? "Редактировать товар" : "Добавить товар" }}
          </h2>
          <button @click="closeModal" class="close-btn">✕</button>
        </div>

        <form @submit.prevent="saveProduct" class="modal-body">
          <!-- ========== ОСНОВНАЯ ИНФОРМАЦИЯ ========== -->
          <fieldset class="form-fieldset">
            <legend>Основная информация</legend>

            <div class="form-row">
              <div class="form-group">
                <label>Название *</label>
                <input
                  v-model="form.name"
                  type="text"
                  required
                  @input="generateSlug"
                />
              </div>
              <div class="form-group">
                <label>Slug</label>
                <input
                  v-model="form.slug"
                  type="text"
                  placeholder="auto-generated"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Brand</label>
                <select v-model="form.brand">
                  <option :value="null">---------</option>
                  <option
                    v-for="brand in brands"
                    :key="brand.id"
                    :value="brand.id"
                  >
                    {{ brand.name }}
                  </option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Описание *</label>
              <textarea v-model="form.description" rows="4" required></textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Каталог *</label>
                <select
                  v-model="form.category"
                  required
                  @change="onCategoryChange"
                >
                  <option :value="null" disabled>---------</option>
                  <option
                    v-for="cat in categories"
                    :key="cat.id"
                    :value="cat.id"
                  >
                    {{ cat.name }}
                  </option>
                </select>
              </div>
            </div>
          </fieldset>

          <!-- ========== ЦЕНА И АРТИКУЛЫ ========== -->
          <fieldset class="form-fieldset">
            <legend>Цена и SKU</legend>

            <div class="form-row">
              <div class="form-group">
                <label>Цена</label>
                <input
                  v-model.number="form.price"
                  type="number"
                  step="0.01"
                  min="0"
                />
              </div>
              <div class="form-group checkbox-group">
                <label class="checkbox-label">
                  <input v-model="form.is_available" type="checkbox" />
                  В наличии
                </label>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Артикул производителя</label>
                <input v-model="form.manufacturer_sku" type="text" />
              </div>
              <div class="form-group">
                <label>Внутренний SKU</label>
                <input
                  v-model="form.internal_sku"
                  type="text"
                  placeholder="auto-generated"
                />
              </div>
            </div>
          </fieldset>

          <!-- ========== ИЗОБРАЖЕНИЯ ТОВАРОВ ========== -->
          <fieldset class="form-fieldset">
            <legend>Изображения товаров</legend>

            <div class="images-grid">
              <div
                v-for="(img, idx) in form.images"
                :key="idx"
                class="image-item"
              >
                <div class="image-preview-box">
                  <img
                    v-if="img.preview || img.image"
                    :src="img.preview || getImageUrl(img.image) || undefined"
                    alt="Preview"
                  />
                  <span v-else class="no-preview">📷</span>
                </div>
                <input
                  type="file"
                  accept="image/*"
                  @change="onFileChange($event, idx)"
                />
                <div class="image-controls">
                  <label>
                    <input
                      type="checkbox"
                      :checked="img.is_main"
                      @change="setMainImage(idx)"
                    />
                    Главное
                  </label>
                  <button
                    type="button"
                    @click="removeImage(idx)"
                    class="btn-remove-sm"
                  >
                    ✕
                  </button>
                </div>
              </div>

              <button type="button" @click="addImage" class="add-image-btn">
                ➕ Добавить фото
              </button>
            </div>
          </fieldset>

          <!-- ========== ХАРАКТЕРИСТИКИ ТОВАРОВ ========== -->
          <fieldset class="form-fieldset">
            <legend>Характеристики товаров</legend>

            <div v-if="!form.category" class="hint-message">
              Сначала выберите каталог для отображения характеристик
            </div>

            <div v-else>
              <table class="inline-table">
                <thead>
                  <tr>
                    <th>Характеристика</th>
                    <th>
                      Значения (удерживайте Ctrl для множественного выбора)
                    </th>
                    <th style="width: 80px">Удалить?</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(feat, idx) in form.features" :key="idx">
                    <td data-label="Характеристика">
                      <select
                        v-model="feat.feature_id"
                        @change="onFeatureChange(idx)"
                      >
                        <option :value="null">---------</option>
                        <option
                          v-for="f in categoryFeatures"
                          :key="f.id"
                          :value="f.id"
                        >
                          {{ f.name }}
                        </option>
                      </select>
                    </td>
                    <td data-label="Значения">
                      <select
                        v-model="feat.value_ids"
                        multiple
                        class="multi-select"
                        :disabled="!feat.feature_id"
                      >
                        <option v-if="!feat.feature_id" disabled>
                          Сначала выберите характеристику
                        </option>
                        <option
                          v-for="fv in getValuesForFeature(feat.feature_id)"
                          :key="fv.id"
                          :value="fv.id"
                        >
                          {{ fv.value }}
                        </option>
                      </select>
                    </td>
                    <td data-label="">
                      <button
                        type="button"
                        @click="removeFeature(idx)"
                        class="btn-remove"
                      >
                        Удалить
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <button
                v-if="form.category"
                type="button"
                @click="addFeature"
                class="btn btn-secondary btn-sm"
              >
                ➕ Добавить характеристику
              </button>
            </div>
          </fieldset>

          <!-- ========== ГРУППЫ ТЕГОВ ТОВАРА ========== -->
          <fieldset class="form-fieldset">
            <legend>Группы тегов товара</legend>

            <div v-if="!form.category" class="hint-message">
              Сначала выберите каталог для отображения тегов
            </div>

            <table v-else class="inline-table">
              <thead>
                <tr>
                  <th>Название тега</th>
                  <th>Теги (удерживайте Ctrl для множественного выбора)</th>
                  <th style="width: 80px">Удалить?</th>
                </tr>
              </thead>
              <tbody class="tag-groups-tbody">
                <tr
                  class="tag-group-row"
                  v-for="(tg, idx) in form.tag_groups"
                  :key="idx"
                >
                  <td data-label="Название тега">
                    <select
                      v-model="tg.group_name_id"
                      @change="onTagGroupChange(idx)"
                    >
                      <option :value="null">---------</option>
                      <option
                        v-for="tn in categoryTagNames"
                        :key="tn.id"
                        :value="tn.id"
                      >
                        {{ tn.name }}
                      </option>
                    </select>
                  </td>
                  <td data-label="Теги">
                    <select
                      v-model="tg.tag_ids"
                      multiple
                      class="multi-select"
                      :disabled="!tg.group_name_id"
                    >
                      <option v-if="!tg.group_name_id" disabled>
                        Сначала выберите группу
                      </option>
                      <option
                        v-for="tag in getTagsForGroup(tg.group_name_id)"
                        :key="tag.id"
                        :value="tag.id"
                      >
                        {{ tag.name }}
                      </option>
                    </select>
                  </td>
                  <td data-label="">
                    <button
                      type="button"
                      @click="removeTagGroup(idx)"
                      class="btn-remove"
                    >
                      Удалить
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <button
              v-if="form.category"
              type="button"
              @click="addTagGroup"
              class="btn btn-secondary btn-sm"
            >
              ➕ Добавить группу тегов
            </button>
          </fieldset>

          <!-- ========== ERROR MESSAGE ========== -->
          <div v-if="formError" class="error-msg">{{ formError }}</div>

          <!-- ========== ACTIONS ========== -->
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Отмена
            </button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? "Сохранение..." : "Сохранить" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- =============== МОДАЛЬНОЕ ОКНО ПОДТВЕРЖДЕНИЯ УДАЛЕНИЯ =============== -->
    <div
      v-if="showDeleteModal"
      class="modal-overlay"
      @click.self="showDeleteModal = false"
    >
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Подтверждение удаления</h2>
        </div>
        <div class="modal-body">
          <p>
            Вы уверены, что хотите удалить товар
            <strong>{{ deletingProduct?.name }}</strong
            >?
          </p>
        </div>
        <div class="modal-actions">
          <button @click="showDeleteModal = false" class="btn btn-secondary">
            Отмена
          </button>
          <button
            @click="deleteProduct"
            class="btn btn-danger"
            :disabled="deleting"
          >
            {{ deleting ? "Удаление..." : "Удалить" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import {
  productsAdminAPI,
  categoriesAdminAPI,
  brandsAdminAPI,
  categoryDataAPI,
} from "@/api/admin";
import { getImageUrl } from "@/api";

// ==================== TYPES ====================
interface ProductImage {
  id?: number;
  image: string | null;
  is_main: boolean;
  order: number;
  file?: File;
  preview?: string;
  _new?: boolean;
}

interface ProductFeature {
  id?: number;
  feature_id: number | null;
  feature_name?: string;
  value_ids: number[]; // Изменено с value_id на value_ids для множественного выбора
  value_texts?: string[]; // Массив текстов значений
}

interface ProductTagGroup {
  id?: number;
  group_name_id: number | null;
  group_name_text?: string;
  tag_ids: number[];
}

interface Product {
  id: number;
  name: string;
  slug: string;
  description: string;
  price: number | null;
  category: number;
  category_name: string;
  brand: number | null;
  brand_name: string | null;
  is_available: boolean;
  manufacturer_sku: string;
  internal_sku: string;
  images: ProductImage[];
  features: ProductFeature[];
  tag_groups: ProductTagGroup[];
}

interface Category {
  id: number;
  name: string;
}

interface Brand {
  id: number;
  name: string;
}

// ==================== STATE ====================
const products = ref<Product[]>([]);
const categories = ref<Category[]>([]);
const brands = ref<Brand[]>([]);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = 20;
const totalCount = ref(0);

// Filters
const searchQuery = ref("");
const selectedCategory = ref<number | string>("");
const selectedBrand = ref<number | string>("");
const availabilityFilter = ref("");

// Modal state
const showModal = ref(false);
const editingProduct = ref<Product | null>(null);
const saving = ref(false);
const formError = ref("");

// Delete modal
const showDeleteModal = ref(false);
const deletingProduct = ref<Product | null>(null);
const deleting = ref(false);

// Category-specific data (filtered by category like in Django admin)
const categoryFeatures = ref<any[]>([]);
const categoryFeatureValues = ref<any[]>([]);
const categoryTags = ref<any[]>([]);
const categoryTagNames = ref<any[]>([]);

// Form data
const form = reactive({
  name: "",
  slug: "",
  description: "",
  category: null as number | null,
  brand: null as number | null,
  price: null as number | null,
  is_available: true,
  manufacturer_sku: "",
  internal_sku: "",
  images: [] as ProductImage[],
  features: [] as ProductFeature[],
  tag_groups: [] as ProductTagGroup[],
});

// ==================== COMPUTED ====================
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize));

// ==================== METHODS ====================

// Transliteration for slug
const translitMap: Record<string, string> = {
  а: "a",
  б: "b",
  в: "v",
  г: "g",
  д: "d",
  е: "e",
  ё: "yo",
  ж: "zh",
  з: "z",
  и: "i",
  й: "y",
  к: "k",
  л: "l",
  м: "m",
  н: "n",
  о: "o",
  п: "p",
  р: "r",
  с: "s",
  т: "t",
  у: "u",
  ф: "f",
  х: "h",
  ц: "ts",
  ч: "ch",
  ш: "sh",
  щ: "sch",
  ъ: "",
  ы: "y",
  ь: "",
  э: "e",
  ю: "yu",
  я: "ya",
  " ": "-",
};

function generateSlug() {
  if (editingProduct.value) return; // Don't auto-generate for edit
  form.slug = form.name
    .toLowerCase()
    .split("")
    .map((c) => translitMap[c] || c)
    .join("")
    .replace(/[^a-z0-9-]/g, "")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

function formatPrice(price: number | null) {
  if (!price) return "—";
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "UZS",
    maximumFractionDigits: 0,
  }).format(price);
}

// ==================== DATA LOADING ====================

async function loadProducts() {
  loading.value = true;
  try {
    const params: any = { page: currentPage.value, page_size: pageSize };
    if (searchQuery.value) params.search = searchQuery.value;
    if (selectedCategory.value) params.category = selectedCategory.value;
    if (selectedBrand.value) params.brand = selectedBrand.value;
    if (availabilityFilter.value)
      params.is_available = availabilityFilter.value;

    const response = await productsAdminAPI.getAll(params);
    products.value = response.data.results || response.data;
    totalCount.value = response.data.count || products.value.length;
  } catch (e) {
    console.error("Failed to load products:", e);
  } finally {
    loading.value = false;
  }
}

async function loadCategories() {
  try {
    const response = await categoriesAdminAPI.getAll();
    categories.value = response.data.results || response.data;
  } catch (e) {
    console.error("Failed to load categories:", e);
  }
}

async function loadBrands() {
  try {
    const response = await brandsAdminAPI.getAll();
    brands.value = response.data.results || response.data;
  } catch (e) {
    console.error("Failed to load brands:", e);
  }
}

// Load features/tags by category (like Django filter_features.js)
async function loadCategoryData(categoryId: number) {
  try {
    const response = await categoryDataAPI.getByCategory(categoryId);
    const data = response.data;

    categoryFeatures.value = data.features || [];
    categoryFeatureValues.value = data.feature_values || [];
    categoryTags.value = data.tags || [];
    categoryTagNames.value = data.tag_names || [];
  } catch (e) {
    console.error("Failed to load category data:", e);
    categoryFeatures.value = [];
    categoryFeatureValues.value = [];
    categoryTags.value = [];
    categoryTagNames.value = [];
  }
}

// ==================== FILTERS ====================

let searchTimeout: number;
function debouncedSearch() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    currentPage.value = 1;
    loadProducts();
  }, 400);
}

function applyFilters() {
  currentPage.value = 1;
  loadProducts();
}

function resetFilters() {
  searchQuery.value = "";
  selectedCategory.value = "";
  selectedBrand.value = "";
  availabilityFilter.value = "";
  currentPage.value = 1;
  loadProducts();
}

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  loadProducts();
}

// ==================== FORM MANAGEMENT ====================

function resetForm() {
  form.name = "";
  form.slug = "";
  form.description = "";
  form.category = null;
  form.brand = null;
  form.price = null;
  form.is_available = true;
  form.manufacturer_sku = "";
  form.internal_sku = "";
  form.images = [];
  form.features = [];
  form.tag_groups = [];
  categoryFeatures.value = [];
  categoryFeatureValues.value = [];
  categoryTags.value = [];
  categoryTagNames.value = [];
  formError.value = "";
}

function openCreateModal() {
  editingProduct.value = null;
  resetForm();
  showModal.value = true;
}

async function editProduct(product: Product) {
  editingProduct.value = product;

  // Load full product data with relations
  try {
    const response = await productsAdminAPI.getById(product.id);
    const p = response.data;

    form.name = p.name;
    form.slug = p.slug;
    form.description = p.description || "";
    form.category = p.category;
    form.brand = p.brand;
    form.price = p.price;
    form.is_available = p.is_available;
    form.manufacturer_sku = p.manufacturer_sku || "";
    form.internal_sku = p.internal_sku || "";

    // Images
    form.images = (p.images || []).map((img: any) => ({
      id: img.id,
      image: img.image,
      is_main: img.is_main,
      order: img.order,
    }));

    // Features - преобразуем в новый формат с value_ids
    // Сервер может возвращать массив объектов {feature_id, value_id}
    // Нужно сгруппировать по feature_id
    const featuresMap = new Map<number, number[]>();
    (p.features || []).forEach((f: any) => {
      if (f.feature_id && f.value_id) {
        const existing = featuresMap.get(f.feature_id) || [];
        if (!existing.includes(f.value_id)) {
          existing.push(f.value_id);
        }
        featuresMap.set(f.feature_id, existing);
      }
    });

    form.features = Array.from(featuresMap.entries()).map(
      ([feature_id, value_ids]) => ({
        feature_id,
        value_ids,
      }),
    );

    // Tag groups
    form.tag_groups = (p.tag_groups || []).map((tg: any) => ({
      id: tg.id,
      group_name_id: tg.group_name_id,
      group_name_text: tg.group_name_text,
      tag_ids: tg.tag_ids || [],
    }));

    // Load category-specific data
    if (p.category) {
      await loadCategoryData(p.category);
    }

    formError.value = "";
    showModal.value = true;
  } catch (e) {
    console.error("Failed to load product:", e);
    alert("Ошибка при загрузке товара");
  }
}

function closeModal() {
  showModal.value = false;
  editingProduct.value = null;
  resetForm();
}

// Category change handler - reload features/tags
async function onCategoryChange() {
  // Clear category-specific data
  form.features = [];
  form.tag_groups = [];

  if (form.category) {
    await loadCategoryData(form.category);
  } else {
    categoryFeatures.value = [];
    categoryFeatureValues.value = [];
    categoryTags.value = [];
    categoryTagNames.value = [];
  }
}

// ==================== IMAGES ====================

function addImage() {
  form.images.push({
    image: null,
    preview: undefined,
    is_main: form.images.length === 0,
    order: form.images.length,
    _new: true,
  });
}

function removeImage(idx: number) {
  form.images.splice(idx, 1);
}

function setMainImage(idx: number) {
  form.images.forEach((img, i) => {
    img.is_main = i === idx;
  });
}

function onFileChange(event: Event, idx: number) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (file) {
    // Читаем файл как DataURL для превью
    const reader = new FileReader();
    reader.onload = (e) => {
      form.images[idx].preview = e.target?.result as string;
      form.images[idx].file = file;
      form.images[idx]._new = true;
    };
    reader.readAsDataURL(file);
  }
}

// ==================== FEATURES ====================

function addFeature() {
  form.features.push({
    feature_id: null,
    value_ids: [], // Изменено на массив
  });
}

function removeFeature(idx: number) {
  form.features.splice(idx, 1);
}

// Фильтрация значений по выбранной характеристике
function getValuesForFeature(featureId: number | null) {
  if (!featureId) return [];
  // Find the feature and return its values
  const feature = categoryFeatures.value.find((f: any) => f.id === featureId);
  if (feature && feature.values && Array.isArray(feature.values)) {
    return feature.values;
  }
  return categoryFeatureValues.value.filter(
    (fv: any) => fv.feature_id === featureId,
  );
}

// Обработка изменения характеристики - сбрасываем значения
function onFeatureChange(idx: number) {
  form.features[idx].value_ids = []; // Сброс на пустой массив
}

// ==================== TAG GROUPS ====================

function addTagGroup() {
  form.tag_groups.push({
    group_name_id: null,
    tag_ids: [],
  });
}

function removeTagGroup(idx: number) {
  form.tag_groups.splice(idx, 1);
}

// Получение тегов по выбранной группе (tag_name)
function getTagsForGroup(groupNameId: number | null) {
  if (!groupNameId) return [];
  // Находим группу и возвращаем привязанные к ней теги
  const tagName = categoryTagNames.value.find(
    (tn: any) => tn.id === groupNameId,
  );
  if (tagName && tagName.tags) {
    return tagName.tags;
  }
  // Fallback - фильтруем теги по tag_name
  return categoryTags.value.filter((t: any) => t.tag_name === groupNameId);
}

// Обработка изменения группы тегов - сбрасываем выбранные теги
function onTagGroupChange(idx: number) {
  form.tag_groups[idx].tag_ids = [];
}

// ==================== SAVE PRODUCT ====================

async function saveProduct() {
  try {
    saving.value = true;
    formError.value = "";

    // Prepare data
    const productData: any = {
      name: form.name,
      slug: form.slug || undefined,
      description: form.description,
      category: form.category,
      brand: form.brand,
      price: form.price,
      is_available: form.is_available,
      manufacturer_sku: form.manufacturer_sku,
      internal_sku: form.internal_sku || undefined,
      features: form.features
        .filter((f) => f.feature_id && f.value_ids && f.value_ids.length > 0)
        .flatMap((f) =>
          // Разворачиваем каждое значение в отдельный объект
          f.value_ids.map((value_id) => ({
            feature_id: f.feature_id,
            value_id: value_id,
          })),
        ),
      tag_groups: form.tag_groups
        .filter((tg) => tg.group_name_id)
        .map((tg) => ({
          group_name_id: tg.group_name_id,
          tag_ids: tg.tag_ids,
        })),
      images: form.images
        .filter((img) => img.id) // Only existing images for update
        .map((img) => ({
          id: img.id,
          is_main: img.is_main,
          order: img.order,
        })),
    };

    let productId: number;

    if (editingProduct.value) {
      // Update
      const response = await productsAdminAPI.update(
        editingProduct.value.id,
        productData,
      );
      productId = response.data.id;
    } else {
      // Create
      const response = await productsAdminAPI.create(productData);
      productId = response.data.id;
    }

    // Upload new images
    const newImages = form.images.filter((img) => img._new && img.file);
    for (const img of newImages) {
      if (img.file) {
        const formData = new FormData();
        formData.append("image", img.file);
        try {
          await productsAdminAPI.uploadImage(productId, formData);
        } catch (e) {
          console.warn("Image upload failed:", e);
        }
      }
    }

    closeModal();
    loadProducts();
  } catch (e: any) {
    console.error("Failed to save product:", e);
    formError.value =
      e.response?.data?.detail ||
      JSON.stringify(e.response?.data) ||
      "Ошибка сохранения";
  } finally {
    saving.value = false;
  }
}

// ==================== DELETE PRODUCT ====================

function confirmDelete(product: Product) {
  deletingProduct.value = product;
  showDeleteModal.value = true;
}

async function deleteProduct() {
  if (!deletingProduct.value) return;

  try {
    deleting.value = true;
    await productsAdminAPI.delete(deletingProduct.value.id);
    showDeleteModal.value = false;
    deletingProduct.value = null;
    loadProducts();
  } catch (e) {
    console.error("Failed to delete product:", e);
    alert("Ошибка при удалении товара");
  } finally {
    deleting.value = false;
  }
}

// ==================== LIFECYCLE ====================

onMounted(async () => {
  await Promise.all([loadCategories(), loadBrands()]);
  await loadProducts();
});
</script>

<style scoped>
.images-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-start;
}

.image-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  background: var(--gray-50);
  width: 150px;
}

.image-preview-box {
  width: 100%;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--gray-200);
}

.image-preview-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-preview {
  font-size: 32px;
  color: var(--gray-300);
}

.image-item input[type="file"] {
  font-size: 11px;
  width: 100%;
}

.image-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.image-controls label {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.btn-remove-sm {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background: var(--error);
  color: white;
  cursor: pointer;
  font-size: 12px;
}

.add-image-btn {
  width: 150px;
  height: 150px;
  border: 2px dashed var(--gray-300);
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  color: var(--gray-500);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.add-image-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
  background: var(--primary-color-light, rgba(59, 130, 246, 0.05));
}
</style>
