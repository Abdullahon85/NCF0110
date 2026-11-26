<template>
  <div class="management-page">
    <!-- Header -->
    <div class="page-header">
      <button class="btn btn-primary" @click="openCreateModal">
        <AdminIcon name="plus" /> Добавить каталог
      </button>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <input
        v-model="search"
        type="text"
        placeholder="Поиск по названию..."
        class="search-input"
        @input="debouncedSearch"
      />
      <select v-model="parentFilter" class="filter-select" @change="loadItems">
        <option value="">Весь каталог</option>
        <option value="null">Только корневые</option>
        <option v-for="cat in allCategories" :key="cat.id" :value="cat.id">
          {{ cat.name }}
        </option>
      </select>
    </div>

    <!-- Table -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Изображение</th>
            <th>Название</th>
            <th>Slug</th>
            <th>Родитель</th>
            <th>Порядок</th>
            <th>Товаров</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td data-label="ID">{{ item.id }}</td>
            <td data-label="Изображение">
              <img v-if="item.image" :src="getImageUrl(item.image)" class="thumb" alt="" />
              <span v-else class="no-image">—</span>
            </td>
            <td data-label="Название" class="name-cell">{{ item.name }}</td>
            <td data-label="Slug" class="slug-cell">{{ item.slug }}</td>
            <td data-label="Родитель">{{ item.parent_name || "—" }}</td>
            <td data-label="Порядок">{{ item.order }}</td>
            <td data-label="Товаров">{{ item.products_count }}</td>
            <td data-label="Действия">
              <div class="actions">
                <button
                  class="btn-icon"
                  title="Редактировать"
                  aria-label="Редактировать"
                  @click="editItem(item)"
                >
                  <AdminIcon name="edit" />
                </button>
                <button
                  class="btn-icon delete"
                  title="Удалить"
                  aria-label="Удалить"
                  @click="confirmDelete(item)"
                >
                  <AdminIcon name="trash" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="8" class="empty">
              <p class="empty-text">Каталог не найден</p>
              <button class="btn btn-primary" @click="openCreateModal">
                <AdminIcon name="plus" /> Добавить каталог
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>
            {{ editingItem ? "Редактировать каталог" : "Новый каталог" }}
          </h2>
          <button class="close-btn" aria-label="Закрыть" @click="closeModal">
            <AdminIcon name="close" />
          </button>
        </div>
        <form class="modal-body" @submit.prevent="saveItem">
          <div class="form-group">
            <label>Название *</label>
            <input v-model="form.name" type="text" required @input="generateSlug" />
          </div>
          <div class="form-group">
            <label>Slug *</label>
            <input v-model="form.slug" type="text" required />
          </div>
          <div class="form-group">
            <label>Родительский каталог</label>
            <select v-model="form.parent">
              <option :value="null">— Нет (корневой) —</option>
              <option v-for="cat in availableParents" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Порядок сортировки</label>
            <input v-model.number="form.order" type="number" min="0" />
          </div>

          <!-- Image Upload Section -->
          <div class="form-group">
            <label>Изображение каталога</label>
            <div class="image-upload-container">
              <div
                v-if="imagePreview || (editingItem?.image && !shouldRemoveImage)"
                class="image-preview"
              >
                <img :src="imagePreview || getImageUrl(editingItem?.image ?? null)" alt="Preview" />
                <button
                  type="button"
                  class="remove-image-btn"
                  title="Удалить изображение"
                  aria-label="Удалить изображение"
                  @click="removeImage"
                >
                  <AdminIcon name="close" />
                </button>
              </div>
              <div v-else class="upload-placeholder">
                <input
                  id="imageInput"
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  class="file-input"
                  @change="handleImageSelect"
                />
                <label for="imageInput" class="upload-label"> 📷 Выбрать изображение </label>
              </div>
            </div>
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Отмена</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? "Сохранение..." : "Сохранить" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Подтверждение удаления</h2>
        </div>
        <div class="modal-body">
          <p>
            Вы уверены, что хотите удалить каталог
            <strong>{{ deletingItem?.name }}</strong>?
          </p>
          <p class="warning">
            ⚠️ Это действие нельзя отменить! Удалить можно только каталог без товаров и
            подкаталогов: сначала перенесите или удалите их.
          </p>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showDeleteModal = false">Отмена</button>
          <button class="btn btn-danger" :disabled="deleting" @click="deleteItem">
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
import { ref, reactive, computed, onMounted } from "vue";
import { makeSlug } from "@/utils/slug";
import { categoriesAdminAPI } from "@/api/admin";
import { getImageUrl } from "@/api";

interface Category {
  id: number;
  name: string;
  slug: string;
  parent: number | null;
  parent_name?: string;
  image?: string;
  order: number;
  products_count: number;
}

const items = ref<Category[]>([]);
const allCategories = ref<Category[]>([]);
const loading = ref(false);
const search = ref("");
const parentFilter = ref("");

