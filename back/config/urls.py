from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.urls import re_path
from django.views.static import serve


urlpatterns = [
    path('dashboard-ctrl-panel/', admin.site.urls),
    path('api/', include('api.urls')),
    path('meta.json', TemplateView.as_view(template_name='meta.json', content_type='application/json')),
]

# django.conf.urls.static.static() returns [] when DEBUG is off, so media
# would disappear in production; serve it explicitly behind SERVE_MEDIA.
if settings.DEBUG or settings.SERVE_MEDIA:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
