from rest_framework import serializers
from .models import Route
from stops.models import Stop
from tracking.utils import haversine

class RouteSerializer(serializers.ModelSerializer):
    bus_no = serializers.SerializerMethodField()

    from_stop = serializers.SerializerMethodField()
    to_stop = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    stops_count = serializers.SerializerMethodField()
    frequency = serializers.SerializerMethodField()
    
    class Meta:
        model = Route
        fields = ['id', 'name', 'bus_no', 'from_stop', 'to_stop', 'distance', 'stops_count', 'frequency']
    
    def get_bus_no(self, obj):
        # Reverse relation: Route -> Buses (related_name='buses')
        bus = obj.buses.first()
        if bus:
            return bus.bus_number
        return None
    

    
    def get_from_stop(self, obj):
        """Get first stop name (lowest order)"""
        first_stop = Stop.objects.filter(route=obj).order_by('order').first()
        return first_stop.name if first_stop else "N/A"
    
    def get_to_stop(self, obj):
        """Get last stop name (highest order)"""
        last_stop = Stop.objects.filter(route=obj).order_by('-order').first()
        return last_stop.name if last_stop else "N/A"
    
    def get_distance(self, obj):
        """Calculate total route distance by summing distances between consecutive stops"""
        stops = list(Stop.objects.filter(route=obj).order_by('order'))
        if len(stops) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(stops) - 1):
            distance = haversine(
                stops[i].latitude,
                stops[i].longitude,
                stops[i + 1].latitude,
                stops[i + 1].longitude
            )
            total_distance += distance
        
        return round(total_distance, 2)
    
    def get_stops_count(self, obj):
        """Get total number of stops in the route"""
        return Stop.objects.filter(route=obj).count()
    
    def get_frequency(self, obj):
        """Get bus frequency (default: 15 minutes if not set)"""
        # Frequency can be added to Route model later, for now return default
        return "15 min"
    
    def to_representation(self, instance):
        """Rename fields to match frontend expectations"""
        data = super().to_representation(instance)
        # Rename fields for frontend compatibility
        data['from'] = data.pop('from_stop')
        data['to'] = data.pop('to_stop')
        return data
