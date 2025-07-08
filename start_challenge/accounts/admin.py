from django.contrib import admin
from .models import (
  Users, Categories
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
  ordering = ('id',)
  list_display = ('email', 'id', 'password')
  list_filter = ('is_staff', 'is_superuser')
  fieldsets = (
    (None, {'fields': ('email', 'password')}),
    ('Personal Information', {'fields': ('username',)}),
    (
      'Permissions',
      {
        'fields': (
          'is_staff',
          'is_superuser',
        )
      }
    ),
    ('Important dates', {'fields': ('last_login',)}),
  )
  add_fieldsets = (
    (None, {
      'classes': ('wide',),
      'fields': ('email', 'password', 'password2'),
    }),
  )

class CategoriesAdmin(admin.ModelAdmin):
  list_display = ('id', 'categoryname')


admin.site.register(Users, UserAdmin)
admin.site.register(Categories, CategoriesAdmin)