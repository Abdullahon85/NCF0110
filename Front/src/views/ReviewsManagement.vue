<template>
  <div class="management-page">
    <div class="page-header">
      <h1>⭐ Отзывы</h1>
      <span class="messages-count">{{ items.length }} всего</span>
    </div>

    <div class="filters-bar">
      <input
        v-model="search"
        type="text"
        placeholder="🔍 Поиск по имени или тексту..."
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
        <option value="false">Скрытые</option>
      </select>
      <select v-model="ratingFilter" @change="loadItems" class="filter-select">
        <option value="">Все оценки</option>
        <option value="5">⭐⭐⭐⭐⭐ 5</option>
        <option value="4">⭐⭐⭐⭐ 4</option>
        <option value="3">⭐⭐⭐ 3</option>
        <option value="2">⭐⭐ 2</option>
        <option value="1">⭐ 1</option>
      </select>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Автор</th>
            <th>Товар</th>
            <th>Оценка</th>
            <th>Отзыв</th>
            <th>Дата</th>
            <th>Ответ</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td data-label="ID">{{ item.id }}</td>
            <td data-label="Автор" class="name-cell">{{ item.author_name }}</td>
            <td data-label="Товар">{{ item.product_name }}</td>
            <td data-label="Оценка">
              <span class="stars">{{ "⭐".repeat(item.rating) }}</span>
            </td>
            <td
              data-label="Отзыв"
              class="message-cell"
              @click="openReply(item)"
            >
              {{ truncate(item.text, 50) }}
            </td>
            <td data-label="Дата">{{ formatDate(item.created_at) }}</td>
            <td data-label="Ответ">
              <span v-if="item.admin_reply" class="badge badge-success"
                >Есть</span
              >
              <span v-else class="badge badge-warning">Нет</span>
            </td>
            <td data-label="Статус">
              <span
                :class="[
                  'badge',
                  item.is_published ? 'badge-success' : 'badge-warning',
                ]"
              >
                {{ item.is_published ? "Опубликован" : "Скрыт" }}
              </span>
            </td>
            <td data-label="Действия">
              <div class="actions">
                <button
                  @click="openReply(item)"
                  class="btn-icon"
                  title="Просмотр / Ответить"
                >
                  💬
                </button>
                <button
                  @click="togglePublished(item)"
                  class="btn-icon"
                  :title="item.is_published ? 'Скрыть' : 'Опубликовать'"
                >
                  {{ item.is_published ? "🚫" : "✅" }}
                </button>
                <button
                  @click="confirmDelete(item)"
                  class="btn-icon delete"
                  title="Удалить"
                >
                  🗑️
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="9" class="empty">Отзывов нет</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Reply / View Modal -->
    <div
      v-if="showReplyModal"
      class="modal-overlay"
      @click.self="showReplyModal = false"
    >
      <div class="modal">
        <div class="modal-header">
          <h2>Отзыв #{{ editingItem?.id }}</h2>
          <button @click="showReplyModal = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="message-field">
            <label>Автор:</label>
            <span>{{ editingItem?.author_name }}</span>
          </div>
          <div class="message-field">
            <label>Товар:</label>
            <span>{{ editingItem?.product_name }}</span>
          </div>
          <div class="message-field">
            <label>Оценка:</label>
            <span>{{ "⭐".repeat(editingItem?.rating || 0) }}</span>
          </div>
          <div class="message-field">
            <label>Дата:</label>
            <span>{{
              editingItem ? formatDateTime(editingItem.created_at) : ""
            }}</span>
          </div>
          <div class="message-field full">
            <label>Отзыв:</label>
            <p class="message-text">{{ editingItem?.text }}</p>
          </div>
          <div class="form-group">
            <label>Ответ администратора:</label>
            <textarea
              v-model="replyText"
              rows="4"
              placeholder="Напишите ответ..."
            ></textarea>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="saveReply" class="btn btn-primary" :disabled="saving">
            💾 Сохранить ответ
          </button>
          <button @click="showReplyModal = false" class="btn btn-secondary">
            Закрыть
          </button>
        </div>
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
            Удалить отзыв от <strong>{{ deletingItem?.author_name }}</strong
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
import { ref, onMounted } from "vue";
import { reviewsAdminAPI } from "@/api/admin";

interface ReviewItem {
  id: number;
  product: number;
  product_name: string;
  author_name: string;
  rating: number;
  text: string;
  created_at: string;
  is_published: boolean;
  admin_reply: string;
  admin_reply_date: string | null;
}

const items = ref<ReviewItem[]>([]);
const search = ref("");
const publishedFilter = ref("");
const ratingFilter = ref("");
const showReplyModal = ref(false);
const editingItem = ref<ReviewItem | null>(null);
const replyText = ref("");
const showDeleteModal = ref(false);
const deletingItem = ref<ReviewItem | null>(null);
const deleting = ref(false);
const saving = ref(false);

function truncate(str: string, len: number) {
  return str.length > len ? str.slice(0, len) + "..." : str;
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("ru-RU");
}

function formatDateTime(dateStr: string) {
  return new Date(dateStr).toLocaleString("ru-RU");
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
    if (ratingFilter.value) params.rating = ratingFilter.value;
    const response = await reviewsAdminAPI.getAll(params);
    items.value = response.data.results || response.data;
  } catch (e) {
    console.error(e);
  }
}

function openReply(item: ReviewItem) {
  editingItem.value = item;
  replyText.value = item.admin_reply || "";
  showReplyModal.value = true;
}

async function saveReply() {
  if (!editingItem.value) return;
  try {
    saving.value = true;
    await reviewsAdminAPI.update(editingItem.value.id, {
      admin_reply: replyText.value,
    });
    editingItem.value.admin_reply = replyText.value;
    showReplyModal.value = false;
    loadItems();
  } catch (e) {
    alert("Ошибка сохранения");
  } finally {
    saving.value = false;
  }
}

async function togglePublished(item: ReviewItem) {
  try {
    await reviewsAdminAPI.update(item.id, { is_published: !item.is_published });
    item.is_published = !item.is_published;
  } catch (e) {
    alert("Ошибка");
  }
}

function confirmDelete(item: ReviewItem) {
  deletingItem.value = item;
  showDeleteModal.value = true;
}

async function deleteItem() {
  if (!deletingItem.value) return;
  try {
    deleting.value = true;
    await reviewsAdminAPI.delete(deletingItem.value.id);
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
