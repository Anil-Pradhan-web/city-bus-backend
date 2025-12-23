from django.contrib import admin
from .models import LiveLocation

@admin.register(LiveLocation)
class LiveLocationAdmin(admin.ModelAdmin):
    list_display = ('bus', 'latitude', 'longitude', 'timestamp')
    list_filter = ('bus',)
    ordering = ('-timestamp',)
