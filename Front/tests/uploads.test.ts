import { test } from "node:test";
import assert from "node:assert/strict";
import { uploadEach } from "../src/utils/uploads.ts";

test("one bad file does not stop the others and is reported", async () => {
  const done: string[] = [];
  const failures = await uploadEach(
    ["a.jpg", "big.jpg", "c.png"],
    async (name) => {
      if (name === "big.jpg") throw { response: { data: { error: "File too large. Maximum size is 10MB." } } };
      done.push(name);
    },
    (name) => name,
  );
  assert.deepEqual(done, ["a.jpg", "c.png"]);
  assert.deepEqual(failures, ["big.jpg: File too large. Maximum size is 10MB."]);
});

test("no failures -> empty list", async () => {
  assert.deepEqual(await uploadEach([1, 2], async () => {}, String), []);
});
