import { test } from "node:test";
import assert from "node:assert/strict";
import { textToHtml, truncateText } from "../src/utils/richText.ts";

test("html is shown as text, not executed", () => {
  assert.equal(
    textToHtml('<script>alert("x")</script> & <b>'),
    "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt; &amp; &lt;b&gt;",
  );
  assert.equal(textToHtml("<img src=x onerror='a'>"), "&lt;img src=x onerror=&#39;a&#39;&gt;");
});

test("line breaks become <br>", () => {
  assert.equal(textToHtml("a\nb\r\nc"), "a<br>b<br>c");
});

test("empty values", () => {
  assert.equal(textToHtml(null), "");
  assert.equal(textToHtml(undefined), "");
  assert.equal(textToHtml(""), "");
});

test("truncate works on text before escaping", () => {
  assert.equal(truncateText("abcdef", 3), "abc...");
  assert.equal(truncateText("abc", 3), "abc");
  assert.equal(textToHtml(truncateText("<<<<<", 2)), "&lt;&lt;...");
});
