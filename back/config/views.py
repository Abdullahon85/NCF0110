"""Single-container mode: the built Vue site is served by Django itself."""
from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_safe


@require_safe
def spa_index(request):
    """index.html of the Vue site for every route that is not the API, media or static.

    Files that exist in the build (/assets/..., favicon) are sent earlier by WhiteNoise.
    404 when FRONTEND_DIR is not set (local development: the site runs on Vite)."""
    if not settings.FRONTEND_DIR:
        raise Http404
    try:
        html = (Path(settings.FRONTEND_DIR) / "index.html").read_bytes()
    except FileNotFoundError:
        raise Http404
    response = HttpResponse(html, content_type="text/html; charset=utf-8")
    response["Cache-Control"] = "no-cache"  # always pick up a new build after a redeploy
    return response
