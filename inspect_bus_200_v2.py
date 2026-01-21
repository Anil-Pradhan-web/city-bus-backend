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
    output_file = 'bus_200_stops_utf8.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        try:
            bus = Bus.objects.filter(bus_number='200').first()
            if not bus:
                f.write("Bus 200 not found!\n")
                return

            f.write(f"Bus: {bus.bus_number}\n")
            f.write(f"Route: {bus.route}\n")

            if not bus.route:
                f.write("No route assigned\n")
                return

            stops = list(Stop.objects.filter(route=bus.route).order_by('order'))
            f.write(f"Total Stops: {len(stops)}\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'Order':<6} {'Name':<30} {'Lat':<12} {'Lng':<12}\n")
            f.write("-" * 60 + "\n")
            for stop in stops:
                f.write(f"{stop.order:<6} {stop.name[:30]:<30} {stop.latitude:<12} {stop.longitude:<12}\n")
                
        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == '__main__':
    inspect_bus_200()
