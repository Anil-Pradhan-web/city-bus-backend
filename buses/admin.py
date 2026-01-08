from django.contrib import admin
from .models import Bus
from tracking.admin import LiveLocationInline

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_number', 'route', 'is_active', 'get_current_location')
    list_filter = ('is_active', 'route')
    search_fields = ('bus_number', 'route__name')
    list_editable = ('is_active',)
    inlines = [LiveLocationInline]
    ordering = ('bus_number',)

    list_per_page = 25
    
    fieldsets = (
        ('Bus Information', {
            'fields': ('bus_number', 'route')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def get_current_location(self, obj):
        """Display current location if available"""
        try:
            if hasattr(obj, 'live_location'):
                loc = obj.live_location
                return f"({loc.latitude:.4f}, {loc.longitude:.4f})"
            return "No location"
        except:
            return "No location"
    get_current_location.short_description = 'Current Location'
    
    actions = ['activate_buses', 'deactivate_buses']
    
    def activate_buses(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} bus(es) activated successfully.')
    activate_buses.short_description = 'Activate selected buses'
    
    def deactivate_buses(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} bus(es) deactivated successfully.')
    deactivate_buses.short_description = 'Deactivate selected buses'
