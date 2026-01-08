from django.contrib import admin
from .models import Route
from stops.models import Stop
from buses.models import Bus

class StopInline(admin.TabularInline):
    model = Stop
    extra = 1
    fields = ('name', 'latitude', 'longitude', 'order')
    ordering = ('order',)

class BusInline(admin.TabularInline):
    model = Bus
    extra = 0
    fields = ('bus_number', 'is_active')
    readonly_fields = ('bus_number',)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_total_stops', 'get_total_buses', 'get_active_buses')
    search_fields = ('name',)
    inlines = [StopInline, BusInline]
    list_per_page = 20
    
    def get_total_stops(self, obj):
        return obj.stops.count()
    get_total_stops.short_description = 'Total Stops'
    
    def get_total_buses(self, obj):
        return obj.buses.count()
    get_total_buses.short_description = 'Total Buses'
    
    def get_active_buses(self, obj):
        return obj.buses.filter(is_active=True).count()
    get_active_buses.short_description = 'Active Buses'
