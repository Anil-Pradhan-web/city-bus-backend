from django.contrib import admin
from .models import Stop

@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ('name', 'route', 'order')
    list_filter = ('route',)
    ordering = ('order',)
