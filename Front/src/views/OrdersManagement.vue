<template>
  <div class="management-page">
    <div class="page-header">
      <h1>🛒 Заявки</h1>
      <span class="messages-count">{{ newCount }} новых</span>
    </div>

    <!-- Фильтры -->
    <div class="filters-bar">
      <input
        v-model="search"
        type="text"
        placeholder="🔍 Имя, телефон, email..."
        class="search-input"
        @input="debouncedSearch"
      />
      <select v-model="statusFilter" @change="loadOrders" class="filter-select">
        <option value="">Все статусы</option>
        <option value="new">Новые</option>
        <option value="processing">В обработке</option>
        <option value="completed">Выполненные</option>
        <option value="cancelled">Отменённые</option>
        <option value="wrong_phone">Неправильный номер</option>
        <option value="no_answer">Не поднял трубку</option>
      </select>
      <input
        v-model="dateFrom"
        type="date"
        class="filter-date"
        title="Дата от"
        @change="loadOrders"
      />
      <input
        v-model="dateTo"
        type="date"
        class="filter-date"
        title="Дата до"
        @change="loadOrders"
      />
      <button class="btn-export" @click="exportCsv" :disabled="exporting" title="Скачать CSV">
        <span v-if="exporting">⏳</span>
        <span v-else>⬇️ CSV</span>
      </button>
    </div>

    <!-- Загрузка / ошибка -->
    <div v-if="loading" class="loading-state">Загрузка...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>

    <!-- Таблица -->
    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Заказчик</th>
            <th>Телефон</th>
            <th>Позиций</th>
            <th>Дата</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="orders.length === 0">
            <td colspan="7" class="empty-row">Заявок не найдено</td>
          </tr>
          <template v-for="order in orders" :key="order.id">
            <!-- Строка заявки -->
            <tr
              class="order-row"
              :class="{
                'order-row--new': order.status === 'new',
                'order-row--expanded': expanded === order.id,
              }"
              @click="toggleExpand(order.id)"
            >
              <td>#{{ order.id }}</td>
              <td>
                <div class="order-customer">
                  <strong>{{ order.customer_name }}</strong>
                  <span v-if="order.customer_email" class="order-email">{{
                    order.customer_email
                  }}</span>
                </div>
              </td>
              <td>
                <a
                  :href="'tel:' + order.customer_phone"
                  class="order-phone"
                  @click.stop
                >
                  {{ order.customer_phone }}
                </a>
              </td>
              <td>
                <span class="order-items-count"
                  >{{ order.items?.length ?? 0 }} поз.</span
                >
              </td>
              <td class="order-date">{{ formatDate(order.created_at) }}</td>
              <td @click.stop>
                <select
                  :value="order.status"
                  @change="
                    (e) =>
                      updateStatus(order, (e.target as HTMLSelectElement).value)
                  "
                  class="status-select"
                  :class="'status-' + order.status"
                >
                  <option value="new">Новый</option>
                  <option value="processing">В обработке</option>
                  <option value="completed">Выполнен</option>
                  <option value="cancelled">Отменён</option>
                  <option value="wrong_phone">Неправильный номер</option>
                  <option value="no_answer">Не поднял трубку</option>
                </select>
              </td>
              <td @click.stop>
                <button
                  class="action-btn delete"
                  title="Удалить"
                  @click="confirmDelete(order)"
                >
                  🗑️
                </button>
              </td>
            </tr>

            <!-- Развёрнутые позиции -->
            <tr v-if="expanded === order.id" class="order-details-row">
              <td colspan="7">
                <div class="order-details">
                  <div v-if="order.customer_telegram" class="order-comment">
                    <strong>Telegram:</strong>
                    <a :href="'https://t.me/' + order.customer_telegram.replace('@','')" target="_blank" class="order-tg-link">{{ order.customer_telegram }}</a>
                  </div>
                  <div v-if="order.comment" class="order-comment">
                    <strong>Комментарий:</strong> {{ order.comment }}
                  </div>
                  <table class="order-items-table">
                    <thead>
                      <tr>
                        <th>Товар</th>
                        <th>Артикул</th>
                        <th>Цена</th>
                        <th>Кол-во</th>
                        <th>Итого</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, i) in order.items" :key="i">
                        <td>{{ item.product_name }}</td>
                        <td class="text-muted">
                          {{ item.product_sku || "—" }}
                        </td>
                        <td>
                          {{
                            item.price ? formatPrice(item.price) : "По запросу"
                          }}
                        </td>
                        <td>{{ item.quantity }}</td>
                        <td>
                          {{
                            item.price
                              ? formatPrice(item.price * item.quantity)
                              : "—"
                          }}
                        </td>
                      </tr>
                    </tbody>
                    <tfoot v-if="hasTotal(order)">
                      <tr>
                        <td colspan="4" class="text-right">
                          <strong>Сумма:</strong>
                        </td>
                        <td>
                          <strong>{{ formatPrice(calcTotal(order)) }}</strong>
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Пагинация -->
    <div v-if="totalPages > 1" class="pagination">
      <button :disabled="page <= 1" @click="goPage(page - 1)" class="page-btn">
        ←
      </button>
      <span class="page-info">{{ page }} / {{ totalPages }}</span>
      <button
        :disabled="page >= totalPages"
        @click="goPage(page + 1)"
        class="page-btn"
      >
        →
      </button>
    </div>

    <!-- Диалог подтверждения удаления -->
    <div
      v-if="deleteTarget"
      class="modal-overlay"
      @click.self="deleteTarget = null"
    >
      <div class="modal-box">
        <h3>Удалить заявку #{{ deleteTarget.id }}?</h3>
        <p>
          «{{ deleteTarget.customer_name }}» — {{ deleteTarget.customer_phone }}
        </p>
        <div class="modal-actions">
          <button class="btn-danger" @click="doDelete">Удалить</button>
          <button class="btn-cancel" @click="deleteTarget = null">
            Отмена
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { ordersAdminAPI } from "@/api/admin";
import axios from "axios";

