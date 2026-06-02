from django.contrib import admin

from apps.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'slug')
