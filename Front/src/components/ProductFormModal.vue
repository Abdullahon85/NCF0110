<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ isEdit ? "Редактировать товар" : "Добавить товар" }}</h2>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <form @submit.prevent="submitForm" class="product-form">
        <!-- ОСНОВНАЯ ИНФОРМАЦИЯ -->
        <fieldset class="form-fieldset">
          <legend>Основная информация</legend>

          <div class="form-row-2cols">
            <div class="form-group">
              <label>Название *</label>
              <input
                v-model="formData.name"
                type="text"
                placeholder="Название товара"
                required
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label>Slug</label>
              <input
                v-model="formData.slug"
                type="text"
                placeholder="slug-tovara"
                class="form-input"
              />
            </div>
          </div>

          <div class="form-row-2cols">
            <div class="form-group">
              <label>Каталог *</label>
              <select
                v-model.number="formData.category"
                required
                class="form-input"
              >
                <option value="">Выберите каталог</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Бренд</label>
              <select v-model.number="formData.brand" class="form-input">
                <option :value="null">---</option>
                <option
                  v-for="brand in brands"
                  :key="brand.id"
                  :value="brand.id"
                >
                  {{ brand.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Описание *</label>
            <textarea
              v-model="formData.description"
              placeholder="Подробное описание товара"
              required
              rows="4"
              class="form-input"
            />
          </div>
        </fieldset>

        <!-- ЦЕНА И СТАТУС -->
        <fieldset class="form-fieldset">
          <legend>Цена и статус</legend>

          <div class="form-row-2cols">
            <div class="form-group">
              <label>Цена (руб)</label>
              <input
                v-model.number="formData.price"
                type="number"
                step="0.01"
                placeholder="999.99"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label>В наличии</label>
              <div class="checkbox-group">
                <label class="checkbox-label">
                  <input v-model="formData.is_available" type="checkbox" />
                  Товар в наличии
                </label>
              </div>
            </div>
          </div>
        </fieldset>

        <!-- SKU -->
        <fieldset class="form-fieldset">
          <legend>SKU и артикулы</legend>

          <div class="form-row-2cols">
            <div class="form-group">
              <label>Артикул производителя</label>
              <input
                v-model="formData.manufacturer_sku"
                type="text"
                placeholder="Артикул производителя"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label>Внутренний SKU</label>
              <input
                v-model="formData.internal_sku"
                type="text"
                placeholder="Автогенерируется"
                class="form-input"
              />
            </div>
          </div>
        </fieldset>

        <!-- ИЗОБРАЖЕНИЯ -->
        <fieldset class="form-fieldset">
          <legend>Изображения товара</legend>

          <div v-if="formData.images.length > 0" class="inline-table">
            <table>
              <thead>
                <tr>
                  <th>Изображение</th>
                  <th>Главное</th>
                  <th>Порядок</th>
                  <th>Удалить</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(img, idx) in formData.images" :key="idx">
                  <td>
                    <img
                      :src="img.data"
                      :alt="img.name"
                      style="max-width: 100px; max-height: 100px"
                    />
                  </td>
                  <td>
                    <input
                      v-model="img.is_main"
                      type="checkbox"
                      @change="setMainImage(idx)"
                    />
                  </td>
                  <td>
                    <input
                      v-model.number="img.order"
                      type="number"
                      min="0"
                      style="width: 60px"
                    />
                  </td>
                  <td>
                    <button
                      @click.prevent="removeImage(idx)"
                      type="button"
                      class="btn-small btn-danger"
                    >
                      Удалить
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="form-group">
            <input
              ref="fileInputRef"
              type="file"
              multiple
              accept="image/*"
              @change="handleImageUpload"
              class="file-input"
            />
          </div>
          <button
            @click.prevent="triggerFileInput"
            type="button"
            class="btn btn-secondary"
          >
            + Добавить изображение
          </button>
        </fieldset>

        <!-- ХАРАКТЕРИСТИКИ -->
        <fieldset class="form-fieldset">
          <legend>Характеристики товара</legend>

          <!-- Datalists for autocomplete -->
          <datalist id="feature-names-list">
            <option v-for="f in categoryFeatures" :key="f.id" :value="f.name" />
          </datalist>
          <datalist id="feature-values-list">
            <option
              v-for="v in currentFeatureValues"
              :key="v.id"
              :value="v.value"
            />
          </datalist>

          <p v-if="formData.category && categoryFeatures.length > 0" class="hint-text">
            💡 Подсказки для категории активны — начните вводить название
          </p>
          <p v-else-if="!formData.category" class="hint-text muted">
            Выберите каталог, чтобы увидеть подсказки для характеристик
          </p>

          <div v-if="formData.features.length > 0" class="inline-table">
            <table>
              <thead>
                <tr>
                  <th>Характеристика</th>
                  <th>Значение</th>
                  <th>Удалить</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(feat, idx) in formData.features" :key="idx">
                  <td>
                    <input
                      v-model="feat.name"
                      type="text"
                      placeholder="Название характеристики"
                      class="form-input-small"
                      list="feature-names-list"
                      @change="onFeatureNameChange(feat)"
                    />
                  </td>
                  <td>
                    <input
                      v-model="feat.value"
                      type="text"
                      placeholder="Значение"
                      class="form-input-small"
                      :list="'feature-values-' + idx"
                    />
                    <datalist :id="'feature-values-' + idx">
                      <option
                        v-for="v in getValuesForFeature(feat.name)"
                        :key="v.id"
                        :value="v.value"
                      />
                    </datalist>
                  </td>
                  <td>
                    <button
                      @click.prevent="removeFeature(idx)"
                      type="button"
                      class="btn-small btn-danger"
                    >
                      Удалить
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <button
            @click.prevent="addFeature"
            type="button"
            class="btn btn-secondary"
          >
            + Добавить характеристику
          </button>
        </fieldset>

        <!-- КНОПКИ -->
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="submitting">
            {{ submitting ? "Сохранение..." : "Сохранить" }}
          </button>
          <button type="button" @click="$emit('close')" class="btn btn-ghost">
            Отмена
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import type { Product, Category, Brand } from "@/types";
import axios from "axios";

interface Props {
  product?: Product | null;
  categories: Category[];
  brands: Brand[];
}

interface ImageData {
  data: string; // base64
  name: string;
  is_main: boolean;
  order: number;
}

interface FeatureData {
  name: string;
  value: string;
}

interface FormData {
  name: string;
  slug: string;
  description: string;
  category: number | null;
  brand: number | null;
  price: number | null;
  is_available: boolean;
  manufacturer_sku: string;
  internal_sku: string;
  images: ImageData[];
  features: FeatureData[];
}

const props = defineProps<Props>();
const emit = defineEmits(["save", "close"]);

const formData = ref<FormData>({
  name: "",
  slug: "",
  description: "",
  category: null,
  brand: null,
  price: null,
  is_available: true,
  manufacturer_sku: "",
  internal_sku: "",
  images: [],
  features: [],
});

const submitting = ref(false);
const isEdit = computed(() => !!props.product);

// Category-based feature/tag suggestions
interface FeatureSuggestion { id: number; name: string; values: { id: number; value: string }[] }
const categoryFeatures = ref<FeatureSuggestion[]>([]);
const currentFeatureValues = ref<{ id: number; value: string }[]>([]);

const loadCategoryFeatures = async (categoryId: number) => {
  try {
    const baseUrl = import.meta.env.VITE_API_URL || '/api';
    const res = await axios.get(`${baseUrl}/features-tags-by-category/`, { params: { category: categoryId } });
    categoryFeatures.value = res.data.features || [];
  } catch {
    categoryFeatures.value = [];
  }
};

const getValuesForFeature = (featureName: string) => {
  const feat = categoryFeatures.value.find(f => f.name === featureName);
  return feat ? feat.values : [];
};

const onFeatureNameChange = (feat: FeatureData) => {
  currentFeatureValues.value = getValuesForFeature(feat.name);
};

// Функция для преобразования русских символов в латиницу для слага
const generateSlug = (text: string): string => {
  const translitMap: Record<string, string> = {
    а: "a",
    б: "b",
    в: "v",
    г: "g",
    д: "d",
    е: "e",
    ё: "yo",
    ж: "zh",
    з: "z",
    и: "i",
    й: "y",
    к: "k",
    л: "l",
    м: "m",
    н: "n",
    о: "o",
    п: "p",
    р: "r",
    с: "s",
    т: "t",
    у: "u",
    ф: "f",
    х: "h",
    ц: "ts",
    ч: "ch",
    ш: "sh",
    щ: "sch",
    ъ: "",
    ы: "y",
    ь: "",
    э: "e",
    ю: "yu",
    я: "ya",
  };

  return text
    .toLowerCase()
    .split("")
    .map((char) => translitMap[char] || char)
    .join("")
    .replace(/[^\w\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-+|-+$/g, "");
};

const fileInputRef = ref<HTMLInputElement | null>(null);

const triggerFileInput = () => {
  fileInputRef.value?.click();
};

const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  if (!files) return;

  for (let file of Array.from(files)) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const imageData: ImageData = {
        data: e.target?.result as string,
        name: file.name,
        is_main: formData.value.images.length === 0, // первое изображение - главное
        order: formData.value.images.length,
      };
      formData.value.images.push(imageData);
    };
    reader.readAsDataURL(file);
  }

  // Сбросим input
  target.value = "";
};

