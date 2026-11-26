import { test } from "node:test";
import assert from "node:assert/strict";
import { isTokenExpired, sessionState } from "../src/utils/jwt.ts";

// unsigned test tokens: only the payload matters here
const b64url = (o: object) => Buffer.from(JSON.stringify(o)).toString("base64url");
const token = (exp: number, extra: object = {}) => `x.${b64url({ exp, ...extra })}.y`;
const now = Date.now() / 1000;

test("expired access + live refresh = session continues via refresh", () => {
  assert.equal(sessionState(token(now - 60), token(now + 3600)), "refresh");
});

test("valid access = valid", () => {
  assert.equal(sessionState(token(now + 600), token(now + 3600)), "valid");
});

test("nothing usable = none", () => {
  assert.equal(sessionState(null, null), "none");
  assert.equal(sessionState(token(now - 60), null), "none");
  assert.equal(sessionState(token(now - 60), token(now - 1)), "none");
  assert.equal(sessionState("garbage", "garbage"), "none");
});

test("base64url payloads with - and _ are decoded", () => {
  // a payload whose base64url form contains '-' or '_'
  let t = "";
  for (let i = 0; i < 200 && !/[-_]/.test(t); i++) t = token(now + 600, { pad: "?>".repeat(i) });
  assert.match(t, /[-_]/);
  assert.equal(isTokenExpired(t), false);
});
