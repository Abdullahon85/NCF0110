<template>
  <div class="management-page">
    <div class="page-header">
      <h1>✉️ Сообщения</h1>
      <span class="messages-count">{{ unprocessedCount }} непрочитанных</span>
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
        v-model="processedFilter"
        @change="loadItems"
        class="filter-select"
      >
        <option value="">Все</option>
        <option value="false">Непрочитанные</option>
        <option value="true">Обработанные</option>
      </select>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Имя</th>
            <th>Email</th>
            <th>Телефон</th>
            <th>Сообщение</th>
            <th>Дата</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in items"
            :key="item.id"
            :class="{ unread: !item.is_processed }"
          >
            <td data-label="ID">{{ item.id }}</td>
            <td data-label="Имя" class="name-cell">{{ item.name }}</td>
            <td data-label="Email">
              <a :href="'mailto:' + item.email">{{ item.email }}</a>
            </td>
            <td data-label="Телефон">
              <a :href="'tel:' + item.phone">{{ item.phone }}</a>
            </td>
            <td
              data-label="Сообщение"
              class="message-cell"
              @click="viewMessage(item)"
            >
              {{ truncate(item.message, 50) }}
            </td>
            <td data-label="Дата">{{ formatDate(item.created_at) }}</td>
            <td data-label="Статус">
              <span
                :class="[
                  'badge',
                  item.is_processed ? 'badge-success' : 'badge-warning',
                ]"
              >
                {{ item.is_processed ? "Обработано" : "Новое" }}
              </span>
            </td>
            <td data-label="Действия">
              <div class="actions">
                <button
                  @click="viewMessage(item)"
                  class="btn-icon"
                  title="Просмотр"
                >
                  👁️
                </button>
                <button
                  v-if="!item.is_processed"
                  @click="markProcessed(item)"
                  class="btn-icon"
                  title="Пометить как обработанное"
                >
                  ✅
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
            <td colspan="8" class="empty">Сообщений нет</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- View Modal -->
    <div
      v-if="showViewModal"
      class="modal-overlay"
      @click.self="showViewModal = false"
    >
      <div class="modal">
        <div class="modal-header">
          <h2>Сообщение #{{ viewingItem?.id }}</h2>
          <button @click="showViewModal = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body message-view">
          <div class="message-field">
            <label>Имя:</label>
            <span>{{ viewingItem?.name }}</span>
          </div>
          <div class="message-field">
            <label>Email:</label>
            <a :href="'mailto:' + viewingItem?.email">{{
              viewingItem?.email
            }}</a>
          </div>
          <div class="message-field">
            <label>Телефон:</label>
            <a :href="'tel:' + viewingItem?.phone">{{ viewingItem?.phone }}</a>
          </div>
          <div class="message-field">
            <label>Дата:</label>
            <span>{{
              viewingItem ? formatDateTime(viewingItem.created_at) : ""
            }}</span>
          </div>
          <div class="message-field full">
            <label>Сообщение:</label>
            <p class="message-text">{{ viewingItem?.message }}</p>
          </div>
        </div>
        <div class="modal-actions">
          <button
            v-if="viewingItem && !viewingItem.is_processed"
            @click="
              markProcessed(viewingItem);
              showViewModal = false;
            "
            class="btn btn-primary"
          >
            ✅ Отметить как обработанное
          </button>
          <button @click="showViewModal = false" class="btn btn-secondary">
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
            Удалить сообщение от <strong>{{ deletingItem?.name }}</strong
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
import { messagesAdminAPI } from "@/api/admin";

interface Message {
  id: number;
  name: string;
  email: string;
  phone: string;
  message: string;
  created_at: string;
  is_processed: boolean;
}

const items = ref<Message[]>([]);
const search = ref("");
const processedFilter = ref("");
const showViewModal = ref(false);
const viewingItem = ref<Message | null>(null);
const showDeleteModal = ref(false);
const deletingItem = ref<Message | null>(null);
const deleting = ref(false);

const unprocessedCount = computed(
  () => items.value.filter((i) => !i.is_processed).length
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
    if (processedFilter.value) params.is_processed = processedFilter.value;
    const response = await messagesAdminAPI.getAll(params);
    items.value = response.data.results || response.data;
  } catch (e) {
    console.error(e);
  }
}

function viewMessage(item: Message) {
  viewingItem.value = item;
  showViewModal.value = true;
}

async function markProcessed(item: Message) {
  try {
    await messagesAdminAPI.markProcessed(item.id);
    item.is_processed = true;
  } catch (e) {
    alert("Ошибка");
  }
}

function confirmDelete(item: Message) {
  deletingItem.value = item;
  showDeleteModal.value = true;
}

async function deleteItem() {
  if (!deletingItem.value) return;
  try {
    deleting.value = true;
    await messagesAdminAPI.delete(deletingItem.value.id);
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
