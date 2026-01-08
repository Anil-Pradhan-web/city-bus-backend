from django.contrib import admin
from .models import Stop

@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ('name', 'route', 'order', 'get_coordinates')
    list_filter = ('route',)
    search_fields = ('name', 'route__name')
    ordering = ('route', 'order')
    list_per_page = 30
    
    fieldsets = (
        ('Stop Information', {
            'fields': ('route', 'name', 'order')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'description': 'GPS coordinates of the stop'
        }),
    )
    
    def get_coordinates(self, obj):
        return f"({obj.latitude:.4f}, {obj.longitude:.4f})"
    get_coordinates.short_description = 'Coordinates'
