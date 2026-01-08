from django.contrib import admin
from django.utils import timezone
from .models import LiveLocation

class LiveLocationInline(admin.StackedInline):
    model = LiveLocation
    can_delete = False
    verbose_name_plural = 'Current Live Location'
    fields = ('latitude', 'longitude', 'current_stop_index', 'is_moving_forward')


@admin.register(LiveLocation)
class LiveLocationAdmin(admin.ModelAdmin):
    list_display = (
        'bus', 
        'get_route', 
        'get_coordinates', 
        'current_stop_index', 
        'get_direction',
        'timestamp',
        'get_time_since_update'
    )
    list_filter = ('bus__route', 'is_moving_forward', 'bus__is_active')
    search_fields = ('bus__bus_number', 'bus__route__name')
    ordering = ('-timestamp',)
    list_per_page = 25
    readonly_fields = ('timestamp', 'last_moved_at')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "bus":
            # Sirf wo buses dikhao jinki location set nahi hai
            # Par agar existing object edit kar rahe ho, to wo bus dikhni chahiye
            obj_id = request.resolver_match.kwargs.get('object_id')
            if not obj_id: # Creating new
                 kwargs["queryset"] = db_field.related_model.objects.filter(live_location__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    fieldsets = (
        ('Bus Information', {
            'fields': ('bus',)
        }),
        ('Current Location', {
            'fields': ('latitude', 'longitude', 'current_stop_index')
        }),
        ('Movement', {
            'fields': ('is_moving_forward',),
            'description': 'Direction of bus movement'
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'last_moved_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_route(self, obj):
        return obj.bus.route.name if obj.bus.route else 'No Route'
    get_route.short_description = 'Route'
    get_route.admin_order_field = 'bus__route__name'
    
    def get_coordinates(self, obj):
        return f"({obj.latitude:.4f}, {obj.longitude:.4f})"
    get_coordinates.short_description = 'Coordinates'
    
    def get_direction(self, obj):
        return "Forward ➡️" if obj.is_moving_forward else "Backward ⬅️"
    get_direction.short_description = 'Direction'
    
    def get_time_since_update(self, obj):
        if obj.timestamp:
            delta = timezone.now() - obj.timestamp
            seconds = delta.total_seconds()
            if seconds < 60:
                return f"{int(seconds)}s ago"
            elif seconds < 3600:
                return f"{int(seconds/60)}m ago"
            else:
                return f"{int(seconds/3600)}h ago"
        return "Never"
    get_time_since_update.short_description = 'Last Update'
