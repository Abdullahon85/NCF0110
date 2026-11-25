// Human-readable message for a failed public form submission (order, review, question).
export function describeSubmitError(error: any, fallback: string): string {
  const status: number | undefined = error?.response?.status;
  const data = error?.response?.data;

  if (status === 429) {
    return "Слишком много отправок с вашего адреса. Пожалуйста, попробуйте позже.";
  }
  if (status === 404) {
    return "Товар не найден. Обновите страницу.";
  }
  if (status === 400 && data && typeof data === "object") {
    if (data.items) {
      return "Один из товаров больше недоступен или указано неверное количество. Обновите корзину и попробуйте снова.";
    }
    if (typeof data.detail === "string") return data.detail;
    for (const value of Object.values(data)) {
      const first = Array.isArray(value) ? value[0] : value;
      if (typeof first === "string") return first;
    }
  }
  return fallback;
}

// Labels for the field names the admin API reports errors on.
const FIELD_LABELS: Record<string, string> = {
  name: "Название",
  title: "Заголовок",
  slug: "Адрес (slug)",
  category: "Каталог",
  parent: "Родительский каталог",
  brand: "Бренд",
  price: "Цена",
  description: "Описание",
  content: "Текст",
  preview: "Краткое описание",
  image: "Изображение",
  logo: "Логотип",
  link: "Ссылка",
  email: "Email",
  phone: "Телефон",
  address: "Адрес",
  map_url: "Ссылка на карту",
  instagram: "Instagram",
  telegram: "Telegram",
  whatsapp: "WhatsApp",
  facebook: "Facebook",
  value: "Значение",
  status: "Статус",
  old_password: "Текущий пароль",
  new_password: "Новый пароль",
  features: "Характеристики",
  tag_groups: "Группы тегов",
};

// First human-readable message in a DRF error body (strings, lists, nested objects).
function firstMessage(value: unknown): string | null {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) {
    for (const item of value) {
      const found = firstMessage(item);
      if (found) return found;
    }
    return null;
  }
  if (value && typeof value === "object") {
    for (const item of Object.values(value)) {
      const found = firstMessage(item);
      if (found) return found;
    }
  }
  return null;
}

// Message for a failed admin action: the server's explanation, the first field
// error with a russian label, or the fallback when there is no readable body.
export function adminErrorMessage(error: unknown, fallback: string): string {
  const data = (error as any)?.response?.data;
  if (!data || typeof data !== "object") return fallback;
  if (typeof data.detail === "string") return data.detail;
  if (typeof data.error === "string") return data.error;
  for (const [field, value] of Object.entries(data)) {
    const message = firstMessage(value);
    if (!message) continue;
    const label = FIELD_LABELS[field];
    return label ? `${label}: ${message}` : message;
  }
  return fallback;
}
