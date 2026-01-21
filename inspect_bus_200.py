import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_backend.settings')
django.setup()

from buses.models import Bus
from routes.models import Route
from stops.models import Stop

def inspect_bus_200():
    try:
        bus = Bus.objects.filter(bus_number='200').first()
        if not bus:
            print("Bus 200 not found!")
            return

        print(f"Bus: {bus.bus_number}")
        print(f"Route: {bus.route}")

        if not bus.route:
            print("No route assigned")
            return

        stops = list(Stop.objects.filter(route=bus.route).order_by('order'))
        print(f"Total Stops: {len(stops)}")
        print("-" * 60)
        print(f"{'Order':<6} {'Name':<30} {'Lat':<12} {'Lng':<12}")
        print("-" * 60)
        for stop in stops:
            print(f"{stop.order:<6} {stop.name[:30]:<30} {stop.latitude:<12} {stop.longitude:<12}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    inspect_bus_200()
