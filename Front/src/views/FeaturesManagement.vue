<template>
  <div class="management-page">
    <div class="page-header">
      <h1>📋 Управление характеристиками</h1>
      <div class="header-actions">
        <button
          @click="activeTab = 'features'"
          :class="['tab-btn', { active: activeTab === 'features' }]"
        >
          Характеристики
        </button>
        <button
          @click="activeTab = 'values'"
          :class="['tab-btn', { active: activeTab === 'values' }]"
        >
          Значения
        </button>
        <button @click="openCreateModal" class="btn btn-primary">
          ➕ Добавить
        </button>
      </div>
    </div>

    <div class="filters-bar">
      <input
        v-model="search"
        type="text"
        placeholder="🔍 Поиск..."
        class="search-input"
        @input="debouncedSearch"
      />
      <select
        v-model="categoryFilter"
        @change="onCategoryFilterChange"
        class="filter-select"
      >
        <option value="">Весь каталог</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">
          {{ cat.name }}
        </option>
      </select>
      <!-- Фильтр по характеристике для вкладки значений -->
      <select
        v-if="activeTab === 'values'"
        v-model="featureFilter"
        @change="onFeatureFilterChange"
        class="filter-select"
      >
        <option value="">Все характеристики</option>
        <option
          v-for="feat in filteredFeatures"
          :key="feat.id"
          :value="feat.id"
        >
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
                <span
                  v-if="item.values && item.values.length > 0"
                  class="values-chips"
                >
                  <span
                    v-for="val in item.values.slice(0, 3)"
                    :key="val.id"
                    class="chip"
                    >{{ val.value }}</span
                  >
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
                  @click="editFeature(item)"
                  class="btn-icon"
                  title="Редактировать"
                >
                  ✏️
                </button>
                <button
                  @click="confirmDeleteFeature(item)"
                  class="btn-icon delete"
                  title="Удалить"
                >
                  🗑️
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="features.length === 0">
            <td colspan="5" class="empty">Характеристики не найдены</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Пагинация для характеристик -->
    <div v-if="activeTab === 'features' && totalPages > 1" class="pagination">
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
                  <span
                    v-if="item.features_info.length > 3"
                    class="chip chip-more"
                  >
                    +{{ item.features_info.length - 3 }}
                  </span>
                </span>
                <span v-else class="no-values">Не привязано</span>
              </div>
            </td>
            <td data-label="Каталог">{{ item.category_name || "—" }}</td>
            <td data-label="Действия">
              <div class="actions">
                <button @click="editValue(item)" class="btn-icon">✏️</button>
                <button
                  @click="confirmDeleteValue(item)"
                  class="btn-icon delete"
                >
                  🗑️
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

    <!-- Feature Modal (с выбором значений) -->
    <div
      v-if="showFeatureModal"
      class="modal-overlay"
      @click.self="showFeatureModal = false"
    >
      <div class="modal modal-lg">
        <div class="modal-header">
          <h2>
            {{
              editingFeature
                ? "Редактировать характеристику"
                : "Новая характеристика"
            }}
          </h2>
          <button @click="showFeatureModal = false" class="close-btn">✕</button>
        </div>
        <form @submit.prevent="saveFeature" class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label>Название *</label>
              <input v-model="featureForm.name" type="text" required />
            </div>
            <div class="form-group">
              <label>Каталог *</label>
              <select
                v-model="featureForm.category"
                @change="onFeatureCategoryChange"
                required
              >
                <option :value="null" disabled>— Выберите —</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Блок привязки значений -->
          <div class="form-group" v-if="featureForm.category">
            <label>
              Привязанные значения
              <span
                v-if="featureForm.selectedValues.length > 0"
                class="count-badge"
              >
                {{ featureForm.selectedValues.length }}
              </span>
            </label>

            <!-- Текущие привязанные значения -->
            <div class="selected-values">
              <div
                v-if="featureForm.selectedValues.length > 0"
                class="values-chips-edit"
              >
                <span
                  v-for="val in featureForm.selectedValues"
                  :key="val.id"
                  class="chip chip-removable"
                >
                  {{ val.value }}
                  <button
                    type="button"
                    @click="removeSelectedValue(val)"
                    class="chip-remove"
                  >
                    ✕
                  </button>
                </span>
              </div>
              <p v-else class="hint-text">Нет привязанных значений</p>
            </div>

            <!-- Выбор из доступных значений каталога -->
            <div class="available-values">
              <div class="values-header">
                <label
                  >Доступные значения для привязки (можно выбрать
                  несколько):</label
                >
                <button
                  v-if="availableValuesForFeature.length > 0"
                  type="button"
                  @click="selectAllValues"
                  class="btn-select-all"
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
                    @click.stop="toggleValueSelection(val)"
                    class="value-checkbox"
                  />
                  <span class="value-name">{{ val.value }}</span>
                  <span class="value-check">{{
                    isValueSelected(val.id) ? "✓" : "+"
                  }}</span>
                </div>
                <div
                  v-if="availableValuesForFeature.length === 0"
                  class="no-items"
                >
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
                  @click="quickAddValues"
                  class="btn btn-secondary"
                  :disabled="!newValuesInput.trim()"
                >
                  ➕ Добавить
                </button>
              </div>
              <div v-if="quickAddStatus" class="quick-add-status">
                {{ quickAddStatus }}
              </div>
            </div>
          </div>

          <div v-else class="hint-message">
            Сначала выберите каталог для привязки значений
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>
          <div class="modal-actions">
            <button
              type="button"
              @click="showFeatureModal = false"
              class="btn btn-secondary"
            >
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
    <div
      v-if="showValueModal"
      class="modal-overlay"
      @click.self="showValueModal = false"
    >
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editingValue ? "Редактировать" : "Новое значение" }}</h2>
          <button @click="showValueModal = false" class="close-btn">✕</button>
        </div>
        <form @submit.prevent="saveValue" class="modal-body">
          <div class="form-group">
            <label>Значение *</label>
            <input v-model="valueForm.value" type="text" required />
          </div>
          <div class="form-group">
            <label>Каталог *</label>
            <select
              v-model="valueForm.category"
              @change="onValueCategoryChange"
              required
            >
              <option :value="null" disabled>— Выберите —</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="info-message">
            💡 Примечание: значения привязываются к характеристикам при
            редактировании самих характеристик
          </div>
          <div v-if="error" class="error-msg">{{ error }}</div>
          <div class="modal-actions">
            <button
              type="button"
              @click="showValueModal = false"
              class="btn btn-secondary"
            >
              Отмена
            </button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              Сохранить
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Modal -->
    <div
      v-if="showDeleteModal"
      class="modal-overlay"
      @click.self="showDeleteModal = false"
    >
      <div class="modal modal-sm">
        <div class="modal-header"><h2>Подтверждение</h2></div>
        <div class="modal-body">
          <p>
            Удалить
            <strong>{{ deletingItem?.name || deletingItem?.value }}</strong
            >?
          </p>
        </div>
        <div class="modal-actions">
          <button @click="showDeleteModal = false" class="btn btn-secondary">
            Отмена
          </button>
          <button
            @click="performDelete"
            class="btn btn-danger"
            :disabled="deleting"
          >
            Удалить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from "vue";
