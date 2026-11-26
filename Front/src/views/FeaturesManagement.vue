<template>
  <div class="management-page">
    <div class="page-header">
      <div class="header-actions">
        <button
          :class="['tab-btn', { active: activeTab === 'features' }]"
          @click="activeTab = 'features'"
        >
          Характеристики
        </button>
        <button
          :class="['tab-btn', { active: activeTab === 'values' }]"
          @click="activeTab = 'values'"
        >
          Значения
        </button>
        <button class="btn btn-primary" @click="openCreateModal">
          <AdminIcon name="plus" /> Добавить
        </button>
      </div>
    </div>

    <div class="filters-bar">
      <input
        v-model="search"
        type="text"
        placeholder="Поиск..."
        class="search-input"
        @input="debouncedSearch"
      />
      <select v-model="categoryFilter" class="filter-select" @change="onCategoryFilterChange">
        <option value="">Весь каталог</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">
          {{ cat.name }}
        </option>
      </select>
      <!-- Фильтр по характеристике для вкладки значений -->
      <select
        v-if="activeTab === 'values'"
        v-model="featureFilter"
        class="filter-select"
        @change="onFeatureFilterChange"
      >
        <option value="">Все характеристики</option>
        <option v-for="feat in filteredFeatures" :key="feat.id" :value="feat.id">
          {{ feat.name }}
        </option>
      </select>
    </div>

    <!-- Loading Indicator -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Загрузка...</p>
    </div>

    <!-- Features Table -->
    <div v-if="activeTab === 'features' && !loading" class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Каталог</th>
            <th>Привязанные значения</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in features" :key="item.id">
            <td data-label="ID">{{ item.id }}</td>
            <td data-label="Название" class="name-cell">{{ item.name }}</td>
            <td data-label="Каталог">{{ item.category_name || "—" }}</td>
            <td data-label="Значения">
              <div class="values-preview">
                <span v-if="item.values && item.values.length > 0" class="values-chips">
                  <span v-for="val in item.values.slice(0, 3)" :key="val.id" class="chip">{{
                    val.value
                  }}</span>
                  <span v-if="item.values.length > 3" class="chip chip-more">
                    +{{ item.values.length - 3 }}
                  </span>
                </span>
                <span v-else class="no-values">Нет значений</span>
              </div>
            </td>
            <td data-label="Действия">
              <div class="actions">
                <button
                  class="btn-icon"
                  title="Редактировать"
                  aria-label="Редактировать"
                  @click="editFeature(item)"
                >
                  <AdminIcon name="edit" />
                </button>
                <button
                  class="btn-icon delete"
                  title="Удалить"
                  aria-label="Удалить"
                  @click="confirmDeleteFeature(item)"
                >
                  <AdminIcon name="trash" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="features.length === 0">
            <td colspan="5" class="empty">
              <p class="empty-text">Характеристики не найдены</p>
              <button class="btn btn-primary" @click="openCreateModal">
                <AdminIcon name="plus" /> Добавить
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Пагинация для характеристик -->
    <div v-if="activeTab === 'features' && totalPages > 1" class="pagination">
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

    <!-- Values Table -->
    <div v-if="activeTab === 'values' && !loading" class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Значение</th>
            <th>Характеристика</th>
            <th>Каталог</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in featureValues" :key="item.id">
            <td data-label="ID">{{ item.id }}</td>
            <td data-label="Значение" class="name-cell">{{ item.value }}</td>
            <td data-label="Характеристика">
              <div class="values-preview">
                <span
                  v-if="item.features_info && item.features_info.length > 0"
                  class="values-chips"
                >
                  <span
                    v-for="feat in item.features_info.slice(0, 3)"
                    :key="feat.id"
                    class="chip"
                    >{{ feat.name }}</span
                  >
                  <span v-if="item.features_info.length > 3" class="chip chip-more">
                    +{{ item.features_info.length - 3 }}
                  </span>
                </span>
                <span v-else class="no-values">Не привязано</span>
              </div>
            </td>
            <td data-label="Каталог">{{ item.category_name || "—" }}</td>
            <td data-label="Действия">
              <div class="actions">
                <button class="btn-icon" aria-label="Редактировать" @click="editValue(item)">
                  <AdminIcon name="edit" />
                </button>
                <button
                  class="btn-icon delete"
                  aria-label="Удалить"
                  @click="confirmDeleteValue(item)"
                >
                  <AdminIcon name="trash" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="featureValues.length === 0">
            <td colspan="5" class="empty">Значения не найдены</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Пагинация для значений -->
    <div v-if="activeTab === 'values' && totalPages > 1" class="pagination">
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

    <!-- Feature Modal (с выбором значений) -->
    <div v-if="showFeatureModal" class="modal-overlay" @click.self="showFeatureModal = false">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h2>
            {{ editingFeature ? "Редактировать характеристику" : "Новая характеристика" }}
          </h2>
          <button class="close-btn" aria-label="Закрыть" @click="showFeatureModal = false">
            <AdminIcon name="close" />
          </button>
        </div>
        <form class="modal-body" @submit.prevent="saveFeature">
          <div class="form-row">
            <div class="form-group">
              <label>Название *</label>
              <input v-model="featureForm.name" type="text" required />
            </div>
            <div class="form-group">
              <label>Каталог *</label>
              <select v-model="featureForm.category" required @change="onFeatureCategoryChange">
                <option :value="null" disabled>— Выберите —</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Как характеристика выглядит на сайте: таблица на странице товара и фильтр каталога -->
          <div class="form-row">
            <div class="form-group">
              <label>Группа в таблице</label>
              <input v-model="featureForm.group" type="text" placeholder="Общие" />
            </div>
            <div class="form-group">
              <label>Порядок</label>
              <input v-model.number="featureForm.order" type="number" step="1" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Вид в фильтре каталога</label>
              <select v-model="featureForm.filter_type">
                <option v-for="t in FILTER_TYPES" :key="t.value" :value="t.value">
                  {{ t.label }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Единица</label>
              <input
                v-model="featureForm.unit"
                type="text"
                maxlength="20"
                placeholder="Мп, Вт, шт"
              />
            </div>
          </div>

          <!-- Блок привязки значений -->
          <div v-if="featureForm.category" class="form-group">
            <label>
              Привязанные значения
              <span v-if="featureForm.selectedValues.length > 0" class="count-badge">
                {{ featureForm.selectedValues.length }}
              </span>
            </label>

            <!-- Текущие привязанные значения -->
            <div class="selected-values">
              <div v-if="featureForm.selectedValues.length > 0" class="values-chips-edit">
                <span
                  v-for="val in featureForm.selectedValues"
                  :key="val.id"
                  class="chip chip-removable"
                >
                  {{ val.value }}
                  <button
                    type="button"
                    class="chip-remove"
                    aria-label="Удалить"
                    @click="removeSelectedValue(val)"
                  >
                    <AdminIcon name="close" />
                  </button>
                </span>
              </div>
              <p v-else class="hint-text">Нет привязанных значений</p>
            </div>

            <!-- Выбор из доступных значений каталога -->
            <div class="available-values">
              <div class="values-header">
                <label>Доступные значения для привязки (можно выбрать несколько):</label>
                <button
                  v-if="availableValuesForFeature.length > 0"
                  type="button"
                  class="btn-select-all"
                  @click="selectAllValues"
                >
                  {{ allValuesSelected ? "✓ Все выбраны" : "Выбрать все" }}
                </button>
              </div>
              <div class="values-list">
                <div
                  v-for="val in availableValuesForFeature"
                  :key="val.id"
                  class="value-item"
                  :class="{ selected: isValueSelected(val.id) }"
                  @click="toggleValueSelection(val)"
                >
                  <input
                    type="checkbox"
                    :checked="isValueSelected(val.id)"
                    class="value-checkbox"
                    @click.stop="toggleValueSelection(val)"
                  />
                  <span class="value-name">{{ val.value }}</span>
                  <span class="value-check">{{ isValueSelected(val.id) ? "✓" : "+" }}</span>
                </div>
                <div v-if="availableValuesForFeature.length === 0" class="no-items">
                  Все значения уже привязаны или нет доступных значений
                </div>
              </div>
            </div>

            <!-- Быстрое добавление новых значений -->
            <div class="quick-add-section">
              <label>Быстрое добавление значений (через запятую):</label>
              <div class="quick-add-row">
                <input
                  v-model="newValuesInput"
                  type="text"
                  placeholder="Красный, Синий, Зелёный..."
                  @keydown.enter.prevent="quickAddValues"
                />
                <button
                  type="button"
                  class="btn btn-secondary"
                  :disabled="!newValuesInput.trim()"
                  @click="quickAddValues"
                >
                  <AdminIcon name="plus" /> Добавить
                </button>
              </div>
              <div v-if="quickAddStatus" class="quick-add-status">
                {{ quickAddStatus }}
              </div>
            </div>
          </div>

          <div v-else class="hint-message">Сначала выберите каталог для привязки значений</div>

          <div v-if="error" class="error-msg">{{ error }}</div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showFeatureModal = false">
              Отмена
            </button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? "Сохранение..." : "Сохранить" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Value Modal -->
    <div v-if="showValueModal" class="modal-overlay" @click.self="showValueModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editingValue ? "Редактировать" : "Новое значение" }}</h2>
          <button class="close-btn" aria-label="Закрыть" @click="showValueModal = false">
            <AdminIcon name="close" />
          </button>
        </div>
        <form class="modal-body" @submit.prevent="saveValue">
          <div class="form-group">
            <label>Значение *</label>
            <input v-model="valueForm.value" type="text" required />
          </div>
          <div class="form-group">
            <label>Каталог *</label>
            <select v-model="valueForm.category" required @change="onValueCategoryChange">
              <option :value="null" disabled>— Выберите —</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="info-message">
            💡 Примечание: значения привязываются к характеристикам при редактировании самих
            характеристик
          </div>
          <div v-if="error" class="error-msg">{{ error }}</div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showValueModal = false">
              Отмена
            </button>
            <button type="submit" class="btn btn-primary" :disabled="saving">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal modal-sm">
        <div class="modal-header"><h2>Подтверждение</h2></div>
        <div class="modal-body">
          <p>
            Удалить
            <strong>{{ deletingItem?.name || deletingItem?.value }}</strong>?
          </p>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showDeleteModal = false">Отмена</button>
          <button class="btn btn-danger" :disabled="deleting" @click="performDelete">
            Удалить
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
import { ref, reactive, onMounted, watch, computed } from "vue";
import { featuresAdminAPI, featureValuesAdminAPI, categoriesAdminAPI } from "@/api/admin";

interface FeatureValue {
  id: number;
  value: string;
  feature?: number;
  category?: number;
}

const activeTab = ref<"features" | "values">("features");
const features = ref<any[]>([]);
const featureValues = ref<any[]>([]);
const categories = ref<any[]>([]);
const search = ref("");
const categoryFilter = ref("");
const featureFilter = ref("");
const saving = ref(false);
const error = ref("");
const loading = ref(false);

// Pagination
const currentPage = ref(1);
const pageSize = 20;
const totalCountFeatures = ref(0);
const totalCountValues = ref(0);

// Feature form с выбранными значениями
const showFeatureModal = ref(false);
const editingFeature = ref<any>(null);
// Same values as Feature.FILTER_TYPES on the backend.
const FILTER_TYPES = [
  { value: "list", label: "Список значений с галочками" },
  { value: "bool", label: "Да / Нет" },
  { value: "range", label: "Числовой диапазон" },
  { value: "none", label: "Не показывать в фильтре" },
];

const featureForm = reactive({
  name: "",
  category: null as number | null,
  group: "",
  order: 0,
  filter_type: "list",
  unit: "",
  selectedValues: [] as FeatureValue[],
  originalValueIds: [] as number[], // для отслеживания изменений
});
const newValuesInput = ref("");
const quickAddStatus = ref("");

// Доступные значения для привязки (не привязанные к текущей характеристике)
const allCategoryValues = ref<FeatureValue[]>([]);

const availableValuesForFeature = computed(() => {
  const selectedIds = featureForm.selectedValues.map((v) => v.id);
  return allCategoryValues.value.filter((v) => !selectedIds.includes(v.id));
});

// Проверка, выбраны ли все доступные значения
const allValuesSelected = computed(() => {
  return availableValuesForFeature.value.length === 0 && allCategoryValues.value.length > 0;
});

// Value form
const showValueModal = ref(false);
const editingValue = ref<any>(null);
const valueForm = reactive({
  value: "",
  category: null as number | null,
});

// Delete
const showDeleteModal = ref(false);
const deletingItem = ref<any>(null);
const deleteType = ref<"feature" | "value">("feature");
const deleting = ref(false);

// Отфильтрованные характеристики для фильтра
const filteredFeatures = computed(() => {
  if (!categoryFilter.value) return features.value;
  return features.value.filter((f) => f.category == categoryFilter.value);
});

// Pagination computed
const totalPages = computed(() => {
  const count = activeTab.value === "features" ? totalCountFeatures.value : totalCountValues.value;
  return Math.ceil(count / pageSize);
});

let searchTimeout: number;
function debouncedSearch() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    currentPage.value = 1;
    loadItems();
  }, 300);
}

