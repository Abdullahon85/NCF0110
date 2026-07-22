<template>
  <div class="management-page settings-page">
    <div class="page-header">
      <h1>⚙️ Настройки сайта</h1>
    </div>

    <div class="settings-grid">
      <!-- About Section -->
      <div class="settings-card">
        <div class="card-header">
          <h2>📄 О компании</h2>
        </div>
        <form @submit.prevent="saveAbout" class="card-body">
          <div class="form-group">
            <label>Заголовок *</label>
            <input v-model="about.title" type="text" required />
          </div>
          <div class="form-group">
            <label>Содержание *</label>
            <textarea v-model="about.content" rows="6" required></textarea>
          </div>
          <div class="form-group">
            <label>Ссылка на изображение</label>
            <input v-model="about.image" type="url" placeholder="https://..." />
            <img
              v-if="about.image"
              :src="about.image"
              class="preview-image"
              alt="Preview"
            />
          </div>
          <div v-if="aboutError" class="error-msg">{{ aboutError }}</div>
          <div v-if="aboutSuccess" class="success-msg">✓ Сохранено</div>
          <div class="card-actions">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="savingAbout"
            >
              {{ savingAbout ? "Сохранение..." : "Сохранить" }}
            </button>
          </div>
        </form>
      </div>

      <!-- Contact Section -->
      <div class="settings-card">
        <div class="card-header">
          <h2>📞 Контактная информация</h2>
        </div>
        <form @submit.prevent="saveContact" class="card-body">
          <div class="form-group">
            <label>Телефон *</label>
            <input
              v-model="contact.phone"
              type="tel"
              required
              placeholder="+7 (XXX) XXX-XX-XX"
            />
          </div>
          <div class="form-group">
            <label>Email *</label>
            <input v-model="contact.email" type="email" required />
          </div>
          <div class="form-group">
            <label>Адрес *</label>
            <textarea v-model="contact.address" rows="2" required></textarea>
          </div>
          <div class="form-group">
            <label>Ссылка на карту (Yandex/Google Maps)</label>
            <input
              v-model="contact.map_url"
              type="url"
              placeholder="https://..."
            />
          </div>
          <div class="form-group">
            <label>Режим работы</label>
            <input
              v-model="contact.working_hours"
              type="text"
              placeholder="Пн-Пт: 9:00-18:00"
            />
          </div>
          <div v-if="contactError" class="error-msg">{{ contactError }}</div>
          <div v-if="contactSuccess" class="success-msg">✓ Сохранено</div>
          <div class="card-actions">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="savingContact"
            >
              {{ savingContact ? "Сохранение..." : "Сохранить" }}
            </button>
          </div>
        </form>
      </div>

      <!-- Social Links -->
      <div class="settings-card">
        <div class="card-header">
          <h2>🔗 Социальные сети</h2>
        </div>
        <form @submit.prevent="saveSocial" class="card-body">
          <div class="form-group">
            <label>Instagram</label>
            <input
              v-model="social.instagram"
              type="url"
              placeholder="https://instagram.com/..."
            />
          </div>
          <div class="form-group">
            <label>Telegram</label>
            <input
              v-model="social.telegram"
              type="url"
              placeholder="https://t.me/..."
            />
          </div>
          <div class="form-group">
            <label>WhatsApp</label>
            <input
              v-model="social.whatsapp"
              type="url"
              placeholder="https://wa.me/..."
            />
          </div>
          <div class="form-group">
            <label>Facebook</label>
            <input
              v-model="social.facebook"
              type="url"
              placeholder="https://facebook.com/..."
            />
          </div>
          <div v-if="socialError" class="error-msg">{{ socialError }}</div>
          <div v-if="socialSuccess" class="success-msg">✓ Сохранено</div>
          <div class="card-actions">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="savingSocial"
            >
              {{ savingSocial ? "Сохранение..." : "Сохранить" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { settingsAdminAPI } from "@/api/admin";

const about = reactive({
  title: "",
  content: "",
  image: "",
});
const savingAbout = ref(false);
const aboutError = ref("");
const aboutSuccess = ref(false);

const contact = reactive({
  phone: "",
  email: "",
  address: "",
  map_url: "",
  working_hours: "",
});
const savingContact = ref(false);
const contactError = ref("");
const contactSuccess = ref(false);

const social = reactive({
  instagram: "",
  telegram: "",
  whatsapp: "",
  facebook: "",
});
const savingSocial = ref(false);
const socialError = ref("");
const socialSuccess = ref(false);

async function loadSettings() {
  try {
    const [aboutRes, contactRes] = await Promise.all([
      settingsAdminAPI.getAbout(),
      settingsAdminAPI.getContact(),
    ]);
    if (aboutRes.data) {
      about.title = aboutRes.data.title || "";
      about.content = aboutRes.data.content || "";
      about.image = aboutRes.data.image || "";
    }
    if (contactRes.data) {
      contact.phone = contactRes.data.phone || "";
      contact.email = contactRes.data.email || "";
      contact.address = contactRes.data.address || "";
      contact.map_url = contactRes.data.map_url || "";
      contact.working_hours = contactRes.data.working_hours || "";
      // Social links from contact
      social.instagram = contactRes.data.instagram || "";
      social.telegram = contactRes.data.telegram || "";
      social.whatsapp = contactRes.data.whatsapp || "";
      social.facebook = contactRes.data.facebook || "";
    }
  } catch (e) {
    console.error(e);
  }
}

async function saveAbout() {
  try {
    savingAbout.value = true;
    aboutError.value = "";
    aboutSuccess.value = false;
    await settingsAdminAPI.updateAbout(about);
    aboutSuccess.value = true;
    setTimeout(() => (aboutSuccess.value = false), 2000);
  } catch (e: any) {
    aboutError.value = e.response?.data?.detail || "Ошибка сохранения";
  } finally {
    savingAbout.value = false;
  }
}

async function saveContact() {
  try {
    savingContact.value = true;
    contactError.value = "";
    contactSuccess.value = false;
    await settingsAdminAPI.updateContact(contact);
    contactSuccess.value = true;
    setTimeout(() => (contactSuccess.value = false), 2000);
  } catch (e: any) {
    contactError.value = e.response?.data?.detail || "Ошибка сохранения";
  } finally {
    savingContact.value = false;
  }
}

async function saveSocial() {
  try {
    savingSocial.value = true;
    socialError.value = "";
    socialSuccess.value = false;
    await settingsAdminAPI.patchContact(social);
    socialSuccess.value = true;
    setTimeout(() => (socialSuccess.value = false), 2000);
  } catch (e: any) {
    socialError.value = e.response?.data?.detail || "Ошибка сохранения";
  } finally {
    savingSocial.value = false;
  }
}

onMounted(loadSettings);
</script>

<!-- Styles in main.css -->
