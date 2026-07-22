<template>
  <div class="management-page">
    <div class="page-header">
      <h1>🏷️ Управление брендами</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        ➕ Добавить бренд
      </button>
    </div>

    <div class="filters-bar">
      <input
        v-model="search"
        type="text"
        placeholder="🔍 Поиск..."
        class="search-input"
        @input="debouncedSearch"
      />
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Лого</th>
            <th>Название</th>
            <th>Slug</th>
            <th>Описание</th>
            <th>Товаров</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td data-label="ID">{{ item.id }}</td>
            <td data-label="Лого">
              <img
                v-if="item.logo_url"
                :src="item.logo_url"
                class="thumb"
                alt=""
              />
              <span v-else class="no-image">—</span>
            </td>
            <td data-label="Название" class="name-cell">{{ item.name }}</td>
            <td data-label="Slug" class="slug-cell">{{ item.slug }}</td>
            <td data-label="Описание">{{ truncate(item.description, 50) }}</td>
            <td data-label="Товаров">{{ item.products_count }}</td>
            <td data-label="Действия">
              <div class="actions">
                <button @click="editItem(item)" class="btn-icon">✏️</button>
                <button @click="confirmDelete(item)" class="btn-icon delete">
                  🗑️
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="7" class="empty">Бренды не найдены</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editingItem ? "Редактировать бренд" : "Новый бренд" }}</h2>
          <button @click="closeModal" class="close-btn">✕</button>
        </div>
        <form @submit.prevent="saveItem" class="modal-body">
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
            <label>Slug *</label>
            <input v-model="form.slug" type="text" required />
          </div>
          <div class="form-group">
            <label>Описание</label>
            <textarea v-model="form.description" rows="3"></textarea>
          </div>

          <!-- Logo Upload Section -->
          <div class="form-group">
            <label>Логотип бренда</label>
            <div class="image-upload-container">
              <div
                v-if="logoPreview || editingItem?.logo_url"
                class="image-preview"
              >
                <img
                  :src="logoPreview || editingItem?.logo_url"
                  alt="Logo Preview"
                />
                <button
                  type="button"
                  @click="removeLogo"
                  class="remove-image-btn"
                  title="Удалить логотип"
                >
                  ✕
                </button>
              </div>
              <div v-else class="upload-placeholder">
                <input
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  @change="handleLogoSelect"
                  class="file-input"
                  id="logoInput"
                />
                <label for="logoInput" class="upload-label">
                  📷 Выбрать логотип
                </label>
              </div>
            </div>
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>
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

    <!-- Delete Modal -->
    <div
      v-if="showDeleteModal"
      class="modal-overlay"
      @click.self="showDeleteModal = false"
    >
      <div class="modal modal-sm">
        <div class="modal-header"><h2>Подтверждение удаления</h2></div>
        <div class="modal-body">
          <p>
            Удалить бренд <strong>{{ deletingItem?.name }}</strong
            >?
          </p>
          <p class="warning">⚠️ Это действие нельзя отменить!</p>
        </div>
        <div class="modal-actions">
          <button @click="showDeleteModal = false" class="btn btn-secondary">
            Отмена
          </button>
          <button
            @click="deleteItem"
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
import { ref, reactive, onMounted } from "vue";
import { brandsAdminAPI } from "@/api/admin";

interface Brand {
  id: number;
  name: string;
  slug: string;
  logo_url?: string;
  description: string;
  products_count: number;
}

const items = ref<Brand[]>([]);
const search = ref("");
const showModal = ref(false);
const editingItem = ref<Brand | null>(null);
const saving = ref(false);
const error = ref("");
const form = reactive({ name: "", slug: "", description: "" });
const showDeleteModal = ref(false);
const deletingItem = ref<Brand | null>(null);
const deleting = ref(false);

// Logo upload state
const logoPreview = ref("");
const selectedLogoFile = ref<File | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);

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
  if (editingItem.value) return;
  form.slug = form.name
    .toLowerCase()
    .split("")
    .map((c) => translitMap[c] || c)
    .join("")
    .replace(/[^a-z0-9-]/g, "")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

function truncate(str: string, len: number) {
  return str?.length > len ? str.substring(0, len) + "..." : str || "";
}

let searchTimeout: number;
function debouncedSearch() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(loadItems, 300);
}

async function loadItems() {
  try {
    const params: any = {};
    if (search.value) params.search = search.value;
    const response = await brandsAdminAPI.getAll(params);
    items.value = response.data.results || response.data;
  } catch (e) {
    console.error(e);
  }
}

function openCreateModal() {
  editingItem.value = null;
  form.name = "";
  form.slug = "";
  form.description = "";
  error.value = "";
  logoPreview.value = "";
  selectedLogoFile.value = null;
  showModal.value = true;
}

function editItem(item: Brand) {
  editingItem.value = item;
  form.name = item.name;
  form.slug = item.slug;
  form.description = item.description;
  error.value = "";
  logoPreview.value = "";
  selectedLogoFile.value = null;
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingItem.value = null;
  logoPreview.value = "";
  selectedLogoFile.value = null;
}

function handleLogoSelect(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];

  if (file) {
    selectedLogoFile.value = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      logoPreview.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
}

function removeLogo() {
  logoPreview.value = "";
  selectedLogoFile.value = null;
  if (fileInput.value) {
    fileInput.value.value = "";
  }
}

async function uploadLogo(brandId: number): Promise<void> {
  if (!selectedLogoFile.value) return;

  const formData = new FormData();
  formData.append("logo", selectedLogoFile.value);

  await brandsAdminAPI.uploadLogo(brandId, formData);
}

async function saveItem() {
  try {
    saving.value = true;
    error.value = "";

    let brandId: number;

    if (editingItem.value) {
      await brandsAdminAPI.update(editingItem.value.id, form);
      brandId = editingItem.value.id;
    } else {
      const response = await brandsAdminAPI.create(form);
      brandId = response.data.id;
    }

    // Upload logo if selected
    if (selectedLogoFile.value) {
      await uploadLogo(brandId);
    }

    closeModal();
    loadItems();
  } catch (e: any) {
    error.value = e.response?.data?.detail || "Ошибка сохранения";
  } finally {
    saving.value = false;
  }
}

function confirmDelete(item: Brand) {
  deletingItem.value = item;
  showDeleteModal.value = true;
}

async function deleteItem() {
  if (!deletingItem.value) return;
  try {
    deleting.value = true;
    await brandsAdminAPI.delete(deletingItem.value.id);
    showDeleteModal.value = false;
    deletingItem.value = null;
    loadItems();
  } catch (e: any) {
    alert("Ошибка удаления");
  } finally {
    deleting.value = false;
  }
}

onMounted(loadItems);
</script>

<!-- Styles in main.css -->