function onCategoryFilterChange() {
  featureFilter.value = "";
  currentPage.value = 1;
  loadItems();
}

function onFeatureFilterChange() {
  currentPage.value = 1;
  loadItems();
}

async function loadItems() {
  loading.value = true;
  const params: any = {
    page: currentPage.value,
    page_size: pageSize,
  };
  if (search.value) params.search = search.value;
  if (categoryFilter.value) params.category = categoryFilter.value;

  try {
    // Загружаем только данные для активной вкладки
    if (activeTab.value === "features") {
      const featuresRes = await featuresAdminAPI.getAll(params);

      features.value = featuresRes.data.results || featuresRes.data;
      totalCountFeatures.value = featuresRes.data.count || features.value.length;
    } else {
      const valueParams: any = { ...params };
      if (featureFilter.value) valueParams.feature = featureFilter.value;

      const valuesRes = await featureValuesAdminAPI.getAll(valueParams);
      featureValues.value = valuesRes.data.results || valuesRes.data;
      totalCountValues.value = valuesRes.data.count || featureValues.value.length;
    }
  } catch (e) {
    console.error("Error loading items:", e);
  } finally {
    loading.value = false;
  }
}

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  loadItems();
}

async function loadCategories() {
  try {
    const res = await categoriesAdminAPI.getAll();
    categories.value = res.data.results || res.data;
  } catch (e) {
    console.error(e);
  }
}

