from django.contrib import admin
from .models import ChatsGroup, Chats

class ChatsInline(admin.TabularInline):
  model = Chats
  extra = 1

class ChatsGroupAdmin(admin.ModelAdmin):
  list_display = ('group_category', 'groupname', 'created_at')
  inlines = [ChatsInline]
  filter_horizontal = ('user',)

admin.site.register(ChatsGroup, ChatsGroupAdmin)