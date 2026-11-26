<template>
  <div class="management-page">
    <div class="page-header">
      <button class="btn btn-primary" @click="openCreateModal">
        <AdminIcon name="plus" /> Добавить баннер
      </button>
    </div>

    <div class="filters-bar">
      <input
        v-model="search"
        type="text"
        placeholder="Поиск..."
        class="search-input"
        @input="debouncedSearch"
      />
      <select v-model="activeFilter" class="filter-select" @change="loadItems">
        <option value="">Все</option>
        <option value="true">Активные</option>
        <option value="false">Неактивные</option>
      </select>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Порядок</th>
            <th>Изображение</th>
            <th>Заголовок</th>
            <th>Ссылка</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredItems" :key="item.id">
            <td data-label="Порядок">{{ item.order }}</td>
            <td data-label="Изображение">
              <img v-if="item.image" :src="item.image" :alt="item.title" class="table-image" />
              <span v-else class="no-image">Нет фото</span>
            </td>
            <td data-label="Заголовок" class="name-cell">
              <strong>{{ item.title || "—" }}</strong>
              <small v-if="item.description" class="description-preview">
                {{ item.description.slice(0, 50) }}{{ item.description.length > 50 ? "..." : "" }}
              </small>
            </td>
            <td data-label="Ссылка">
              <a v-if="item.link" :href="item.link" target="_blank" class="link-preview">
                {{ item.link.slice(0, 30) }}{{ item.link.length > 30 ? "..." : "" }}
              </a>
              <span v-else class="text-muted">—</span>
            </td>
            <td data-label="Статус">
              <span :class="['badge', item.is_active ? 'badge-success' : 'badge-warning']">
                {{ item.is_active ? "Активен" : "Неактивен" }}
              </span>
            </td>
            <td data-label="Действия">
              <div class="actions">
                <button
                  class="btn-icon"
                  title="Вверх"
                  :disabled="item.order <= 1"
                  @click="moveUp(item)"
                >
                  ⬆️
                </button>
                <button
                  class="btn-icon"
                  title="Вниз"
                  :disabled="item.order >= items.length"
                  @click="moveDown(item)"
                >
                  ⬇️
                </button>
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
          <tr v-if="filteredItems.length === 0">
            <td colspan="6" class="empty">
              <p class="empty-text">Баннеры не найдены</p>
              <button class="btn btn-primary" @click="openCreateModal">
                <AdminIcon name="plus" /> Добавить баннер
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h2>{{ editingItem ? "Редактировать баннер" : "Новый баннер" }}</h2>
          <button class="close-btn" aria-label="Закрыть" @click="closeModal">
            <AdminIcon name="close" />
          </button>
        </div>
        <form class="modal-body" @submit.prevent="saveItem">
          <div class="form-row">
            <div class="form-group">
              <label>Заголовок</label>
              <input v-model="form.title" type="text" placeholder="Необязательно" />
            </div>
            <div class="form-group">
              <label>Порядок</label>
              <input v-model.number="form.order" type="number" min="0" />
            </div>
          </div>

          <div class="form-group">
            <label>Описание</label>
            <textarea
              v-model="form.description"
              rows="3"
              placeholder="Краткое описание для баннера"
            ></textarea>
          </div>

          <div class="form-group">
            <label>Ссылка</label>
            <input v-model="form.link" type="text" placeholder="/catalog или https://..." />
          </div>

          <div class="form-group">
            <label>Изображение</label>
            <div class="image-upload-area">
              <div v-if="form.image || imagePreview" class="image-preview">
                <img :src="imagePreview || form.image" alt="Preview" />
                <div class="image-actions">
                  <label class="change-image-btn">
                    📷 Изменить
                    <input
                      type="file"
                      accept="image/*"
                      class="file-input-hidden"
                      @change="handleFileSelect"
                    />
                  </label>
                  <button type="button" class="remove-image-btn" @click="removeImage">
                    <AdminIcon name="close" /> Удалить
                  </button>
                </div>
              </div>
              <label v-else class="upload-placeholder">
                <input
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  class="file-input-hidden"
                  @change="handleFileSelect"
                />
                <span>📷 Выберите изображение</span>
                <small>Рекомендуемый размер: 1920x800</small>
              </label>
            </div>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="form.is_active" type="checkbox" />
              Активен (отображается на сайте)
            </label>
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

    <!-- Delete Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Подтверждение удаления</h2>
        </div>
        <div class="modal-body">
          <p>
            Удалить баннер <strong>{{ deletingItem?.title }}</strong>?
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
import { ref, computed, onMounted } from "vue";
import { bannersAdminAPI } from "@/api/admin";
import type { Banner } from "@/types";

