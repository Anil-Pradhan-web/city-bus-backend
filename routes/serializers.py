from rest_framework import serializers
from .models import Route
from stops.models import Stop
from tracking.utils import haversine

class RouteSerializer(serializers.ModelSerializer):
    bus_no = serializers.SerializerMethodField()

    from_stop = serializers.SerializerMethodField()
    to_stop = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()
    stops_count = serializers.SerializerMethodField()
    stops_count_value = serializers.SerializerMethodField()
    frequency = serializers.SerializerMethodField()
    frequency_minutes = serializers.SerializerMethodField()
    
    city = serializers.SerializerMethodField()
    
    class Meta:
        model = Route
        fields = [
            'id',
            'name',
            'bus_no',
            'from_stop',
            'to_stop',
            'distance',
            'distance_km',
            'stops_count',
            'stops_count_value',
            'frequency',
            'frequency_minutes',
            'city',
        ]
    
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
            return "N/A"
        
        total_distance = 0.0
        for i in range(len(stops) - 1):
            distance = haversine(
                stops[i].latitude,
                stops[i].longitude,
                stops[i + 1].latitude,
                stops[i + 1].longitude
            )
            total_distance += distance
        
        return f"{round(total_distance, 1)} km"

    def get_distance_km(self, obj):
        """Return total route distance as a numeric value in kilometers."""
        stops = list(Stop.objects.filter(route=obj).order_by('order'))
        if len(stops) < 2:
            return None

        total_distance = 0.0
        for i in range(len(stops) - 1):
            distance = haversine(
                stops[i].latitude,
                stops[i].longitude,
                stops[i + 1].latitude,
                stops[i + 1].longitude
            )
            total_distance += distance

        return round(total_distance, 1)
    
    def get_stops_count(self, obj):
        """Get total number of stops in the route"""
        count = Stop.objects.filter(route=obj).count()
        return f"{count} Stops"

    def get_stops_count_value(self, obj):
        """Return total number of stops as an integer."""
        return Stop.objects.filter(route=obj).count()
    
    def get_frequency(self, obj):
        """Get bus frequency based on route/city"""
        bus = obj.buses.first()
        if bus:
            return "Every 10 mins"
        
        return "Every 10 mins"

    def get_frequency_minutes(self, obj):
        """Return frequency in minutes as an integer for frontend use."""
        bus = obj.buses.first()
        if bus:
            return 10

        return 10

    def get_city(self, obj):
        """Derive city from bus number pattern"""
        bus = obj.buses.first()
        if bus:
            num = str(bus.bus_number)
            if num.startswith('1'): return "Bhubaneswar"
            if num.startswith('2'): return "Puri"
            if num.startswith('3'): return "Berhampur"
            if num.startswith('4'): return "Cuttack"
        return "Odisha"
    
    def to_representation(self, instance):
        """Rename fields to match frontend expectations"""
        data = super().to_representation(instance)
        # Rename fields for frontend compatibility
        data['from'] = data.pop('from_stop')
        data['to'] = data.pop('to_stop')
        return data
