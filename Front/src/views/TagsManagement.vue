<template>
  <div class="management-page">
    <div class="page-header">
      <h1>#️⃣ Управление тегами</h1>
      <div class="header-actions">
        <button
          @click="activeTab = 'tagNames'"
          :class="['tab-btn', { active: activeTab === 'tagNames' }]"
        >
          Группы тегов
        </button>
        <button
          @click="activeTab = 'tags'"
          :class="['tab-btn', { active: activeTab === 'tags' }]"
        >
          Все теги
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
        @change="loadItems"
        class="filter-select"
      >
        <option value="">Весь каталог</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">
          {{ cat.name }}
        </option>
      </select>
    </div>

    <!-- Tag Names (Groups) Table -->
    <div v-if="activeTab === 'tagNames'" class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Название группы</th>
            <th>Каталог</th>
            <th>Теги</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in tagNames" :key="item.id">
            <td data-label="ID">{{ item.id }}</td>
            <td data-label="Группа" class="name-cell">{{ item.name }}</td>
            <td data-label="Каталог">{{ item.category_name || "—" }}</td>
            <td data-label="Теги">
              <span class="tags-count">{{ item.tags_count || 0 }} тегов</span>
              <div v-if="item.tags && item.tags.length" class="tags-preview">
                <span
                  v-for="tag in item.tags.slice(0, 3)"
                  :key="tag.id"
                  class="tag-chip small"
                >
                  {{ tag.name }}
                </span>
                <span v-if="item.tags.length > 3" class="more-tags"
                  >+{{ item.tags.length - 3 }}</span
                >
              </div>
            </td>
            <td data-label="Действия">
              <div class="actions">
                <button @click="editTagName(item)" class="btn-icon">✏️</button>
                <button
                  @click="confirmDeleteTagName(item)"
                  class="btn-icon delete"
                >
                  🗑️
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="tagNames.length === 0">
            <td colspan="5" class="empty">Группы тегов не найдены</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- All Tags Table -->
    <div v-if="activeTab === 'tags'" class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Slug</th>
            <th>Группа</th>
            <th>Каталог</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in tags" :key="item.id">
            <td data-label="ID">{{ item.id }}</td>
            <td data-label="Название" class="name-cell">{{ item.name }}</td>
            <td data-label="Slug" class="slug-cell">{{ item.slug }}</td>
            <td data-label="Группа">{{ item.tag_name_display || "—" }}</td>
            <td data-label="Каталог">{{ item.category_name || "—" }}</td>
            <td data-label="Действия">
              <div class="actions">
                <button @click="editTag(item)" class="btn-icon">✏️</button>
                <button @click="confirmDeleteTag(item)" class="btn-icon delete">
                  🗑️
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="tags.length === 0">
            <td colspan="6" class="empty">Теги не найдены</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- TagName (Group) Modal with Tag Selection -->
    <div
      v-if="showTagNameModal"
      class="modal-overlay"
      @click.self="showTagNameModal = false"
    >
      <div class="modal modal-lg">
        <div class="modal-header">
          <h2>
            {{ editingTagName ? "Редактировать группу" : "Новая группа тегов" }}
          </h2>
          <button @click="showTagNameModal = false" class="close-btn">✕</button>
        </div>
        <form @submit.prevent="saveTagName" class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label>Название группы *</label>
              <input v-model="tagNameForm.name" type="text" required />
            </div>
            <div class="form-group">
              <label>Каталог</label>
              <select v-model="tagNameForm.category">
                <option :value="null">— Не выбрано —</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Tags Selection Section -->
          <div class="form-group" v-if="editingTagName">
            <label>Привязанные теги</label>

            <!-- Selected Tags Display -->
            <div class="selected-values">
              <span
                v-for="tag in selectedTags"
                :key="tag.id"
                class="value-chip"
              >
                {{ tag.name }}
                <button
                  type="button"
                  @click="removeSelectedTag(tag)"
                  class="chip-remove"
                >
                  ✕
                </button>
              </span>
              <span v-if="selectedTags.length === 0" class="no-values">
                Нет привязанных тегов
              </span>
            </div>

            <!-- Quick Add Tags -->
            <div class="quick-add-section">
              <label>Быстрое добавление тегов (через запятую):</label>
              <div class="quick-add-row">
                <input
                  v-model="quickAddInput"
                  type="text"
                  placeholder="тег1, тег2, тег3"
                  @keydown.enter.prevent="quickAddTags"
                />
                <button
                  type="button"
                  @click="quickAddTags"
                  class="btn btn-secondary"
                >
                  ➕ Добавить
                </button>
              </div>
              <div v-if="quickAddStatus" class="quick-add-status">
                {{ quickAddStatus }}
              </div>
            </div>

            <!-- Available Tags to Select -->
            <div class="available-values">
              <label>Доступные теги для привязки:</label>
              <div class="values-list">
                <div
                  v-for="tag in availableTags"
                  :key="tag.id"
                  class="value-item"
                  :class="{ selected: isTagSelected(tag.id) }"
                  @click="toggleTagSelection(tag)"
                >
                  <span class="value-name">{{ tag.name }}</span>
                  <span class="value-check">{{
                    isTagSelected(tag.id) ? "✓" : "+"
                  }}</span>
                </div>
                <div v-if="availableTags.length === 0" class="no-items">
                  Все теги уже привязаны или нет доступных тегов
                </div>
              </div>
            </div>
          </div>

          <div v-else class="info-msg">
            💡 Сначала создайте группу, затем сможете привязать к ней теги
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>
          <div class="modal-actions">
            <button
              type="button"
              @click="showTagNameModal = false"
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

    <!-- Tag Modal (for individual tag editing) -->
    <div
      v-if="showTagModal"
      class="modal-overlay"
      @click.self="showTagModal = false"
    >
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editingTag ? "Редактировать тег" : "Новый тег" }}</h2>
          <button @click="showTagModal = false" class="close-btn">✕</button>
        </div>
        <form @submit.prevent="saveTag" class="modal-body">
          <div class="form-group">
            <label>Название *</label>
            <input
              v-model="tagForm.name"
              type="text"
              required
              @input="generateTagSlug"
            />
          </div>
          <div class="form-group">
            <label>Slug *</label>
            <input v-model="tagForm.slug" type="text" required />
          </div>
          <div class="form-group">
            <label>Группа тегов</label>
            <select v-model="tagForm.tag_name">
              <option :value="null">— Не выбрано —</option>
              <option v-for="tn in tagNames" :key="tn.id" :value="tn.id">
                {{ tn.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Каталог</label>
            <select v-model="tagForm.category">
              <option :value="null">— Не выбрано —</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div v-if="error" class="error-msg">{{ error }}</div>
          <div class="modal-actions">
            <button
              type="button"
              @click="showTagModal = false"
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
            Удалить <strong>{{ deletingItem?.name }}</strong
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
  tagsAdminAPI,
  tagNamesAdminAPI,
  categoriesAdminAPI,
} from "@/api/admin";

const activeTab = ref<"tags" | "tagNames">("tagNames");
const tags = ref<any[]>([]);
const tagNames = ref<any[]>([]);
const categories = ref<any[]>([]);
const search = ref("");
const categoryFilter = ref("");
const saving = ref(false);
const error = ref("");

// Tag modal
const showTagModal = ref(false);
const editingTag = ref<any>(null);
const tagForm = reactive({
  name: "",
  slug: "",
  category: null as number | null,
  tag_name: null as number | null,
});

// TagName modal
const showTagNameModal = ref(false);
const editingTagName = ref<any>(null);
const tagNameForm = reactive({ name: "", category: null as number | null });

// Tag selection for TagName
const selectedTags = ref<any[]>([]);
const allTags = ref<any[]>([]);
const quickAddInput = ref("");
const quickAddStatus = ref("");

// Delete
const showDeleteModal = ref(false);
const deletingItem = ref<any>(null);
const deleteType = ref<"tag" | "tagName">("tag");
const deleting = ref(false);

// Computed: available tags (not yet selected)
const availableTags = computed(() => {
  const selectedIds = new Set(selectedTags.value.map((t) => t.id));
  return allTags.value.filter((t) => !selectedIds.has(t.id));
});

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

function generateSlug(text: string): string {
  return text
    .toLowerCase()
    .split("")
    .map((c) => translitMap[c] || c)
    .join("")
    .replace(/[^a-z0-9-]/g, "")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

function generateTagSlug() {
  if (editingTag.value) return;
  tagForm.slug = generateSlug(tagForm.name);
}

let searchTimeout: number;
function debouncedSearch() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(loadItems, 300);
}

async function loadItems() {
  const params: any = {};
  if (search.value) params.search = search.value;
  if (categoryFilter.value) params.category = categoryFilter.value;

  try {
    const [tagsRes, tagNamesRes] = await Promise.all([
      tagsAdminAPI.getAll(params),
      tagNamesAdminAPI.getAll(params),
    ]);
    tags.value = tagsRes.data.results || tagsRes.data;
    tagNames.value = tagNamesRes.data.results || tagNamesRes.data;
  } catch (e) {
    console.error(e);
  }
}

async function loadAllTags() {
  try {
    const res = await tagsAdminAPI.getAll();
    allTags.value = res.data.results || res.data;
  } catch (e) {
    console.error(e);
  }
}

async function loadCategories() {
  try {
    const res = await categoriesAdminAPI.getAll();
    categories.value = res.data.results || res.data;
  } catch (e) {
    console.error(e);
  }
}

function openCreateModal() {
  error.value = "";
  if (activeTab.value === "tags") {
    editingTag.value = null;
    tagForm.name = "";
    tagForm.slug = "";
    tagForm.category = null;
    tagForm.tag_name = null;
    showTagModal.value = true;
  } else {
    editingTagName.value = null;
    tagNameForm.name = "";
    tagNameForm.category = null;
    selectedTags.value = [];
    showTagNameModal.value = true;
  }
}

function editTag(item: any) {
  editingTag.value = item;
  tagForm.name = item.name;
  tagForm.slug = item.slug;
  tagForm.category = item.category;
  tagForm.tag_name = item.tag_name;
  error.value = "";
  showTagModal.value = true;
}

async function editTagName(item: any) {
  editingTagName.value = item;
  tagNameForm.name = item.name;
  tagNameForm.category = item.category;
  error.value = "";

  // Load tags for this group
  selectedTags.value = item.tags ? [...item.tags] : [];
  await loadAllTags();

  showTagNameModal.value = true;
}

function isTagSelected(tagId: number): boolean {
  return selectedTags.value.some((t) => t.id === tagId);
}

function toggleTagSelection(tag: any) {
  if (isTagSelected(tag.id)) {
    selectedTags.value = selectedTags.value.filter((t) => t.id !== tag.id);
  } else {
    selectedTags.value.push(tag);
  }
}

function removeSelectedTag(tag: any) {
  selectedTags.value = selectedTags.value.filter((t) => t.id !== tag.id);
}

async function quickAddTags() {
  if (!quickAddInput.value.trim() || !editingTagName.value) return;

  const newTags = quickAddInput.value
    .split(",")
    .map((v) => v.trim())
    .filter((v) => v.length > 0);

  let created = 0;
  let linked = 0;
  quickAddStatus.value = "";

  for (const tagName of newTags) {
    // Check if tag already exists
    const existing = allTags.value.find(
      (t) => t.name.toLowerCase() === tagName.toLowerCase()
    );

    if (existing) {
      // Add existing tag if not already selected
      if (!isTagSelected(existing.id)) {
        selectedTags.value.push(existing);
        linked++;
      }
    } else {
      // Create new tag
      try {
        const slug = generateSlug(tagName);
        const res = await tagsAdminAPI.create({
          name: tagName,
          slug: slug,
          category: tagNameForm.category,
          tag_name: editingTagName.value.id,
        });
        const newTag = res.data;
        allTags.value.push(newTag);
        selectedTags.value.push(newTag);
        created++;
      } catch (e: any) {
        console.error("Error creating tag:", e);
      }
    }
  }

  quickAddInput.value = "";

  // Show status message
  const messages = [];
  if (created > 0) messages.push(`✅ Создано: ${created}`);
  if (linked > 0) messages.push(`🔗 Привязано: ${linked}`);
  quickAddStatus.value = messages.join(", ");
  setTimeout(() => {
    quickAddStatus.value = "";
  }, 3000);
}

async function saveTag() {
  try {
    saving.value = true;
    error.value = "";
    if (editingTag.value) {
      await tagsAdminAPI.update(editingTag.value.id, tagForm);
    } else {
      await tagsAdminAPI.create(tagForm);
    }
    showTagModal.value = false;
    loadItems();
    loadAllTags();
  } catch (e: any) {
    error.value = e.response?.data?.detail || "Ошибка";
  } finally {
    saving.value = false;
  }
}

async function saveTagName() {
  try {
    saving.value = true;
    error.value = "";

    if (editingTagName.value) {
      // Update tag name
      await tagNamesAdminAPI.update(editingTagName.value.id, tagNameForm);

      // Update tag associations
      const currentTagIds = new Set(selectedTags.value.map((t) => t.id));
      const originalTagIds = new Set(
        (editingTagName.value.tags || []).map((t: any) => t.id)
      );

      // Tags to link (newly selected)
      for (const tag of selectedTags.value) {
        if (!originalTagIds.has(tag.id)) {
          await tagsAdminAPI.update(tag.id, {
            tag_name: editingTagName.value.id,
          });
        }
      }

      // Tags to unlink (deselected)
      for (const tag of editingTagName.value.tags || []) {
        if (!currentTagIds.has(tag.id)) {
          await tagsAdminAPI.update(tag.id, { tag_name: null });
        }
      }
      showTagNameModal.value = false;
      loadItems();
    } else {
      // Create new group and immediately open for editing
      const res = await tagNamesAdminAPI.create(tagNameForm);
      const newTagName = res.data;
      await loadItems();
      await loadAllTags();

      // Immediately open the newly created group for editing
      editingTagName.value = { ...newTagName, tags: [] };
      tagNameForm.name = newTagName.name;
      tagNameForm.category = newTagName.category;
      selectedTags.value = [];
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || "Ошибка";
  } finally {
    saving.value = false;
  }
}

function confirmDeleteTag(item: any) {
  deletingItem.value = item;
  deleteType.value = "tag";
  showDeleteModal.value = true;
}

function confirmDeleteTagName(item: any) {
  deletingItem.value = item;
  deleteType.value = "tagName";
  showDeleteModal.value = true;
}

async function performDelete() {
  try {
    deleting.value = true;
    if (deleteType.value === "tag") {
      await tagsAdminAPI.delete(deletingItem.value.id);
    } else {
      await tagNamesAdminAPI.delete(deletingItem.value.id);
    }
    showDeleteModal.value = false;
    deletingItem.value = null;
    loadItems();
  } catch (e) {
    alert("Ошибка удаления");
  } finally {
    deleting.value = false;
  }
}

watch(activeTab, loadItems);

onMounted(() => {
  loadItems();
  loadCategories();
  loadAllTags();
});
</script>

<style scoped>
.tags-count {
  font-size: 12px;
  color: #666;
}

.tags-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.tag-chip.small {
  font-size: 11px;
  padding: 2px 6px;
  background: #e0e7ff;
  color: #4f46e5;
  border-radius: 4px;
}

.more-tags {
  font-size: 11px;
  color: #666;
}

.selected-values {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  min-height: 50px;
  margin-bottom: 16px;
}

.value-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: #4f46e5;
  color: white;
  border-radius: 16px;
  font-size: 13px;
}

.chip-remove {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  cursor: pointer;
  padding: 0 4px;
  border-radius: 50%;
  font-size: 12px;
}

.chip-remove:hover {
  background: rgba(255, 255, 255, 0.3);
}

.no-values {
  color: #94a3b8;
  font-style: italic;
}

.quick-add-section {
  margin-bottom: 16px;
}

.quick-add-section label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.quick-add-row {
  display: flex;
  gap: 8px;
}

.quick-add-row input {
  flex: 1;
}

.available-values {
  margin-top: 16px;
}

.available-values label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.values-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.value-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.value-item:hover {
  border-color: #4f46e5;
  background: #f0f0ff;
}

.value-item.selected {
  background: #e0e7ff;
  border-color: #4f46e5;
}

.value-name {
  font-size: 13px;
}

.value-check {
  font-size: 14px;
  color: #4f46e5;
}

.no-items {
  grid-column: 1 / -1;
  text-align: center;
  color: #94a3b8;
  padding: 20px;
}

.info-msg {
  padding: 16px;
  background: #fef3c7;
  border: 1px solid #fcd34d;
  border-radius: 8px;
  color: #92400e;
  margin: 16px 0;
}

.quick-add-status {
  margin-top: 8px;
  padding: 8px 12px;
  background: #d1fae5;
  color: #065f46;
  border-radius: 6px;
  font-size: 13px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

</style>
