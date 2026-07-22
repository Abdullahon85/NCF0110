<template>
  <div class="management-page">
    <div class="page-header">
      <h1>📰 Управление новостями</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        ➕ Добавить новость
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
      <select
        v-model="publishedFilter"
        @change="loadItems"
        class="filter-select"
      >
        <option value="">Все</option>
        <option value="true">Опубликованные</option>
        <option value="false">Черновики</option>
      </select>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Заголовок</th>
            <th>Дата</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td data-label="ID">{{ item.id }}</td>
            <td data-label="Заголовок" class="name-cell">{{ item.title }}</td>
            <td data-label="Дата">{{ formatDate(item.pub_date) }}</td>
            <td data-label="Статус">
              <span
                :class="[
                  'badge',
                  item.is_published ? 'badge-success' : 'badge-warning',
                ]"
              >
                {{ item.is_published ? "Опубликовано" : "Черновик" }}
              </span>
            </td>
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
            <td colspan="5" class="empty">Новости не найдены</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h2>{{ editingItem ? "Редактировать новость" : "Новая новость" }}</h2>
          <button @click="closeModal" class="close-btn">✕</button>
        </div>
        <form @submit.prevent="saveItem" class="modal-body">
          <div class="form-group">
            <label>Заголовок *</label>
            <input
              v-model="form.title"
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
            <label>Краткое описание *</label>
            <textarea
              v-model="form.preview"
              rows="2"
              required
              maxlength="500"
            ></textarea>
          </div>
          <div class="form-group">
            <label>Содержание *</label>
            <textarea v-model="form.content" rows="8" required></textarea>
          </div>
          <div class="form-group">
            <label>Ссылка на изображение</label>
            <input v-model="form.image" type="url" placeholder="https://..." />
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="form.is_published" type="checkbox" />
              Опубликовать
            </label>
          </div>
          <div v-if="error" class="error-msg">{{ error }}</div>
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">
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
            Удалить новость <strong>{{ deletingItem?.title }}</strong
            >?
          </p>
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
import { newsAdminAPI } from "@/api/admin";

interface NewsItem {
  id: number;
  title: string;
  slug: string;
  preview: string;
  content: string;
  image?: string;
  pub_date: string;
  is_published: boolean;
}

const items = ref<NewsItem[]>([]);
const search = ref("");
const publishedFilter = ref("");
const showModal = ref(false);
const editingItem = ref<NewsItem | null>(null);
const saving = ref(false);
const error = ref("");

const form = reactive({
  title: "",
  slug: "",
  preview: "",
  content: "",
  image: "",
  is_published: true,
});

const showDeleteModal = ref(false);
const deletingItem = ref<NewsItem | null>(null);
const deleting = ref(false);

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
  form.slug = form.title
    .toLowerCase()
    .split("")
    .map((c) => translitMap[c] || c)
    .join("")
    .replace(/[^a-z0-9-]/g, "")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
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
    if (publishedFilter.value) params.is_published = publishedFilter.value;
    const response = await newsAdminAPI.getAll(params);
    items.value = response.data.results || response.data;
  } catch (e) {
    console.error(e);
  }
}

function openCreateModal() {
  editingItem.value = null;
  form.title = "";
  form.slug = "";
  form.preview = "";
  form.content = "";
  form.image = "";
  form.is_published = true;
  error.value = "";
  showModal.value = true;
}

function editItem(item: NewsItem) {
  editingItem.value = item;
  form.title = item.title;
  form.slug = item.slug;
  form.preview = item.preview;
  form.content = item.content;
  form.image = item.image || "";
  form.is_published = item.is_published;
  error.value = "";
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingItem.value = null;
}

async function saveItem() {
  try {
    saving.value = true;
    error.value = "";
    const data = { ...form };
    if (editingItem.value)
      await newsAdminAPI.update(editingItem.value.id, data);
    else await newsAdminAPI.create(data);
    closeModal();
    loadItems();
  } catch (e: any) {
    error.value = e.response?.data?.detail || "Ошибка сохранения";
  } finally {
    saving.value = false;
  }
}

function confirmDelete(item: NewsItem) {
  deletingItem.value = item;
  showDeleteModal.value = true;
}

async function deleteItem() {
  if (!deletingItem.value) return;
  try {
    deleting.value = true;
    await newsAdminAPI.delete(deletingItem.value.id);
    showDeleteModal.value = false;
    loadItems();
  } catch (e) {
    alert("Ошибка удаления");
  } finally {
    deleting.value = false;
  }
}

onMounted(loadItems);
</script>

<!-- Styles in main.css -->
