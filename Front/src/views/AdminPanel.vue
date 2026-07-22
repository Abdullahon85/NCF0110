<template>
  <div class="admin-panel">
    <aside class="admin-sidebar">
      <div class="logo">Admin Panel</div>
      <nav class="admin-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.id"
          :to="item.path"
          :class="['nav-item', { active: currentSection === item.id }]"
        >
          <span class="icon">{{ item.icon }}</span>
          <span class="label">{{ item.label }}</span>
        </router-link>
      </nav>
      <div class="user-info">
        <span>Администратор</span>
        <button @click="logout" class="logout-btn">Выход</button>
      </div>
    </aside>

    <main class="admin-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();

const menuItems = [
  { id: "products", label: "Товары", path: "/admin/products", icon: "📦" },
  {
    id: "categories",
    label: "Каталог",
    path: "/admin/categories",
    icon: "📂",
  },
  { id: "brands", label: "Бренды", path: "/admin/brands", icon: "🏷️" },
  { id: "tags", label: "Теги", path: "/admin/tags", icon: "🔖" },
  {
    id: "features",
    label: "Характеристики",
    path: "/admin/features",
    icon: "⚙️",
  },
  { id: "news", label: "Новости", path: "/admin/news", icon: "📰" },
  { id: "contact", label: "Сообщения", path: "/admin/contact", icon: "💬" },
];

const currentSection = computed(() => {
  const pathParts = route.path.split("/");
  return pathParts[2] || "products";
});

const logout = () => {
  // TODO: Implement logout
  router.push("/");
};
</script>

<!-- Styles in main.css -->