const removeImage = (index: number) => {
  formData.value.images.splice(index, 1);
  // Переуведем order
  formData.value.images.forEach((img, idx) => {
    img.order = idx;
  });
};

const setMainImage = (index: number) => {
  formData.value.images.forEach((img, idx) => {
    img.is_main = idx === index;
  });
};

const addFeature = () => {
  formData.value.features.push({
    name: "",
    value: "",
  });
};

const removeFeature = (index: number) => {
  formData.value.features.splice(index, 1);
};

const submitForm = async () => {
  submitting.value = true;
  try {
    // Преобразуем данные для отправки на сервер
    const data = {
      name: formData.value.name,
      slug: formData.value.slug,
      description: formData.value.description,
      category_id: formData.value.category,
      brand_id: formData.value.brand || null,
      price: formData.value.price,
      is_available: formData.value.is_available,
      manufacturer_sku: formData.value.manufacturer_sku,
      internal_sku: formData.value.internal_sku,
    };

    emit("save", {
      ...data,
      images: formData.value.images,
      features: formData.value.features,
    });
  } finally {
    submitting.value = false;
  }
};

onMounted(() => {
  if (props.product) {
    formData.value = {
      name: props.product.name,
      slug: props.product.slug,
      description: props.product.description || "",
      category:
        typeof props.product.category === "number"
          ? props.product.category
          : props.product.category?.id || null,
      brand: props.product.brand
        ? typeof props.product.brand === "number"
          ? props.product.brand
          : (props.product.brand as any)?.id || null
        : null,
      price: props.product.price,
      is_available: props.product.is_available,
      manufacturer_sku: (props.product.manufacturer_sku as string) || "",
      internal_sku: (props.product.internal_sku as string) || "",
      images: [],
      features: [],
    };
  }
});

// Watch на изменение имени для автоматического генерирования слага
watch(
  () => formData.value.name,
  (newName) => {
    if (!isEdit.value && newName) {
      formData.value.slug = generateSlug(newName);
    }
  }
);

// Watch на изменение категории — загружаем подсказки
watch(
  () => formData.value.category,
  (catId) => {
    if (catId) {
      loadCategoryFeatures(catId);
    } else {
      categoryFeatures.value = [];
    }
  }
);
</script>

<!-- Styles in main.css -->
