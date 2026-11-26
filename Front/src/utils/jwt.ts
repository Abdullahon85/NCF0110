// Reading the expiry of the admin JWTs (signature is checked by the server, not here).

function payload(token: string): { exp?: number } | null {
  try {
    const part = token.split(".")[1];
    const b64 = part.replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(b64.padEnd(b64.length + ((4 - (b64.length % 4)) % 4), "=")));
  } catch {
    return null;
  }
}

export function isTokenExpired(token: string): boolean {
  const exp = payload(token)?.exp;
  return typeof exp !== "number" || exp * 1000 < Date.now();
}

// "valid": the access token works; "refresh": it expired but the refresh token
// is still alive, so the session continues after one refresh; "none": log in again.
export type SessionState = "valid" | "refresh" | "none";

export function sessionState(access: string | null, refresh: string | null): SessionState {
  if (access && !isTokenExpired(access)) return "valid";
  if (refresh && !isTokenExpired(refresh)) return "refresh";
  return "none";
}