// Modal state
const showModal = ref(false);
const editingItem = ref<Category | null>(null);
const saving = ref(false);
const error = ref("");

const form = reactive({
  name: "",
  slug: "",
  parent: null as number | null,
  order: 0,
});

// Image upload state
const imagePreview = ref("");
const selectedImageFile = ref<File | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);
const shouldRemoveImage = ref(false);

// Delete state
const showDeleteModal = ref(false);
const deletingItem = ref<Category | null>(null);
const deleting = ref(false);

// Computed
// A category cannot be moved under itself or under any of its own subcategories
// (the server refuses it too): that would cut the branch off the site.
const availableParents = computed(() => {
  const editing = editingItem.value;
  if (!editing) return allCategories.value;
  const excluded = new Set<number>([editing.id]);
  let grew = true;
  while (grew) {
    grew = false;
    for (const c of allCategories.value) {
      if (c.parent != null && excluded.has(c.parent) && !excluded.has(c.id)) {
        excluded.add(c.id);
        grew = true;
      }
    }
  }
  return allCategories.value.filter((c) => !excluded.has(c.id));
});

function generateSlug() {
  if (editingItem.value) return; // don't touch the slug of an existing item
  form.slug = makeSlug(form.name);
}

let searchTimeout: number;
function debouncedSearch() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(loadItems, 300);
}

async function loadItems() {
  try {
    loading.value = true;
    const params: any = {};
    if (search.value) params.search = search.value;
    if (parentFilter.value) params.parent = parentFilter.value;

    const response = await categoriesAdminAPI.getAll(params);
    items.value = response.data.results || response.data;
  } catch (e) {
    console.error("Failed to load categories:", e);
  } finally {
    loading.value = false;
  }
}

async function loadAllCategories() {
  try {
    const response = await categoriesAdminAPI.getAll();
    allCategories.value = response.data.results || response.data;
  } catch (e) {
    console.error("Failed to load all categories:", e);
  }
}

function openCreateModal() {
  editingItem.value = null;
  form.name = "";
  form.slug = "";
  form.parent = null;
  form.order = 0;
  error.value = "";
  imagePreview.value = "";
  selectedImageFile.value = null;
  shouldRemoveImage.value = false;
  showModal.value = true;
}

function editItem(item: Category) {
  editingItem.value = { ...item };
  form.name = item.name;
  form.slug = item.slug;
  form.parent = item.parent;
  form.order = item.order;
  error.value = "";
  imagePreview.value = "";
  selectedImageFile.value = null;
  shouldRemoveImage.value = false;
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingItem.value = null;
  imagePreview.value = "";
  selectedImageFile.value = null;
  shouldRemoveImage.value = false;
}

function handleImageSelect(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];

  if (file) {
    selectedImageFile.value = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
}

function removeImage() {
  imagePreview.value = "";
  selectedImageFile.value = null;
  if (fileInput.value) fileInput.value.value = "";
  // Mark existing server image for deletion
  if (editingItem.value?.image) {
    shouldRemoveImage.value = true;
  }
}

async function uploadImage(categoryId: number): Promise<void> {
  if (!selectedImageFile.value) return;

  const formData = new FormData();
  formData.append("image", selectedImageFile.value);

  await categoriesAdminAPI.uploadImage(categoryId, formData);
}

async function saveItem() {
  try {
    saving.value = true;
    error.value = "";

    const data = {
      name: form.name,
      slug: form.slug,
      parent: form.parent,
      order: form.order,
    };

    let categoryId: number;

    if (editingItem.value) {
      await categoriesAdminAPI.update(editingItem.value.id, data);
      categoryId = editingItem.value.id;
    } else {
      const response = await categoriesAdminAPI.create(data);
      categoryId = response.data.id;
    }

    // Delete existing image if flagged
    if (shouldRemoveImage.value && editingItem.value) {
      await categoriesAdminAPI.deleteImage(categoryId);
    }

    // Upload new image if selected
    if (selectedImageFile.value) {
      await uploadImage(categoryId);
    }

    closeModal();
    loadItems();
    loadAllCategories();
  } catch (e: any) {
    error.value = adminErrorMessage(e, "Ошибка сохранения");
  } finally {
    saving.value = false;
  }
}

function confirmDelete(item: Category) {
  deletingItem.value = item;
  showDeleteModal.value = true;
}

async function deleteItem() {
  if (!deletingItem.value) return;

  try {
    deleting.value = true;
    await categoriesAdminAPI.delete(deletingItem.value.id);
    showDeleteModal.value = false;
    deletingItem.value = null;
    loadItems();
    loadAllCategories();
  } catch (e: any) {
    toast.error(adminErrorMessage(e, "Ошибка удаления"));
  } finally {
    deleting.value = false;
  }
}

onMounted(() => {
  loadItems();
  loadAllCategories();
});
</script>

<!-- Styles in styles/site/ -->
