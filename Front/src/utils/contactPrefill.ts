// Message handed to the contact form through history.state (not the URL: a long ?message=
// would exceed the server's request-line limit on reload).

export const CONTACT_MESSAGE_MAX = 3000; // back/api/serializers.py CONTACT_MESSAGE_MAX_LENGTH

export function contactPrefill(state: unknown): string {
  if (!state || typeof state !== "object") return "";
  const message = (state as { message?: unknown }).message;
  return typeof message === "string" ? message.slice(0, CONTACT_MESSAGE_MAX) : "";
}