// Загрузка значений каталога для формы характеристики
async function loadCategoryValues(categoryId: number) {
  try {
    const res = await featureValuesAdminAPI.getAll({
      category: categoryId,
      page_size: 500, // Ограничиваем первоначальную загрузку
    });
    allCategoryValues.value = res.data.results || res.data;
  } catch (e) {
    console.error(e);
    allCategoryValues.value = [];
  }
}

// Загрузка характеристик для формы значений
// ==================== Feature Form ====================

function openCreateModal() {
  error.value = "";
  if (activeTab.value === "features") {
    editingFeature.value = null;
    featureForm.name = "";
    featureForm.category = null;
    featureForm.group = "";
    featureForm.order = 0;
    featureForm.filter_type = "list";
    featureForm.unit = "";
    featureForm.selectedValues.length = 0;
    featureForm.originalValueIds = [];
    allCategoryValues.value = [];
    newValuesInput.value = "";
    showFeatureModal.value = true;
  } else {
    editingValue.value = null;
    valueForm.value = "";
    valueForm.category = null;
    showValueModal.value = true;
  }
}

async function editFeature(item: any) {
  editingFeature.value = item;
  featureForm.name = item.name;
  featureForm.category = item.category;
  featureForm.group = item.group || "";
  featureForm.order = item.order ?? 0;
  featureForm.filter_type = item.filter_type || "list";
  featureForm.unit = item.unit || "";
  newValuesInput.value = "";
  error.value = "";

  // Явно очищаем и заполняем selectedValues
  featureForm.selectedValues.length = 0;
  if (item.values && Array.isArray(item.values)) {
    featureForm.selectedValues.push(...item.values);
    featureForm.originalValueIds = item.values.map((v: any) => v.id);
  } else {
    featureForm.originalValueIds = [];
  }

  if (item.category) {
    await loadCategoryValues(item.category);
  }

  showFeatureModal.value = true;
}

