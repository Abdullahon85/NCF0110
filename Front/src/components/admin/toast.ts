// Short messages in the corner of the admin panel instead of blocking browser pop-ups:
// they do not block the page and hide by themselves after a few seconds.
import { ref } from "vue";

export type Toast = { id: number; text: string; tone: "success" | "error" };

export const TOAST_MS = 5000;
export const toasts = ref<Toast[]>([]);
let nextId = 1;

export function dismiss(id: number) {
  toasts.value = toasts.value.filter((t) => t.id !== id);
}

function show(text: string, tone: Toast["tone"]) {
  const id = nextId++;
  toasts.value = [...toasts.value, { id, text, tone }];
  setTimeout(() => dismiss(id), TOAST_MS);
}

export const toast = {
  success: (text: string) => show(text, "success"),
  error: (text: string) => show(text, "error"),
};