import {
  featuresAdminAPI,
  featureValuesAdminAPI,
  categoriesAdminAPI,
} from "@/api/admin";

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
const featureForm = reactive({
  name: "",
  category: null as number | null,
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
  return (
    availableValuesForFeature.value.length === 0 &&
    allCategoryValues.value.length > 0
  );
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
  const count =
    activeTab.value === "features"
      ? totalCountFeatures.value
      : totalCountValues.value;
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
      totalCountFeatures.value =
        featuresRes.data.count || features.value.length;
    } else {
      const valueParams: any = { ...params };
      if (featureFilter.value) valueParams.feature = featureFilter.value;

      const valuesRes = await featureValuesAdminAPI.getAll(valueParams);
      featureValues.value = valuesRes.data.results || valuesRes.data;
      totalCountValues.value =
        valuesRes.data.count || featureValues.value.length;
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
  featureForm.selectedValues = featureForm.selectedValues.filter(
    (v) => v.id !== val.id,
  );
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
    messages.length > 0
      ? messages.join(", ")
      : "Нет новых значений для добавления";

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
    error.value =
      e.response?.data?.detail ||
      e.response?.data?.name?.[0] ||
      "Ошибка сохранения";
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
    error.value =
      e.response?.data?.detail || e.response?.data?.value?.[0] || "Ошибка";
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
    alert("Ошибка удаления");
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

<style scoped>
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.values-preview {
  display: flex;
  align-items: center;
}

.values-chips,
.values-chips-edit,
.values-chips-select {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  background: var(--surface-color, #e9ecef);
  border-radius: 16px;
  font-size: 12px;
  color: var(--text-color, #333);
}

.chip-more {
  background: var(--primary-color, #007bff);
  color: white;
}

.chip-removable {
  padding-right: 6px;
  gap: 4px;
}

.chip-remove {
  background: none;
  border: none;
  color: var(--danger-color, #dc3545);
  cursor: pointer;
  padding: 0 4px;
  font-size: 12px;
  line-height: 1;
  border-radius: 50%;
}

.chip-remove:hover {
  background: rgba(220, 53, 69, 0.1);
}

.chip-add {
  cursor: pointer;
  border: 1px dashed var(--primary-color, #007bff);
  background: white;
  color: var(--primary-color, #007bff);
  transition: all 0.2s;
}

.chip-add:hover:not(:disabled) {
  background: var(--primary-color, #007bff);
  color: white;
}

.chip-add:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.no-values {
  color: var(--text-muted, #888);
  font-style: italic;
  font-size: 13px;
}

.selected-values {
  margin-bottom: 16px;
  padding: 12px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 2px solid #dee2e6;
  border-radius: 8px;
  min-height: 60px;
  display: flex;
  align-items: center;
}

.selected-values .values-chips-edit {
  width: 100%;
}

.chip-removable {
  display: inline-flex;
  align-items: center;
  padding: 6px 8px 6px 12px;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  gap: 6px;
  transition: all 0.2s ease;
}

.chip-removable:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
}

.chip-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  cursor: pointer;
  padding: 0;
  font-size: 12px;
  line-height: 1;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.chip-remove:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.available-values-section {
  margin-bottom: 16px;
}

.available-values-section label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--text-secondary, #666);
}

.available-values-list {
  padding: 12px;
  background: white;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 8px;
  max-height: 150px;
  overflow-y: auto;
}

/* Улучшенные стили для выбора значений (как у тегов) */
.available-values {
  margin-bottom: 16px;
}

.values-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  gap: 12px;
}

.values-header label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary, #666);
  margin: 0;
}

.btn-select-all {
  padding: 6px 12px;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-select-all:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
}

.btn-select-all:active {
  transform: translateY(0);
}

.values-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;
  padding: 12px;
  background: white;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.value-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  gap: 8px;
}

.value-item:hover {
  background: #e9ecef;
  border-color: var(--primary-color, #007bff);
  transform: translateY(-1px);
}

.value-item.selected {
  background: #d1fae5;
  border-color: #059669;
  color: #065f46;
}

.value-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--primary-color, #007bff);
  flex-shrink: 0;
}

.value-item.selected .value-checkbox {
  accent-color: #059669;
}

.value-name {
  font-size: 13px;
  font-weight: 500;
}

.value-check {
  font-size: 16px;
  font-weight: bold;
  color: var(--primary-color, #007bff);
}

.value-item.selected .value-check {
  color: #059669;
}

.no-items {
  grid-column: 1 / -1;
  text-align: center;
  padding: 20px;
  color: var(--text-muted, #888);
  font-style: italic;
  font-size: 13px;
}

.quick-add-section {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border: 1px dashed #dee2e6;
  border-radius: 8px;
}

.quick-add-section label {
  display: block;
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary, #666);
}

.quick-add-row {
  display: flex;
  gap: 8px;
}

.quick-add-row input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.quick-add-row input:focus {
  outline: none;
  border-color: var(--primary-color, #007bff);
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.quick-add-form {
  display: flex;
  gap: 8px;
}

.quick-add-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 6px;
  font-size: 14px;
}

.hint-text {
  color: var(--text-muted, #888);
  font-size: 13px;
  font-style: italic;
}

.hint-message {
  padding: 16px;
  background: var(--warning-bg, #fff3cd);
  border-radius: 8px;
  color: var(--warning-color, #856404);
  text-align: center;
}

.quick-add-status {
  margin-top: 8px;
  padding: 8px 12px;
  background: #d1fae5;
  color: #065f46;
  border-radius: 6px;
  font-size: 13px;
}

.badge-primary {
  background-color: var(--primary-color, #007bff);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 8px;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  margin-left: 8px;
}

.badge-warning {
  background-color: var(--warning-color, #ffc107);
  color: #212529;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.modal-lg {
  max-width: 700px;
}

.info-message {
  padding: 12px 16px;
  background: linear-gradient(135deg, #e7f3ff 0%, #d0e7ff 100%);
  border-left: 4px solid var(--primary-color, #007bff);
  border-radius: 6px;
  color: var(--text-color, #333);
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 16px;
}
</style>
