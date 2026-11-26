<template>
  <div class="contact-page">
    <div class="container">
      <h1>Контакты</h1>

      <div class="contact-layout">
        <div class="contact-info-section">
          <h2>Свяжитесь с нами</h2>

          <div v-if="loadingInfo" class="loading-container">
            <div class="loading-spinner"></div>
          </div>

          <div v-else-if="error" class="error-container">
            <p>{{ error }}</p>
            <button class="btn-retry" @click="loadContactInfo">Попробовать снова</button>
          </div>

          <div v-else-if="contactInfo" class="contact-details">
            <div class="contact-item">
              <span class="icon">📞</span>
              <div>
                <strong>Телефон:</strong>
                <p>{{ contactInfo.phone }}</p>
              </div>
            </div>

            <div class="contact-item">
              <span class="icon">✉️</span>
              <div>
                <strong>Email:</strong>
                <p>{{ contactInfo.email }}</p>
              </div>
            </div>

            <div class="contact-item">
              <span class="icon">📍</span>
              <div>
                <strong>Адрес:</strong>
                <p>{{ contactInfo.address }}</p>
              </div>
            </div>

            <div v-if="contactInfo.map_url" class="map-container">
              <a
                :href="contactInfo.map_url"
                target="_blank"
                rel="noopener noreferrer"
                class="map-link"
              >
                Открыть на карте →
              </a>
            </div>
          </div>
        </div>

        <div class="contact-form-section">
          <h2>Напишите нам</h2>
          <p>Заполните форму ниже, и мы свяжемся с вами в ближайшее время</p>
          <ContactFormComponent />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { contactAPI } from "@/api";
import ContactFormComponent from "@/components/ContactFormComponent.vue";
import type { ContactInfo } from "@/types";

const contactInfo = ref<ContactInfo | null>(null);
const loadingInfo = ref(true);
const error = ref<string | null>(null);

const loadContactInfo = async () => {
  loadingInfo.value = true;
  error.value = null;

  try {
    const response = await contactAPI.getInfo();
    contactInfo.value = response.data;
  } catch (err) {
    console.error("Failed to load contact info:", err);
    error.value =
      "Произошла ошибка при загрузке контактной информации. Пожалуйста, попробуйте позже.";
  } finally {
    loadingInfo.value = false;
  }
};

onMounted(() => {
  loadContactInfo();
});
</script>

<style scoped src="@/styles/views/ContactPage.css"></style>