interface OrderItemData {
  product_name: string;
  product_sku: string;
  price: number | null;
  quantity: number;
}

interface OrderData {
  id: number;
  customer_name: string;
  customer_phone: string;
  customer_email: string;
  customer_telegram: string;
  comment: string;
  status: string;
  created_at: string;
  items: OrderItemData[];
}

const orders = ref<OrderData[]>([]);
const loading = ref(false);
const error = ref("");
const search = ref("");
const statusFilter = ref("");
const dateFrom = ref("");
const dateTo = ref("");
const page = ref(1);
const pageSize = 20;
const total = ref(0);
const expanded = ref<number | null>(null);
const deleteTarget = ref<OrderData | null>(null);
const exporting = ref(false);

const totalPages = computed(() => Math.ceil(total.value / pageSize));
const newCount = computed(
  () => orders.value.filter((o) => o.status === "new").length,
);

let searchTimer: ReturnType<typeof setTimeout>;
const debouncedSearch = () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    page.value = 1;
    loadOrders();
  }, 350);
};

const loadOrders = async () => {
  loading.value = true;
  error.value = "";
  try {
    const res = await ordersAdminAPI.getAll({
      search: search.value || undefined,
      status: statusFilter.value || undefined,
      date_from: dateFrom.value || undefined,
      date_to: dateTo.value || undefined,
      page: page.value,
      page_size: pageSize,
    });
    const data = res.data as any;
    orders.value = data.results ?? data;
    total.value = data.count ?? orders.value.length;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Ошибка загрузки";
  } finally {
    loading.value = false;
  }
};

const exportCsv = async () => {
  exporting.value = true;
  try {
    const baseUrl = import.meta.env.VITE_API_URL || "/api";
    const token = sessionStorage.getItem("admin_token");
    const params = new URLSearchParams();
    if (search.value) params.set("search", search.value);
    if (statusFilter.value) params.set("status", statusFilter.value);
    if (dateFrom.value) params.set("date_from", dateFrom.value);
    if (dateTo.value) params.set("date_to", dateTo.value);
    const url = `${baseUrl}/admin/orders/export-csv/?${params.toString()}`;
    const res = await axios.get(url, {
      responseType: "blob",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    const blob = new Blob([res.data], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    const date = new Date().toLocaleDateString("ru-RU").replace(/\./g, "-");
    link.download = `orders_${date}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
  } catch {
    alert("Ошибка экспорта");
  } finally {
    exporting.value = false;
  }
};

const goPage = (p: number) => {
  page.value = p;
  loadOrders();
};

const toggleExpand = (id: number) => {
  expanded.value = expanded.value === id ? null : id;
};

const updateStatus = async (order: OrderData, newStatus: string) => {
  const prev = order.status;
  order.status = newStatus;
  try {
    await ordersAdminAPI.updateStatus(order.id, newStatus);
  } catch {
    order.status = prev;
  }
};

const confirmDelete = (order: OrderData) => {
  deleteTarget.value = order;
};

const doDelete = async () => {
  if (!deleteTarget.value) return;
  const targetId = deleteTarget.value.id;
  try {
    await ordersAdminAPI.delete(targetId);
    orders.value = orders.value.filter((o) => o.id !== targetId);
    total.value--;
    if (expanded.value === targetId) expanded.value = null;
    deleteTarget.value = null;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Ошибка удаления";
    deleteTarget.value = null;
  }
};

const hasTotal = (order: OrderData) =>
  order.items?.some((i) => i.price != null);

const calcTotal = (order: OrderData) =>
  order.items?.reduce((s, i) => s + (i.price ?? 0) * i.quantity, 0) ?? 0;

const formatPrice = (price: number) =>
  new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "UZS",
    minimumFractionDigits: 0,
  }).format(price);

const formatDate = (dt: string) => {
  if (!dt) return "—";
  return new Date(dt).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

onMounted(loadOrders);
</script>

<!-- Styles in admin-common.css / main.css -->
