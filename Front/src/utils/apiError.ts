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
