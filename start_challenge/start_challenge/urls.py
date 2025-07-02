from django.contrib import admin
from django.urls import path, include
from . import settings
from django.contrib.staticfiles.urls import static
from . import views

urlpatterns = [
    path('', views.portfolio, name='portfolio'),
    path("admin/", admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('questions/', include('questions.urls')),
    path('schedules/', include('schedules.urls')),
    path('chats/', include('chats.urls')),
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
