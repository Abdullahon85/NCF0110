<template>
  <form @submit.prevent="handleSubmit" class="contact-form">
    <div class="form-group">
      <label for="name">Имя *</label>
      <input
        id="name"
        v-model="formData.name"
        type="text"
        required
        :disabled="loading"
      />
    </div>

    <div class="form-group">
      <label for="email">Email *</label>
      <input
        id="email"
        v-model="formData.email"
        type="email"
        required
        :disabled="loading"
      />
    </div>

    <div class="form-group">
      <label for="message">Сообщение *</label>
      <textarea
        id="message"
        v-model="formData.message"
        rows="5"
        required
        :disabled="loading"
      ></textarea>
    </div>

    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>

    <div v-if="errorMessage" class="alert alert-error">
      {{ errorMessage }}
    </div>

    <button type="submit" :disabled="loading" class="submit-btn">
      {{ loading ? "Отправка..." : "Отправить" }}
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { contactAPI } from "@/api";
import type { ContactMessage } from "@/types";

const formData = reactive<ContactMessage>({
  name: "",
  email: "",
  message: "",
});

const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");

const handleSubmit = async () => {
  loading.value = true;
  successMessage.value = "";
  errorMessage.value = "";

  try {
    await contactAPI.sendMessage(formData);
    successMessage.value = "Ваше сообщение успешно отправлено!";

    // Очистка формы
    formData.name = "";
    formData.email = "";
    formData.message = "";
  } catch (error) {
    errorMessage.value =
      "Произошла ошибка при отправке сообщения. Попробуйте позже.";
  } finally {
    loading.value = false;
  }
};
</script>

<!-- Styles in main.css -->
