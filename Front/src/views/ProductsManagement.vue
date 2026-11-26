<template>
  <div class="products-management">
    <!-- Заголовок страницы -->
    <div class="page-header">
      <button class="btn btn-primary" @click="openCreateModal">
        <AdminIcon name="plus" /> Добавить товар
      </button>
    </div>

    <!-- Фильтры -->
    <div class="filters-bar">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Поиск по названию или SKU..."
        class="search-input"
        @input="debouncedSearch"
      />
      <select v-model="selectedCategory" class="filter-select" @change="applyFilters">
        <option value="">Весь каталог</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">
          {{ cat.name }}
        </option>
      </select>
      <select v-model="selectedBrand" class="filter-select" @change="applyFilters">
        <option value="">Все бренды</option>
        <option v-for="brand in brands" :key="brand.id" :value="brand.id">
          {{ brand.name }}
        </option>
      </select>
      <select v-model="availabilityFilter" class="filter-select" @change="applyFilters">
        <option value="">Все товары</option>
        <option value="true">В наличии</option>
        <option value="false">Нет в наличии</option>
      </select>
      <button class="btn btn-secondary" @click="resetFilters">Сбросить</button>
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
            <td data-label="Бренд">
              {{ (product.brand as any)?.name || (product as any).brand_name || "—" }}
            </td>
            <td data-label="Цена">{{ formatPrice(product.price) }}</td>
            <td data-label="Статус">
              <span :class="['badge', product.is_available ? 'badge-success' : 'badge-warning']">
                {{ product.is_available ? "В наличии" : "Нет" }}
              </span>
            </td>
            <td data-label="Действия">
              <div class="actions">
                <button
                  class="btn-icon"
                  title="Редактировать"
                  aria-label="Редактировать"
                  @click="editProduct(product)"
                >
                  <AdminIcon name="edit" />
                </button>
                <button
                  class="btn-icon delete"
                  title="Удалить"
                  aria-label="Удалить"
                  @click="confirmDelete(product)"
                >
                  <AdminIcon name="trash" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="products.length === 0">
            <td colspan="9" class="empty">
              <p class="empty-text">Товары не найдены</p>
              <button class="btn btn-primary" @click="openCreateModal">
                <AdminIcon name="plus" /> Добавить товар
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Пагинация -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        :disabled="currentPage === 1"
        class="btn btn-secondary"
        @click="goToPage(currentPage - 1)"
      >
        ← Назад
      </button>
      <span class="page-info">Страница {{ currentPage }} из {{ totalPages }}</span>
      <button
        :disabled="currentPage === totalPages"
        class="btn btn-secondary"
        @click="goToPage(currentPage + 1)"
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
          <button class="close-btn" aria-label="Закрыть" @click="closeModal">
            <AdminIcon name="close" />
          </button>
        </div>

        <form class="modal-body" @submit.prevent="saveProduct">
          <!-- ========== ОСНОВНАЯ ИНФОРМАЦИЯ ========== -->
          <fieldset class="form-fieldset">
            <legend>Основная информация</legend>

            <div class="form-row">
              <div class="form-group">
                <label>Название *</label>
                <input v-model="form.name" type="text" required @input="generateSlug" />
              </div>
              <div class="form-group">
                <label>Slug</label>
                <input v-model="form.slug" type="text" placeholder="auto-generated" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Бренд</label>
                <select v-model="form.brand">
                  <option :value="null">---------</option>
                  <option v-for="brand in brands" :key="brand.id" :value="brand.id">
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
                <select v-model="form.category" required @change="onCategoryChange">
                  <option :value="null" disabled>---------</option>
                  <option v-for="cat in categories" :key="cat.id" :value="cat.id">
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
                <input v-model.number="form.price" type="number" step="0.01" min="0" />
              </div>
              <div class="form-group">
                <label>Старая цена (зачёркнутая)</label>
                <input v-model.number="form.old_price" type="number" step="0.01" min="0" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group checkbox-group">
                <label class="checkbox-label">
                  <input v-model="form.is_available" type="checkbox" />
                  В наличии (без галочки — «Под заказ»)
                </label>
              </div>
              <div class="form-group">
                <label>Количество, шт</label>
                <input
                  v-model.number="form.stock_quantity"
                  type="number"
                  step="1"
                  min="0"
                  placeholder="не указывать"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Ярлык на карточке</label>
                <select v-model="form.status">
                  <option value="">Нет</option>
                  <option value="new">Новинка</option>
                  <option value="promo">Акция</option>
                  <option value="sale">Распродажа</option>
                </select>
              </div>
              <div class="form-group checkbox-group">
                <label class="checkbox-label">
                  <input v-model="form.is_recommended" type="checkbox" />
                  Рекомендуем (вкладка на главной)
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
                <input v-model="form.internal_sku" type="text" placeholder="auto-generated" />
              </div>
            </div>
          </fieldset>

          <!-- ========== СОПУТСТВУЮЩИЕ ТОВАРЫ ========== -->
          <fieldset class="form-fieldset">
            <legend>Сопутствующие товары</legend>
            <ul v-if="form.related.length" class="related-list">
              <li v-for="item in form.related" :key="item.id">
                <span
                  >{{ item.name }}
                  <small v-if="item.internal_sku">({{ item.internal_sku }})</small></span
                >
                <button
                  type="button"
                  class="btn-remove-sm"
                  aria-label="Убрать"
                  @click="removeRelated(item.id)"
                >
                  <AdminIcon name="close" />
                </button>
              </li>
            </ul>
            <div class="form-group">
              <label>Добавить: поиск по названию или артикулу</label>
              <input v-model="relatedSearch" type="search" @input="searchRelated" />
            </div>
            <ul v-if="relatedResults.length" class="related-results">
              <li v-for="item in relatedResults" :key="item.id">
                <button type="button" class="btn btn-secondary btn-sm" @click="addRelated(item)">
                  <AdminIcon name="plus" /> {{ item.name }}
                </button>
              </li>
            </ul>
          </fieldset>

          <!-- ========== ДОКУМЕНТАЦИЯ ========== -->
          <fieldset class="form-fieldset">
            <legend>Документация (PDF, Word, Excel, ZIP, RAR до 20 МБ)</legend>
            <ul v-if="form.documents.length" class="related-list">
              <li v-for="doc in form.documents" :key="doc.id">
                <a :href="doc.url ?? undefined" target="_blank" rel="noopener">{{ doc.title }}</a>
                <button
                  type="button"
                  class="btn-remove-sm"
                  aria-label="Удалить"
                  @click="removeDocument(doc.id)"
                >
                  <AdminIcon name="close" />
                </button>
              </li>
            </ul>
            <div v-for="(doc, idx) in form.newDocuments" :key="idx" class="form-row">
              <div class="form-group">
                <label>Название</label>
                <input v-model="doc.title" type="text" maxlength="200" placeholder="Паспорт" />
              </div>
              <div class="form-group">
                <label>Файл</label>
                <input
                  type="file"
                  accept=".pdf,.doc,.docx,.xls,.xlsx,.zip,.rar"
                  @change="doc.file = ($event.target as HTMLInputElement).files?.[0] ?? null"
                />
              </div>
            </div>
            <button
              type="button"
              class="btn btn-secondary btn-sm"
              @click="form.newDocuments.push({ title: '', file: null })"
            >
              <AdminIcon name="plus" /> Добавить документ
            </button>
          </fieldset>

          <!-- ========== ИЗОБРАЖЕНИЯ ТОВАРОВ ========== -->
          <fieldset class="form-fieldset">
            <legend>Изображения товаров</legend>

            <div class="images-grid">
              <div v-for="(img, idx) in form.images" :key="idx" class="image-item">
                <div class="image-preview-box">
                  <img
                    v-if="img.preview || img.image"
                    :src="img.preview || getImageUrl(img.image) || undefined"
                    alt="Preview"
                  />
                  <span v-else class="no-preview">📷</span>
                </div>
                <input type="file" accept="image/*" @change="onFileChange($event, idx)" />
                <div class="image-controls">
                  <label>
                    <input type="checkbox" :checked="img.is_main" @change="setMainImage(idx)" />
                    Главное
                  </label>
                  <button
                    type="button"
                    class="btn-remove-sm"
                    aria-label="Удалить"
                    @click="removeImage(idx)"
                  >
                    <AdminIcon name="close" />
                  </button>
                </div>
              </div>

              <button type="button" class="add-image-btn" @click="addImage">
                <AdminIcon name="plus" /> Добавить фото
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
                    <th>Значения (удерживайте Ctrl для множественного выбора)</th>
                    <th style="width: 80px">Удалить?</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(feat, idx) in form.features" :key="idx">
                    <td data-label="Характеристика">
                      <select v-model="feat.feature_id" @change="onFeatureChange(idx)">
                        <option :value="null">---------</option>
                        <option v-for="f in categoryFeatures" :key="f.id" :value="f.id">
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
                      <button type="button" class="btn-remove" @click="removeFeature(idx)">
                        Удалить
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <button
                v-if="form.category"
                type="button"
                class="btn btn-secondary btn-sm"
                @click="addFeature"
              >
                <AdminIcon name="plus" /> Добавить характеристику
              </button>
            </div>
          </fieldset>

          <!-- ========== ERROR MESSAGE ========== -->
          <div v-if="formError" class="error-msg">{{ formError }}</div>

          <!-- ========== ACTIONS ========== -->
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Отмена</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? "Сохранение..." : "Сохранить" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- =============== МОДАЛЬНОЕ ОКНО ПОДТВЕРЖДЕНИЯ УДАЛЕНИЯ =============== -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Подтверждение удаления</h2>
        </div>
        <div class="modal-body">
          <p>
            Вы уверены, что хотите удалить товар
            <strong>{{ deletingProduct?.name }}</strong>?
          </p>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showDeleteModal = false">Отмена</button>
          <button class="btn btn-danger" :disabled="deleting" @click="deleteProduct">
            {{ deleting ? "Удаление..." : "Удалить" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toast } from "@/components/admin/toast";
import AdminIcon from "@/components/admin/AdminIcon.vue";
import { adminErrorMessage } from "@/utils/apiError";
import { uploadEach } from "@/utils/uploads";
import { ref, reactive, computed, onMounted } from "vue";
import { makeSlug } from "@/utils/slug";
import { productsAdminAPI, categoriesAdminAPI, brandsAdminAPI, categoryDataAPI } from "@/api/admin";
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

// Form data
const form = reactive({
  name: "",
  slug: "",
  description: "",
  category: null as number | null,
  brand: null as number | null,
  price: null as number | null,
  old_price: null as number | null,
  stock_quantity: null as number | null,
  status: "" as "" | "new" | "promo" | "sale",
  is_recommended: false,
  related: [] as RelatedProduct[],
  documents: [] as ProductDocument[],
  newDocuments: [] as { title: string; file: File | null }[],
  is_available: true,
  manufacturer_sku: "",
  internal_sku: "",
  images: [] as ProductImage[],
  features: [] as ProductFeature[],
});

// ==================== COMPUTED ====================
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize));

