<template>
  <div class="ad-shell">
    <aside
      id="ad-sidebar"
      class="ad-sidebar"
      :class="{ 'is-open': menuOpen }"
      aria-label="Меню админки"
    >
      <div class="ad-brand">
        <span class="ad-brand-mark" aria-hidden="true">NCF</span>
        <span class="ad-brand-name">
          NCF
          <small>Админ-панель</small>
        </span>
        <button
          ref="closeBtn"
          type="button"
          class="ad-icon-btn ad-close-btn"
          aria-label="Закрыть меню"
          @click="closeMenu"
        >
          <AdminIcon name="close" />
        </button>
      </div>

      <nav class="ad-nav">
        <div v-for="group in adminMenu" :key="group.title ?? 'main'" class="ad-nav-group">
          <p v-if="group.title" class="ad-nav-title">{{ group.title }}</p>
          <ul class="ad-nav-list">
            <li v-for="item in group.items" :key="item.path">
              <router-link
                :to="item.path"
                class="ad-nav-link"
                :class="{ 'is-active': isActivePath(item.path, route.path) }"
                :aria-current="isActivePath(item.path, route.path) ? 'page' : undefined"
              >
                <AdminIcon :name="item.icon" />
                <span class="ad-nav-label">{{ item.label }}</span>
                <span
                  v-if="item.badge && counts[item.badge]"
                  class="ad-count"
                  :aria-label="`новых: ${counts[item.badge]}`"
                  >{{ counts[item.badge] }}</span
                >
              </router-link>
            </li>
          </ul>
        </div>
      </nav>

      <div class="ad-sidebar-foot">
        <router-link to="/admin/profile" class="ad-user">
          <span class="ad-avatar" aria-hidden="true">{{ userInitials }}</span>
          <span class="ad-user-text">
            <strong>{{ authStore.fullName || "Администратор" }}</strong>
            <small>Профиль</small>
          </span>
        </router-link>
        <button
          type="button"
          class="ad-icon-btn"
          aria-label="Выйти"
          title="Выйти"
          @click="handleLogout"
        >
          <AdminIcon name="logout" />
        </button>
      </div>
    </aside>

    <div v-if="menuOpen" class="ad-scrim" @click="closeMenu"></div>

    <div class="ad-main">
      <header class="ad-topbar">
        <button
          type="button"
          class="ad-icon-btn ad-menu-btn"
          aria-label="Открыть меню"
          aria-controls="ad-sidebar"
          :aria-expanded="menuOpen"
          @click="openMenu"
        >
          <AdminIcon name="menu" />
        </button>
        <h1 class="ad-title">{{ pageTitle(route.path) }}</h1>
        <a href="/" target="_blank" rel="noopener" class="ad-site-link">
          <AdminIcon name="external" />
          <span>Открыть сайт</span>
        </a>
      </header>

      <main class="ad-content">
        <router-view />
      </main>
      <AdminToasts />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { statsAPI } from "@/api/admin";
import AdminIcon from "./AdminIcon.vue";
import AdminToasts from "./AdminToasts.vue";
import { adminMenu, pageTitle, isActivePath, type BadgeKey } from "./adminMenu";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const menuOpen = ref(false);
const closeBtn = ref<HTMLButtonElement | null>(null);
const counts = reactive<Record<BadgeKey, number>>({ orders: 0, messages: 0 });

const userInitials = computed(() => {
  const user = authStore.user;
  if (!user) return "?";
  const first = user.first_name?.[0] || "";
  const last = user.last_name?.[0] || "";
  if (first && last) return (first + last).toUpperCase();
  return (user.username?.[0] || "?").toUpperCase();
});

function openMenu() {
  menuOpen.value = true;
  document.body.style.overflow = "hidden";
  nextTick(() => closeBtn.value?.focus());
}

function closeMenu() {
  menuOpen.value = false;
  document.body.style.overflow = "";
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === "Escape" && menuOpen.value) closeMenu();
}

async function handleLogout() {
  await authStore.logout();
  router.push("/admin/login");
}

async function loadCounts() {
  try {
    const { data } = await statsAPI.getDashboard();
    counts.orders = data.new_orders_count || 0;
    counts.messages = data.unread_messages || 0;
  } catch {
    // Counters are optional; the menu works without them.
  }
}

watch(
  () => route.path,
  () => {
    closeMenu();
    loadCounts();
  },
);

onMounted(() => {
  document.addEventListener("keydown", onKeydown);
  loadCounts();
});

onUnmounted(() => {
  document.removeEventListener("keydown", onKeydown);
  document.body.style.overflow = "";
});
</script>
