// Texts typed by the admin (product descriptions, news, "About", brand
// descriptions) are plain text from a <textarea>. They are shown with v-html
// only to keep line breaks: everything else is escaped, so HTML or <script>
// typed into a description is displayed as text and never runs on the site.
const ESCAPES: Record<string, string> = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
};

export function textToHtml(text: string | null | undefined): string {
  if (!text) return "";
  return text.replace(/[&<>"']/g, (ch) => ESCAPES[ch]).replace(/\r?\n/g, "<br>");
}

export function truncateText(text: string, max: number): string {
  return text.length <= max ? text : text.substring(0, max) + "...";
}