const items = ref<Banner[]>([]);
const loading = ref(true);
const search = ref("");
const activeFilter = ref("");
const showModal = ref(false);
const showDeleteModal = ref(false);
const editingItem = ref<Banner | null>(null);
const deletingItem = ref<Banner | null>(null);
const saving = ref(false);
const deleting = ref(false);
const error = ref("");
const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const imagePreview = ref<string | null>(null);
const imageRemoved = ref(false);

const form = ref({
  title: "",
  description: "",
  image: "",
  link: "",
  order: 0,
  is_active: true,
});

const filteredItems = computed(() => {
  let result = items.value;

  if (search.value) {
    const q = search.value.toLowerCase();
    result = result.filter(
      (item) => item.title.toLowerCase().includes(q) || item.description?.toLowerCase().includes(q),
    );
  }

  if (activeFilter.value !== "") {
    const isActive = activeFilter.value === "true";
    result = result.filter((item) => item.is_active === isActive);
  }

  return result;
});

async function loadItems() {
  loading.value = true;
  try {
    const res = await bannersAdminAPI.getAll();
    items.value = res.data;
  } catch (e) {
    console.error("Failed to load banners:", e);
  } finally {
    loading.value = false;
  }
}

let searchTimeout: number;
function debouncedSearch() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {}, 500);
}

function openCreateModal() {
  editingItem.value = null;
  form.value = {
    title: "",
    description: "",
    image: "",
    link: "",
    order: items.value.length + 1,
    is_active: true,
  };
  selectedFile.value = null;
  imagePreview.value = null;
  imageRemoved.value = false;
  error.value = "";
  showModal.value = true;
}

function editItem(item: Banner) {
  editingItem.value = item;
  form.value = {
    title: item.title,
    description: item.description || "",
    image: item.image || "",
    link: item.link || "",
    order: item.order,
    is_active: item.is_active,
  };
  selectedFile.value = null;
  imagePreview.value = null;
  imageRemoved.value = false;
  error.value = "";
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingItem.value = null;
  selectedFile.value = null;
  imagePreview.value = null;
  imageRemoved.value = false;
}

function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    selectedFile.value = file;
    imagePreview.value = URL.createObjectURL(file);
    imageRemoved.value = false;
  }
}

function removeImage() {
  selectedFile.value = null;
  imagePreview.value = null;
  form.value.image = "";
  imageRemoved.value = true;
  if (fileInput.value) {
    fileInput.value.value = "";
  }
}

async function saveItem() {
  saving.value = true;
  error.value = "";

  try {
    const data: any = {
      title: form.value.title,
      description: form.value.description || null,
      link: form.value.link || null,
      order: form.value.order,
      is_active: form.value.is_active,
    };

    let bannerId: number;

    if (editingItem.value) {
      const res = await bannersAdminAPI.update(editingItem.value.id, data);
      bannerId = res.data.id;
    } else {
      const res = await bannersAdminAPI.create(data);
      bannerId = res.data.id;
    }

    // Загружаем изображение если выбрано
    if (selectedFile.value) {
      const formData = new FormData();
      formData.append("image", selectedFile.value);
      await bannersAdminAPI.uploadImage(bannerId, formData);
    } else if (imageRemoved.value && editingItem.value) {
      // Если изображение было удалено, отправляем null
      await bannersAdminAPI.update(bannerId, { image: null });
    }

    closeModal();
    await loadItems();
  } catch (e: any) {
    error.value = adminErrorMessage(e, "Ошибка сохранения");
  } finally {
    saving.value = false;
  }
}

function confirmDelete(item: Banner) {
  deletingItem.value = item;
  showDeleteModal.value = true;
}

async function deleteItem() {
  if (!deletingItem.value) return;

  deleting.value = true;
  try {
    await bannersAdminAPI.delete(deletingItem.value.id);
    showDeleteModal.value = false;
    deletingItem.value = null;
    await loadItems();
  } catch (e: any) {
    console.error("Failed to delete banner:", e);
    toast.error(adminErrorMessage(e, "Ошибка при удалении баннера"));
  } finally {
    deleting.value = false;
  }
}

async function moveUp(item: Banner) {
  const idx = items.value.findIndex((i) => i.id === item.id);
  if (idx <= 0) return;

  const prev = items.value[idx - 1];
  await bannersAdminAPI.update(item.id, { order: prev.order });
  await bannersAdminAPI.update(prev.id, { order: item.order });
  await loadItems();
}

async function moveDown(item: Banner) {
  const idx = items.value.findIndex((i) => i.id === item.id);
  if (idx < 0 || idx >= items.value.length - 1) return;

  const next = items.value[idx + 1];
  await bannersAdminAPI.update(item.id, { order: next.order });
  await bannersAdminAPI.update(next.id, { order: item.order });
  await loadItems();
}

onMounted(loadItems);
</script>

<style scoped src="@/styles/views/BannersManagement.css"></style>
