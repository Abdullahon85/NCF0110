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
            <button @click="loadContactInfo" class="btn-retry">
              Попробовать снова
            </button>
          </div>

          <div v-else-if="contactInfo" class="contact-details">
            <div class="contact-item">
              <span class="icon">📞</span>
              <div>
                <strong>Телефон:</strong>
                <p>{{
                  contactInfo.phone
                }}</p>
              </div>
            </div>

            <div class="contact-item">
              <span class="icon">✉️</span>
              <div>
                <strong>Email:</strong>
                <p>{{
                  contactInfo.email
                }}</p>
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

<style scoped>
.contact-page {
  min-height: calc(100vh - 200px);
  padding: var(--space-8, 2rem) 0;
}

.contact-page h1 {
  font-size: clamp(1.75rem, 5vw, 2.5rem);
  font-weight: 700;
  margin-bottom: var(--space-8, 2rem);
  color: var(--gray-900, #1a1a1a);
}

.contact-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-8, 2rem);
}

@media (min-width: 768px) {
  .contact-layout {
    grid-template-columns: 1fr 1fr;
    gap: var(--space-12, 3rem);
  }
}

.contact-info-section,
.contact-form-section {
  background: var(--white, #fff);
  border-radius: var(--radius-xl, 12px);
  padding: var(--space-8, 2rem);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.contact-info-section h2,
.contact-form-section h2 {
  font-size: clamp(1.25rem, 3vw, 1.75rem);
  font-weight: 600;
  margin-bottom: var(--space-6, 1.5rem);
  color: var(--gray-900, #1a1a1a);
}

.contact-form-section p {
  color: var(--gray-600, #6b7280);
  margin-bottom: var(--space-6, 1.5rem);
  line-height: 1.6;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-12, 3rem) 0;
}

.contact-details {
  display: flex;
  flex-direction: column;
  gap: var(--space-6, 1.5rem);
}

.contact-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4, 1rem);
  padding: var(--space-4, 1rem);
  border-radius: var(--radius-lg, 8px);
  transition: background-color 0.2s ease;
}

.contact-item:hover {
  background: var(--gray-50, #f9fafb);
}

.contact-item .icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  line-height: 1;
}

.contact-item strong {
  display: block;
  font-weight: 600;
  color: var(--gray-900, #1a1a1a);
  margin-bottom: var(--space-1, 0.25rem);
}

.contact-item a {
  color: var(--primary, #2c5aa0);
  text-decoration: none;
  transition: color 0.2s ease;
  word-break: break-all;
}

.contact-item a:hover {
  color: var(--primary-dark, #1e3c70);
  text-decoration: underline;
}

.contact-item p {
  color: var(--gray-700, #374151);
  margin: 0;
  line-height: 1.6;
}

.map-container {
  margin-top: var(--space-6, 1.5rem);
  padding-top: var(--space-6, 1.5rem);
  border-top: 1px solid var(--gray-200, #e5e7eb);
}

.map-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2, 0.5rem);
  padding: var(--space-3, 0.75rem) var(--space-6, 1.5rem);
  background: var(--primary, #2c5aa0);
  color: white;
  text-decoration: none;
  border-radius: var(--radius-lg, 8px);
  font-weight: 500;
  transition:
    background-color 0.2s ease,
    transform 0.2s ease;
}

.map-link:hover {
  background: var(--primary-dark, #1e3c70);
  transform: translateY(-2px);
}

.error-container {
  padding: var(--space-8, 2rem);
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-lg, 8px);
  text-align: center;
}

.error-container p {
  color: #dc2626;
  margin-bottom: var(--space-4, 1rem);
  font-weight: 500;
}

.btn-retry {
  padding: var(--space-3, 0.75rem) var(--space-6, 1.5rem);
  background: var(--primary, #2c5aa0);
  color: white;
  border: none;
  border-radius: var(--radius-lg, 8px);
  font-weight: 500;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    transform 0.2s ease;
}

.btn-retry:hover {
  background: var(--primary-dark, #1e3c70);
  transform: translateY(-2px);
}

.btn-retry:active {
  transform: translateY(0);
}

</style>