// ==================== METHODS ====================

function generateSlug() {
  if (editingProduct.value) return; // don't touch the slug of an existing product
  form.slug = makeSlug(form.name);
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
    if (availabilityFilter.value) params.is_available = availabilityFilter.value;

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

// Load the features of the category (like Django filter_features.js)
async function loadCategoryData(categoryId: number) {
  try {
    const response = await categoryDataAPI.getByCategory(categoryId);
    const data = response.data;

    categoryFeatures.value = data.features || [];
    categoryFeatureValues.value = data.feature_values || [];
  } catch (e) {
    console.error("Failed to load category data:", e);
    categoryFeatures.value = [];
    categoryFeatureValues.value = [];
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
  form.old_price = null;
  form.stock_quantity = null;
  form.status = "";
  form.is_recommended = false;
  form.related = [];
  form.documents = [];
  form.newDocuments = [];
  removedDocIds.value = [];
  relatedSearch.value = "";
  relatedResults.value = [];
  form.is_available = true;
  form.manufacturer_sku = "";
  form.internal_sku = "";
  form.images = [];
  removedImageIds.value = [];
  form.features = [];
  categoryFeatures.value = [];
  categoryFeatureValues.value = [];
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
    form.old_price = p.old_price == null ? null : Number(p.old_price);
    form.stock_quantity = p.stock_quantity ?? null;
    form.status = p.status || "";
    form.is_recommended = Boolean(p.is_recommended);
    form.related = p.related || [];
    form.documents = p.documents || [];
    form.newDocuments = [];
    removedDocIds.value = [];
    form.is_available = p.is_available;
    form.manufacturer_sku = p.manufacturer_sku || "";
    form.internal_sku = p.internal_sku || "";

    // Images
    removedImageIds.value = [];
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

    form.features = Array.from(featuresMap.entries()).map(([feature_id, value_ids]) => ({
      feature_id,
      value_ids,
    }));

    // Load category-specific data
    if (p.category) {
      await loadCategoryData(p.category);
    }

    formError.value = "";
    showModal.value = true;
  } catch (e) {
    console.error("Failed to load product:", e);
    toast.error(adminErrorMessage(e, "Ошибка при загрузке товара"));
  }
}

function closeModal() {
  showModal.value = false;
  editingProduct.value = null;
  resetForm();
}

// Category change handler - reload features
async function onCategoryChange() {
  // Clear category-specific data
  form.features = [];

  if (form.category) {
    await loadCategoryData(form.category);
  } else {
    categoryFeatures.value = [];
    categoryFeatureValues.value = [];
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

// ==================== RELATED PRODUCTS & DOCUMENTS ====================

interface RelatedProduct {
  id: number;
  name: string;
  internal_sku?: string | null;
}
interface ProductDocument {
  id: number;
  title: string;
  url: string | null;
}

const relatedSearch = ref("");
const relatedResults = ref<RelatedProduct[]>([]);
const removedDocIds = ref<number[]>([]);
let relatedTimer: ReturnType<typeof setTimeout> | null = null;

// Search after a pause in typing; the product itself and already chosen ones are not offered.
function searchRelated() {
  if (relatedTimer) clearTimeout(relatedTimer);
  const q = relatedSearch.value.trim();
  if (q.length < 2) {
    relatedResults.value = [];
    return;
  }
  relatedTimer = setTimeout(async () => {
    try {
      const { data } = await productsAdminAPI.getAll({ search: q, page_size: 10 });
      const taken = new Set([editingProduct.value?.id, ...form.related.map((r) => r.id)]);
      relatedResults.value = (data.results || [])
        .filter((p: RelatedProduct) => !taken.has(p.id))
        .map((p: RelatedProduct) => ({ id: p.id, name: p.name, internal_sku: p.internal_sku }));
    } catch {
      relatedResults.value = [];
    }
  }, 400);
}

function addRelated(item: RelatedProduct) {
  form.related.push(item);
  relatedResults.value = relatedResults.value.filter((r) => r.id !== item.id);
}

function removeRelated(id: number) {
  form.related = form.related.filter((r) => r.id !== id);
}

function removeDocument(id: number) {
  removedDocIds.value.push(id);
  form.documents = form.documents.filter((d) => d.id !== id);
}

// Photos already on the server that the admin removed in the form; they are
// deleted on save (images: [{id, _delete: true}]).
const removedImageIds = ref<number[]>([]);

function removeImage(idx: number) {
  const [img] = form.images.splice(idx, 1);
  if (img?.id) removedImageIds.value.push(img.id);
  // The main photo was removed: the first remaining one becomes main.
  if (img?.is_main && form.images.length && !form.images.some((i) => i.is_main)) {
    form.images[0].is_main = true;
  }
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
      // A new file chosen for a photo that is already on the server replaces it:
      // the old one is deleted on save instead of staying next to the new one.
      const oldId = form.images[idx].id;
      if (oldId) {
        removedImageIds.value.push(oldId);
        form.images[idx].id = undefined;
      }
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
  return categoryFeatureValues.value.filter((fv: any) => fv.feature_id === featureId);
}

// Обработка изменения характеристики - сбрасываем значения
function onFeatureChange(idx: number) {
  form.features[idx].value_ids = []; // Сброс на пустой массив
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
      old_price: form.old_price ?? "",
      stock_quantity:
        form.stock_quantity === null || (form.stock_quantity as unknown) === ""
          ? null
          : form.stock_quantity,
      status: form.status,
      is_recommended: form.is_recommended,
      related_ids: form.related.map((r) => r.id),
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
      images: [
        ...form.images
          .filter((img) => img.id) // Only existing images for update
          .map((img) => ({
            id: img.id,
            is_main: img.is_main,
            order: form.images.indexOf(img),
          })),
        ...removedImageIds.value.map((id) => ({ id, _delete: true })),
      ],
    };

    let productId: number;

    if (editingProduct.value) {
      // Update
      const response = await productsAdminAPI.update(editingProduct.value.id, productData);
      productId = response.data.id;
    } else {
      // Create
      const response = await productsAdminAPI.create(productData);
      productId = response.data.id;
    }

    // Upload new images; a bad file must not be lost silently.
    const newImages = form.images.filter((img) => img._new && img.file);
    const failedUploads = await uploadEach(
      newImages,
      (img) => {
        const formData = new FormData();
        formData.append("image", img.file as File);
        formData.append("is_main", img.is_main ? "true" : "false");
        formData.append("order", String(form.images.indexOf(img)));
        return productsAdminAPI.uploadImage(productId, formData);
      },
      (img) => (img.file as File).name,
    );

    // Documents: removed ones first, then the new files (a bad file is reported, not lost).
    for (const id of removedDocIds.value) {
      await productsAdminAPI.deleteDocument(productId, id);
    }
    const newDocs = form.newDocuments.filter((d) => d.file);
    failedUploads.push(
      ...(await uploadEach(
        newDocs,
        (doc) => {
          const formData = new FormData();
          formData.append("title", doc.title.trim() || (doc.file as File).name);
          formData.append("file", doc.file as File);
          return productsAdminAPI.uploadDocument(productId, formData);
        },
        (doc) => (doc.file as File).name,
      )),
    );

    closeModal();
    loadProducts();
    if (failedUploads.length) {
      toast.error(
        "Товар сохранён, но эти изображения не загрузились:\n" + failedUploads.join("\n"),
      );
    }
  } catch (e: any) {
    console.error("Failed to save product:", e);
    formError.value = adminErrorMessage(e, "Ошибка сохранения");
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
    toast.error(adminErrorMessage(e, "Ошибка при удалении товара"));
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

<style scoped src="@/styles/views/ProductsManagement.css"></style>
