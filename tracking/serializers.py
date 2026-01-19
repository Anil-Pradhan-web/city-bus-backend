from rest_framework import serializers
from .models import LiveLocation

class LiveLocationSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = LiveLocation
        fields = ['id', 'bus', 'latitude', 'longitude', 'current_stop_index', 'is_moving_forward', 'timestamp', 'speed', 'crowding', 'last_moved_at', 'stop_arrival_time', 'status']

    def get_status(self, obj):
        if obj.stop_arrival_time:
             # If arrival time is set, we assume it's waiting unless cleared (though logic elsewhere clears it)
             # But strictly speaking, if stop_arrival_time is present, it MIGHT be waiting. 
             # However, MoveBusView logic handles clearing it. Here we just report what's in DB.
             # A better check might be needed, but for now:
             return "WAITING"
        return "MOVING"
