from django.contrib import admin
from django.urls import path, include
from . import settings
from django.contrib.staticfiles.urls import static
from . import views
from accounts import views as accounts_views

urlpatterns = [
    path('', views.portfolio, name='portfolio'),
    path("admin/", admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('questions/', include('questions.urls')),
    path('schedules/', include('schedules.urls')),
    path('chats/', include('chats.urls')),
    path('sw.js', views.service_worker, name='service_worker'),
    path('api/save-subscription/', accounts_views.register_push, name='save_subscription'),
    path('api/unregister-subscription/', accounts_views.unregister_subscription, name='unregister-subscription'),
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
