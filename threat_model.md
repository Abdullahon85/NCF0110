# Threat Model

## Project Overview

A Django 5 / Django REST Framework backend paired with a Vue 3 (Vite/Pinia) frontend for an e-commerce product catalog. Admins manage products, categories, brands, news, banners, orders, and contact messages through a dedicated frontend admin panel. Public users browse the catalog, submit contact messages, place orders, and write product reviews/questions. The backend is deployed on Render.com (previously at `ncb-1.onrender.com`). The frontend is deployed to Netlify/Vercel. JWT (SimpleJWT) is used for admin authentication; public endpoints require no auth. The database is SQLite (single-file, bundled with the app).

## Assets

- **Admin credentials** — Django superuser/staff usernames and passwords. Compromise grants full CRUD over catalog, orders, and public content.
- **JWT signing secret** — Derived from Django's `SECRET_KEY`. If leaked, attackers can forge admin tokens.
- **Order PII** — Customer names, phone numbers, email addresses, and Telegram handles stored in the `Order` model. Accessible only to admins via the API.
- **Contact messages** — Visitor names, emails, and free-text content. Stored and accessible to admins.
- **Uploaded media files** — Product images, brand logos, category images, and banners stored in the `media/` directory and served from the application origin.
- **Application secrets** — `SECRET_KEY`, database credentials (currently SQLite, no password).

## Trust Boundaries

- **Browser → Backend API** — All client requests cross this boundary. The backend must authenticate and authorize every write or sensitive read. The client (including the admin SPA) is untrusted.
- **Public vs. Authenticated** — Product browsing, banners, news, categories, brands, and the contact-message POST endpoint are public. Order creation is public (anonymous customers). Admin CRUD, order management, and stats require a valid admin JWT (`is_staff=True`).
- **Authenticated vs. Admin** — A user with a session cookie but without `is_staff` can theoretically reach the `IsAuthenticatedOrReadOnly`-protected upload endpoint on `ProductViewSet`. The actual admin surfaces use `IsAdminUser`.
- **Application → Media Storage** — Uploaded files are written to the local `media/` directory and served by WhiteNoise/Django at `/media/`. No CDN or separate origin isolation is in place.

## Scan Anchors

- **Entry points**: `back/api/urls.py`, `back/config/urls.py`
- **High-risk areas**: `back/api/views.py` (upload endpoints, order export, admin viewsets), `back/config/settings.py` (ALLOWED_HOSTS, DEBUG default, SECRET_KEY handling)
- **Public surfaces**: `/api/products/`, `/api/categories/`, `/api/brands/`, `/api/news/`, `/api/orders/` (POST only), `/api/contact/message/`
- **Admin surfaces**: `/api/admin/auth/`, `/api/admin/products/`, `/api/admin/categories/`, `/api/admin/brands/`, `/api/admin/banners/`, `/api/admin/orders/export-csv/`, and all other `/api/admin/*` routes
- **Dev-only**: `back/check_data.py`, `back/security_check.py` — standalone scripts, not reachable via HTTP

## Threat Categories

### Spoofing

Admin authentication is via JWT (HS256, 15-minute access token, 1-day refresh, rotation + blacklist on refresh). The `SECRET_KEY` is the JWT signing key; if the insecure default key is used in production (possible when DEBUG env var is absent and the start-up check is skipped), tokens could be forged. Session authentication is also active, meaning Django admin sessions can authenticate to API endpoints. The admin login endpoint applies `LoginRateThrottle` (5/hour) to limit brute-force attempts.

### Tampering

File uploads allow `image/svg+xml`. SVG is an active document type; browsers execute embedded scripts when an SVG is navigated to directly. Uploaded files are served from the same origin, so scripts in SVGs run in the application's origin context. No server-side SVG sanitization is applied.

### Information Disclosure

When `DEBUG=True` (the default if the `DEBUG` env var is missing), Django renders detailed error pages containing stack traces, settings values, and local variables. The `ALLOWED_HOSTS` wildcard prevents Django from rejecting requests with arbitrary Host headers, which can facilitate cache-poisoning or aid in constructing phishing URLs built by the application. Order PII (names, phones, emails) is accessible only to admins; the CSV export endpoint is gated by `IsAdminUser`.

### Elevation of Privilege

The public `ProductViewSet` exposes an `upload-image` POST action protected only by `IsAuthenticatedOrReadOnly`, meaning any authenticated session (not just `is_staff`) can upload images to any product by slug. The intended admin upload endpoint on `ProductAdminViewSet` correctly uses `IsAdminUser`. This inconsistency could be exploited by limited-privilege staff accounts or by session-authenticated users who do not hold the admin JWT.

### Denial of Service

The anonymous throttle is 1000 requests/hour in development and 500/hour in production. The order-creation endpoint is public and unauthenticated with these same default limits. File upload endpoints enforce a 10 MB maximum per file, consistent with Django's `DATA_UPLOAD_MAX_MEMORY_SIZE`. No rate limiting specific to order creation or review/question submission is configured beyond the global anon throttle.
