<template>
  <div class="ad-login">
    <div class="ad-login-card">
      <div class="ad-login-brand">
        <span class="ad-brand-mark" aria-hidden="true">NCF</span>
        <span>Админ-панель</span>
      </div>
      <h1 class="ad-login-title">Вход</h1>
      <p class="ad-login-sub">Введите логин и пароль администратора</p>

      <form class="ad-login-form" @submit.prevent="handleLogin">
        <div class="ad-login-field">
          <label for="username">Логин</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            autocomplete="username"
            required
            :disabled="loading"
          />
        </div>

        <div class="ad-login-field">
          <label for="password">Пароль</label>
          <div class="ad-login-password">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              required
              :disabled="loading"
            />
            <button
              type="button"
              class="ad-icon-btn"
              :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
              :aria-pressed="showPassword"
              @click="showPassword = !showPassword"
            >
              <AdminIcon :name="showPassword ? 'eye-off' : 'eye'" />
            </button>
          </div>
        </div>

        <p v-if="error" class="ad-login-error" role="alert">{{ error }}</p>

        <button type="submit" class="ad-login-submit" :disabled="loading">
          {{ loading ? "Входим…" : "Войти" }}
        </button>
      </form>

      <router-link to="/" class="ad-login-back">Вернуться на сайт</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import AdminIcon from "@/components/admin/AdminIcon.vue";
import { ref, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const form = reactive({
  username: "",
  password: "",
});

const showPassword = ref(false);
const loading = ref(false);
const error = ref<string | null>(null);

async function handleLogin() {
  loading.value = true;
  error.value = null;

  const result = await authStore.login(form.username, form.password);

  if (result.success) {
    const redirect = (route.query.redirect as string) || "/admin";
    router.push(redirect);
  } else {
    loading.value = false;
    error.value = result.error || "Ошибка входа";
  }
}
</script>

<!-- Styles in styles/site/ -->
