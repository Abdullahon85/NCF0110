// Class names used in .vue templates, and which of them only the admin panel uses.
// Shared by tests and by the admin style checks.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { basename, join } from "node:path";

export const SRC = new URL("../src/", import.meta.url).pathname;

export function vueFiles(dir: string = SRC): string[] {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) return vueFiles(path);
    return name.endsWith(".vue") ? [path] : [];
  });
}

export function isAdminFile(path: string): boolean {
  const name = basename(path);
  return (
    path.includes("/components/admin/") ||
    /^Admin.*\.vue$/.test(name) ||
    /Management\.vue$/.test(name)
  );
}

export function templateClasses(path: string): Set<string> {
  const text = readFileSync(path, "utf8");
  const template = text.split(/<script\b/)[0];
  const found = new Set<string>();
  const add = (s: string) =>
    s
      .split(/\s+/)
      .filter((c) => /^[a-zA-Z][\w-]*$/.test(c))
      .forEach((c) => found.add(c));
  for (const m of template.matchAll(/\sclass="([^"]*)"/g)) add(m[1]);
  for (const m of template.matchAll(/:class="([^"]*)"/g)) {
    for (const s of m[1].matchAll(/'([^']*)'|`([^`$]*)`/g)) add(s[1] ?? s[2]);
    for (const k of m[1].matchAll(/([a-zA-Z][\w-]*)\s*:/g)) add(k[1]);
  }
  return found;
}

// Generic building blocks of the shared design system (buttons, badges, forms, modals,
// tables, status words...). Even when only the admin panel uses them today, their rules
// interleave with base rules in main.css (e.g. .btn), so they stay there: moving them
// to a later stylesheet would flip the cascade.
export const SHARED_UTILITY =
  /^(btn|badge|card|modal|form|checkbox|chip|close-btn|data-table|table|empty|label|small|success|warning|danger|info|error|hint|selected|text|page|tab-btn|toggle-btn|section|message|new|full|delete|actions|multi-select|file-input|stars|value|values|header-actions|filter|filters-bar|inline-table|more-tags|no-|preview|thumb|upload|status|unread|collapsed|expanded|mobile-open|description-preview|link-preview|tags|features|count-badge)(-|$|[A-Z])/;

export function adminOnlyClasses(): Set<string> {
  const admin = new Set<string>();
  const pub = new Set<string>();
  for (const f of vueFiles())
    templateClasses(f).forEach((c) => (isAdminFile(f) ? admin : pub).add(c));
  return new Set([...admin].filter((c) => !pub.has(c) && !SHARED_UTILITY.test(c)));
}
