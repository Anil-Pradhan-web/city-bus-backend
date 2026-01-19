from rest_framework import serializers
from .models import Bus
from tracking.models import LiveLocation
from stops.models import Stop

class BusSerializer(serializers.ModelSerializer):
    next_stop = serializers.SerializerMethodField()
    eta = serializers.SerializerMethodField()

    city = serializers.SerializerMethodField()

    class Meta:
        model = Bus
        fields = ['id', 'bus_number', 'is_active', 'next_stop', 'eta', 'city']

    def get_next_stop(self, obj):
        live = LiveLocation.objects.filter(bus=obj).first()
        if live and obj.route:
            stops = list(Stop.objects.filter(route=obj.route).order_by('order'))
            if stops:
                try:
                    # Simple next stop logic
                    idx = live.current_stop_index
                    if live.is_moving_forward:
                        next_idx = idx + 1 if idx < len(stops) - 1 else idx - 1
                    else:
                        next_idx = idx - 1 if idx > 0 else idx + 1
                    
                    # Safety check
                    if 0 <= next_idx < len(stops):
                        return stops[next_idx].name
                except:
                    pass
        return "Not Started"

    def get_city(self, obj):
        num = str(obj.bus_number)
        if num.startswith('1'): return "Bhubaneswar"
        if num.startswith('2'): return "Puri"
        if num.startswith('3'): return "Berhampur"
        if num.startswith('4'): return "Cuttack"
        return "Odisha"

    def get_eta(self, obj):
        # Dummy ETA logic for list view (detailed ETA is in tracking API)
        return "5 min"

