import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_backend.settings')
django.setup()

from buses.models import Bus
from tracking.models import LiveLocation
from routes.models import Route
from stops.models import Stop
from tracking.utils import haversine

bus = Bus.objects.get(bus_number='300')
live = LiveLocation.objects.filter(bus=bus).first()
route = Route.objects.filter(bus=bus).first()
stops = list(Stop.objects.filter(route=route).order_by("order"))

print(f"Bus found: {bus}")
print(f"Live location: {live}")
print(f"Route found: {route}")
print(f"Stops count: {len(stops)}")

if live and route and stops:
    current_index = live.current_stop_index
    next_index = (current_index + 1) % len(stops)
    
    current_stop = stops[current_index]
    next_stop = stops[next_index]
    
    print(f"Current Index: {current_index}")
    print(f"Next Index: {next_index}")
    print(f"Current Stop: {current_stop.name}")
    print(f"Next Stop: {next_stop.name}")
    
    distance = haversine(live.latitude, live.longitude, next_stop.latitude, next_stop.longitude)
    print(f"Distance: {distance} km")
    
    eta = max(1, round((distance / 28) * 60))
    print(f"ETA: {eta} minutes")