async function onFeatureCategoryChange() {
  featureForm.selectedValues.length = 0;
  featureForm.originalValueIds = [];
  if (featureForm.category) {
    await loadCategoryValues(featureForm.category);
  } else {
    allCategoryValues.value = [];
  }
}

function isValueSelected(valueId: number): boolean {
  return featureForm.selectedValues.some((v) => v.id === valueId);
}

function addSelectedValue(val: FeatureValue) {
  if (!isValueSelected(val.id)) {
    featureForm.selectedValues.push(val);
  }
}

function removeSelectedValue(val: FeatureValue) {
  featureForm.selectedValues = featureForm.selectedValues.filter((v) => v.id !== val.id);
}

// Toggle выбор значения (добавить/удалить)
function toggleValueSelection(val: FeatureValue) {
  if (isValueSelected(val.id)) {
    removeSelectedValue(val);
  } else {
    addSelectedValue(val);
  }
}

// Выбрать все доступные значения или снять выбор
function selectAllValues() {
  if (allValuesSelected.value) {
    // Снять выбор со всех
    featureForm.selectedValues.length = 0;
  } else {
    // Выбрать все доступные
    featureForm.selectedValues.length = 0;
    featureForm.selectedValues.push(...availableValuesForFeature.value);
  }
}

// Быстрое создание новых значений и привязка к характеристике
async function quickAddValues() {
  if (!newValuesInput.value.trim() || !featureForm.category) return;

  const values = newValuesInput.value
    .split(",")
    .map((v) => v.trim())
    .filter((v) => v);
  if (values.length === 0) return;

  let created = 0;
  let linked = 0;
  quickAddStatus.value = "";

  for (const val of values) {
    // Проверяем, существует ли уже такое значение
    const existing = allCategoryValues.value.find(
      (v) => v.value.toLowerCase() === val.toLowerCase(),
    );

    if (existing) {
      // Добавляем существующее если ещё не выбрано
      if (!featureForm.selectedValues.some((v) => v.id === existing.id)) {
        featureForm.selectedValues.push(existing);
        linked++;
      }
    } else {
      try {
        // Создаём значение с привязкой к каталогу (привязка к feature происходит при сохранении характеристики)
        const res = await featureValuesAdminAPI.create({
          value: val,
          category: featureForm.category,
        });

        const newVal = res.data;
        featureForm.selectedValues.push(newVal);
        allCategoryValues.value.push(newVal);
        created++;
      } catch (e: any) {
        console.error(`Failed to create "${val}":`, e);
      }
    }
  }

  newValuesInput.value = "";

  // Show status message
  const messages = [];
  if (created > 0) messages.push(`✅ Создано: ${created}`);
  if (linked > 0) messages.push(`🔗 Привязано: ${linked}`);

  quickAddStatus.value =
    messages.length > 0 ? messages.join(", ") : "Нет новых значений для добавления";

  setTimeout(() => {
    quickAddStatus.value = "";
  }, 3000);
}

