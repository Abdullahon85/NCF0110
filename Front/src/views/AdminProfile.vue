<template>
  <div class="profile-page">
    <!-- Profile Info -->
    <div class="card">
      <div class="card-header">
        <h2>👤 Профиль пользователя</h2>
      </div>
      <div class="card-body">
        <form @submit.prevent="saveProfile" class="profile-form">
          <div class="form-row">
            <div class="form-group">
              <label>Логин</label>
              <input
                type="text"
                :value="authStore.user?.username"
                disabled
                class="input-disabled"
              />
              <span class="hint">Логин нельзя изменить</span>
            </div>

            <div class="form-group">
              <label>Email</label>
              <input
                v-model="profileForm.email"
                type="email"
                placeholder="Введите email"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Имя</label>
              <input
                v-model="profileForm.first_name"
                type="text"
                placeholder="Введите имя"
              />
            </div>

            <div class="form-group">
              <label>Фамилия</label>
              <input
                v-model="profileForm.last_name"
                type="text"
                placeholder="Введите фамилию"
              />
            </div>
          </div>

          <div
            v-if="profileMessage"
            :class="['message', profileSuccess ? 'success' : 'error']"
          >
            {{ profileMessage }}
          </div>

          <div class="form-actions">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="savingProfile"
            >
              {{ savingProfile ? "Сохранение..." : "Сохранить профиль" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Change Password -->
    <div class="card">
      <div class="card-header">
        <h2>🔐 Смена пароля</h2>
      </div>
      <div class="card-body">
        <form @submit.prevent="changePassword" class="password-form">
          <div class="form-group">
            <label>Текущий пароль</label>
            <div class="password-input">
              <input
                v-model="passwordForm.oldPassword"
                :type="showOldPassword ? 'text' : 'password'"
                placeholder="Введите текущий пароль"
                autocomplete="current-password"
                required
              />
              <button
                type="button"
                class="toggle-btn"
                @click="showOldPassword = !showOldPassword"
              >
                {{ showOldPassword ? "👁️" : "👁️‍🗨️" }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>Новый пароль</label>
            <div class="password-input">
              <input
                v-model="passwordForm.newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                placeholder="Введите новый пароль"
                autocomplete="new-password"
                required
                minlength="8"
              />
              <button
                type="button"
                class="toggle-btn"
                @click="showNewPassword = !showNewPassword"
              >
                {{ showNewPassword ? "👁️" : "👁️‍🗨️" }}
              </button>
            </div>
            <span class="hint">Минимум 8 символов</span>
          </div>

          <div class="form-group">
            <label>Подтверждение пароля</label>
            <div class="password-input">
              <input
                v-model="passwordForm.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="Повторите новый пароль"
                autocomplete="new-password"
                required
              />
              <button
                type="button"
                class="toggle-btn"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                {{ showConfirmPassword ? "👁️" : "👁️‍🗨️" }}
              </button>
            </div>
          </div>

          <div v-if="passwordForm.newPassword" class="password-strength">
            <div class="strength-label">Надежность пароля:</div>
            <div class="strength-bar">
              <div
                class="strength-fill"
                :style="{ width: passwordStrength.percent + '%' }"
                :class="passwordStrength.class"
              ></div>
            </div>
            <span :class="['strength-text', passwordStrength.class]">
              {{ passwordStrength.text }}
            </span>
          </div>

          <div
            v-if="passwordMessage"
            :class="['message', passwordSuccess ? 'success' : 'error']"
          >
            {{ passwordMessage }}
          </div>

          <div class="form-actions">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="changingPassword"
            >
              {{ changingPassword ? "Изменение..." : "Изменить пароль" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Account Info -->
    <div class="card">
      <div class="card-header">
        <h2>ℹ️ Информация об аккаунте</h2>
      </div>
      <div class="card-body">
        <div class="info-list">
          <div class="info-item">
            <span class="info-label">Роль:</span>
            <span class="info-value">
              <span
                class="badge"
                :class="
                  authStore.user?.is_superuser
                    ? 'badge-danger'
                    : 'badge-primary'
                "
              >
                {{
                  authStore.user?.is_superuser ? "Суперадмин" : "Администратор"
                }}
              </span>
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">Дата регистрации:</span>
            <span class="info-value">{{
              formatDate(authStore.user?.date_joined)
            }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Последний вход:</span>
            <span class="info-value">{{
              formatDate(authStore.user?.last_login)
            }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from "vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

// Profile form
const profileForm = reactive({
  email: authStore.user?.email || "",
  first_name: authStore.user?.first_name || "",
  last_name: authStore.user?.last_name || "",
});

const savingProfile = ref(false);
const profileMessage = ref("");
const profileSuccess = ref(false);

// Password form
const passwordForm = reactive({
  oldPassword: "",
  newPassword: "",
  confirmPassword: "",
});

const showOldPassword = ref(false);
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);
const changingPassword = ref(false);
const passwordMessage = ref("");
const passwordSuccess = ref(false);

// Watch for user changes
watch(
  () => authStore.user,
  (user) => {
    if (user) {
      profileForm.email = user.email || "";
      profileForm.first_name = user.first_name || "";
      profileForm.last_name = user.last_name || "";
    }
  },
  { immediate: true },
);

// Password strength
const passwordStrength = computed(() => {
  const password = passwordForm.newPassword;
  if (!password) return { percent: 0, text: "", class: "" };

  let score = 0;

  if (password.length >= 8) score += 25;
  if (password.length >= 12) score += 15;
  if (/[a-z]/.test(password)) score += 15;
  if (/[A-Z]/.test(password)) score += 15;
  if (/[0-9]/.test(password)) score += 15;
  if (/[^a-zA-Z0-9]/.test(password)) score += 15;

  if (score < 40) return { percent: score, text: "Слабый", class: "weak" };
  if (score < 70) return { percent: score, text: "Средний", class: "medium" };
  return { percent: score, text: "Сильный", class: "strong" };
});

async function saveProfile() {
  savingProfile.value = true;
  profileMessage.value = "";

  const result = await authStore.updateProfile({
    email: profileForm.email,
    first_name: profileForm.first_name,
    last_name: profileForm.last_name,
  });

  savingProfile.value = false;
  profileSuccess.value = result.success;
  profileMessage.value = result.success
    ? "Профиль успешно обновлен!"
    : result.error || "Ошибка";

  if (result.success) {
    setTimeout(() => {
      profileMessage.value = "";
    }, 2000);
  }
}

async function changePassword() {
  // Validation
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordMessage.value = "Пароли не совпадают";
    passwordSuccess.value = false;
    return;
  }

  if (passwordForm.newPassword.length < 8) {
    passwordMessage.value = "Пароль должен быть минимум 8 символов";
    passwordSuccess.value = false;
    return;
  }

  changingPassword.value = true;
  passwordMessage.value = "";

  const result = await authStore.changePassword(
    passwordForm.oldPassword,
    passwordForm.newPassword,
  );

  changingPassword.value = false;
  passwordSuccess.value = result.success;
  passwordMessage.value = result.success
    ? "Пароль успешно изменен!"
    : result.error || "Ошибка";

  if (result.success) {
    passwordForm.oldPassword = "";
    passwordForm.newPassword = "";
    passwordForm.confirmPassword = "";
    setTimeout(() => {
      passwordMessage.value = "";
    }, 2000);
  }
}

function formatDate(dateString?: string): string {
  if (!dateString) return "—";
  const date = new Date(dateString);
  return date.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>

<!-- Styles in main.css -->
