<template>
  <div class="management-page">
    <div class="page-header">
      <button class="btn btn-primary" @click="openCreateModal">
        <AdminIcon name="plus" /> Добавить страницу
      </button>
    </div>

    <p class="hint-message">
      Страницы появляются в подвале сайта в колонке «Покупателям»: оплата, доставка, возврат,
      гарантия, частые вопросы. Текст — обычный, переносы строк сохраняются.
    </p>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Порядок</th>
            <th>Заголовок</th>
            <th>Адрес</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td data-label="Порядок">{{ item.order }}</td>
            <td data-label="Заголовок" class="name-cell">{{ item.title }}</td>
            <td data-label="Адрес">/info/{{ item.slug }}</td>
            <td data-label="Статус">
              <span :class="['badge', item.is_published ? 'badge-success' : 'badge-warning']">
                {{ item.is_published ? "Опубликована" : "Скрыта" }}
              </span>
            </td>
            <td data-label="Действия">
              <div class="actions">
                <button class="btn-icon" aria-label="Редактировать" @click="editItem(item)">
                  <AdminIcon name="edit" />
                </button>
                <button class="btn-icon delete" aria-label="Удалить" @click="confirmDelete(item)">
                  <AdminIcon name="trash" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="5" class="empty">
              <p class="empty-text">Страниц пока нет</p>
              <button class="btn btn-primary" @click="openCreateModal">
                <AdminIcon name="plus" /> Добавить страницу
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h2>{{ editingItem ? "Редактировать страницу" : "Новая страница" }}</h2>
          <button class="close-btn" aria-label="Закрыть" @click="closeModal">
            <AdminIcon name="close" />
          </button>
        </div>
        <form class="modal-body" @submit.prevent="saveItem">
          <div class="form-group">
            <label>Заголовок *</label>
            <input
              v-model="form.title"
              type="text"
              required
              maxlength="200"
              @input="generateSlug"
            />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Адрес (slug)</label>
              <input v-model="form.slug" type="text" placeholder="из заголовка" />
            </div>
            <div class="form-group">
              <label>Порядок</label>
              <input v-model.number="form.order" type="number" step="1" />
            </div>
          </div>
          <div class="form-group">
            <label>Текст</label>
            <textarea v-model="form.content" rows="12"></textarea>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="form.is_published" type="checkbox" />
              Опубликовать
            </label>
          </div>
          <div v-if="error" class="error-msg">{{ error }}</div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Отмена</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="deletingItem" class="modal-overlay" @click.self="deletingItem = null">
      <div class="modal modal-sm">
        <div class="modal-header"><h2>Подтверждение</h2></div>
        <div class="modal-body">
          <p>
            Удалить страницу <strong>{{ deletingItem.title }}</strong>?
          </p>
          <div v-if="error" class="error-msg">{{ error }}</div>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="deletingItem = null">Отмена</button>
          <button class="btn btn-danger" :disabled="saving" @click="deleteItem">Удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import AdminIcon from "@/components/admin/AdminIcon.vue";
import { pagesAdminAPI } from "@/api/admin";
import { adminErrorMessage } from "@/utils/apiError";
import { makeSlug } from "@/utils/slug";

interface InfoPageItem {
  id: number;
  title: string;
  slug: string;
  content: string;
  order: number;
  is_published: boolean;
}

const items = ref<InfoPageItem[]>([]);
const showModal = ref(false);
const editingItem = ref<InfoPageItem | null>(null);
const deletingItem = ref<InfoPageItem | null>(null);
const saving = ref(false);
const error = ref("");
const form = reactive({ title: "", slug: "", content: "", order: 0, is_published: true });

async function loadItems() {
  try {
    const { data } = await pagesAdminAPI.getAll();
    items.value = data.results ?? data;
  } catch (e) {
    error.value = adminErrorMessage(e, "Не удалось загрузить страницы");
  }
}

function generateSlug() {
  if (!editingItem.value) form.slug = makeSlug(form.title);
}

function openCreateModal() {
  editingItem.value = null;
  Object.assign(form, {
    title: "",
    slug: "",
    content: "",
    order: items.value.length,
    is_published: true,
  });
  error.value = "";
  showModal.value = true;
}

function editItem(item: InfoPageItem) {
  editingItem.value = item;
  Object.assign(form, item);
  error.value = "";
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingItem.value = null;
}

async function saveItem() {
  saving.value = true;
  error.value = "";
  try {
    const data = { ...form, slug: form.slug.trim() || undefined };
    if (editingItem.value) await pagesAdminAPI.update(editingItem.value.id, data);
    else await pagesAdminAPI.create(data);
    closeModal();
    await loadItems();
  } catch (e) {
    error.value = adminErrorMessage(e, "Ошибка сохранения");
  } finally {
    saving.value = false;
  }
}

function confirmDelete(item: InfoPageItem) {
  error.value = "";
  deletingItem.value = item;
}

async function deleteItem() {
  if (!deletingItem.value) return;
  saving.value = true;
  try {
    await pagesAdminAPI.delete(deletingItem.value.id);
    deletingItem.value = null;
    await loadItems();
  } catch (e) {
    error.value = adminErrorMessage(e, "Ошибка удаления");
  } finally {
    saving.value = false;
  }
}

onMounted(loadItems);
</script>