async function saveFeature() {
  try {
    saving.value = true;
    error.value = "";

    // Подготовка данных для отправки
    const data = {
      name: featureForm.name,
      category: featureForm.category,
      group: featureForm.group,
      order: featureForm.order || 0,
      filter_type: featureForm.filter_type,
      unit: featureForm.unit,
      value_ids: featureForm.selectedValues.map((v) => v.id),
    };

    if (editingFeature.value) {
      await featuresAdminAPI.update(editingFeature.value.id, data);
    } else {
      await featuresAdminAPI.create(data);
    }

    showFeatureModal.value = false;
    await loadItems();
  } catch (e: any) {
    error.value = adminErrorMessage(e, "Ошибка сохранения");
    console.error("Error saving feature:", error.value);
  } finally {
    saving.value = false;
  }
}

// ==================== Value Form ====================

async function editValue(item: any) {
  editingValue.value = item;
  valueForm.value = item.value;
  valueForm.category = item.category;
  error.value = "";

  showValueModal.value = true;
}

function onValueCategoryChange() {
  // Каталог изменен, можно добавить логику если нужно (например, предупреждение о том, что привязки будут потеряны при сохранении)
}

async function saveValue() {
  try {
    saving.value = true;
    error.value = "";
    if (editingValue.value) {
      await featureValuesAdminAPI.update(editingValue.value.id, valueForm);
    } else {
      await featureValuesAdminAPI.create(valueForm);
    }
    showValueModal.value = false;
    loadItems();
  } catch (e: any) {
    error.value = adminErrorMessage(e, "Ошибка");
  } finally {
    saving.value = false;
  }
}

// ==================== Delete ====================

function confirmDeleteFeature(item: any) {
  deletingItem.value = item;
  deleteType.value = "feature";
  showDeleteModal.value = true;
}

function confirmDeleteValue(item: any) {
  deletingItem.value = item;
  deleteType.value = "value";
  showDeleteModal.value = true;
}

async function performDelete() {
  try {
    deleting.value = true;
    if (deleteType.value === "feature") {
      await featuresAdminAPI.delete(deletingItem.value.id);
    } else {
      await featureValuesAdminAPI.delete(deletingItem.value.id);
    }
    showDeleteModal.value = false;
    loadItems();
  } catch (e) {
    toast.error(adminErrorMessage(e, "Ошибка удаления"));
  } finally {
    deleting.value = false;
  }
}

watch(activeTab, () => {
  featureFilter.value = "";
  currentPage.value = 1;
  loadItems();
});

onMounted(async () => {
  loadItems();
  loadCategories();
});
</script>

<style scoped src="@/styles/views/FeaturesManagement.css"></style>
