from django.contrib import admin
from .models import Templates

class TemplatesAdmin(admin.ModelAdmin):
  list_display = ('id', 'title', 'templatetext')

admin.site.register(Templates, TemplatesAdmin)
