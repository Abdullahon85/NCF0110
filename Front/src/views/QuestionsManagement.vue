<template>
  <div class="management-page">
    <div class="page-header">
      <h1>❓ Вопросы о товарах</h1>
      <span class="messages-count">{{ unansweredCount }} без ответа</span>
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
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Автор</th>
            <th>Товар</th>
            <th>Вопрос</th>
            <th>Дата</th>
            <th>Ответ</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in items"
            :key="item.id"
            :class="{ unread: !item.admin_reply }"
          >
            <td data-label="ID">{{ item.id }}</td>
            <td data-label="Автор" class="name-cell">{{ item.author_name }}</td>
            <td data-label="Товар">{{ item.product_name }}</td>
            <td
              data-label="Вопрос"
              class="message-cell"
              @click="openReply(item)"
            >
              {{ truncate(item.text, 60) }}
            </td>
            <td data-label="Дата">{{ formatDate(item.created_at) }}</td>
            <td data-label="Ответ">
              <span v-if="item.admin_reply" class="badge badge-success"
                >Отвечен</span
              >
              <span v-else class="badge badge-warning">Ожидает</span>
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
            <td colspan="8" class="empty">Вопросов нет</td>
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
          <h2>Вопрос #{{ editingItem?.id }}</h2>
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
            <label>Дата:</label>
            <span>{{
              editingItem ? formatDateTime(editingItem.created_at) : ""
            }}</span>
          </div>
          <div class="message-field full">
            <label>Вопрос:</label>
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
            Удалить вопрос от <strong>{{ deletingItem?.author_name }}</strong
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
import { ref, computed, onMounted } from "vue";
import { questionsAdminAPI } from "@/api/admin";

interface QuestionItem {
  id: number;
  product: number;
  product_name: string;
  author_name: string;
  text: string;
  created_at: string;
  is_published: boolean;
  admin_reply: string;
  admin_reply_date: string | null;
}

const items = ref<QuestionItem[]>([]);
const search = ref("");
const publishedFilter = ref("");
const showReplyModal = ref(false);
const editingItem = ref<QuestionItem | null>(null);
const replyText = ref("");
const showDeleteModal = ref(false);
const deletingItem = ref<QuestionItem | null>(null);
const deleting = ref(false);
const saving = ref(false);

const unansweredCount = computed(
  () => items.value.filter((i) => !i.admin_reply).length,
);

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
    const response = await questionsAdminAPI.getAll(params);
    items.value = response.data.results || response.data;
  } catch (e) {
    console.error(e);
  }
}

function openReply(item: QuestionItem) {
  editingItem.value = item;
  replyText.value = item.admin_reply || "";
  showReplyModal.value = true;
}

async function saveReply() {
  if (!editingItem.value) return;
  try {
    saving.value = true;
    await questionsAdminAPI.update(editingItem.value.id, {
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

async function togglePublished(item: QuestionItem) {
  try {
    await questionsAdminAPI.update(item.id, {
      is_published: !item.is_published,
    });
    item.is_published = !item.is_published;
  } catch (e) {
    alert("Ошибка");
  }
}

function confirmDelete(item: QuestionItem) {
  deletingItem.value = item;
  showDeleteModal.value = true;
}

async function deleteItem() {
  if (!deletingItem.value) return;
  try {
    deleting.value = true;
    await questionsAdminAPI.delete(deletingItem.value.id);
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
