import { test } from "node:test";
import assert from "node:assert/strict";
import { adminErrorMessage } from "../src/utils/apiError.ts";

const err = (data: unknown, status = 400) => ({ response: { status, data } });

test("detail string wins", () => {
  assert.equal(adminErrorMessage(err({ detail: "Нельзя удалить" }), "Ошибка"), "Нельзя удалить");
});

test("known field gets a russian label", () => {
  assert.equal(
    adminErrorMessage(err({ name: ["Уже существует."] }), "Ошибка"),
    "Название: Уже существует.",
  );
  assert.equal(adminErrorMessage(err({ slug: ["Занят."] }), "Ошибка"), "Адрес (slug): Занят.");
});

test("unknown field shows the message alone", () => {
  assert.equal(adminErrorMessage(err({ weird_field: ["Плохо."] }), "Ошибка"), "Плохо.");
});

test("non_field_errors and nested lists", () => {
  assert.equal(
    adminErrorMessage(err({ non_field_errors: ["Общая ошибка."] }), "Ошибка"),
    "Общая ошибка.",
  );
  assert.equal(
    adminErrorMessage(err({ items: [{ quantity: ["Слишком много."] }] }), "Ошибка"),
    "Слишком много.",
  );
});

test("no response body -> fallback", () => {
  assert.equal(
    adminErrorMessage(new Error("Network Error"), "Ошибка сохранения"),
    "Ошибка сохранения",
  );
  assert.equal(
    adminErrorMessage(err("<html>502</html>", 502), "Ошибка сохранения"),
    "Ошибка сохранения",
  );
  assert.equal(adminErrorMessage(undefined, "Ошибка"), "Ошибка");
});
