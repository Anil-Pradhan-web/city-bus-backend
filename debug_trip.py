import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_backend.settings')
django.setup()

from stops.models import Stop
from routes.models import Route

print("--- Debugging Routes ---")

s1_name = "Berhampur New Bus Stand"
s2_name = "Gopalpur Junction"

starts = Stop.objects.filter(name__icontains="Berhampur New Bus Stand")
ends = Stop.objects.filter(name__icontains="Gopalpur Junction")

print(f"Found {starts.count()} start stops matching '{s1_name}'")
for s in starts:
    print(f"  - ID: {s.id}, Name: {s.name}, Route: {s.route.name} (ID: {s.route.id}), Order: {s.order}")

print(f"Found {ends.count()} end stops matching '{s2_name}'")
for s in ends:
    print(f"  - ID: {s.id}, Name: {s.name}, Route: {s.route.name} (ID: {s.route.id}), Order: {s.order}")

print("\n--- Checking Direct Connection logic ---")
for start in starts:
    for end in ends:
        if start.route == end.route:
            print(f"Match found on Route: {start.route.name}")
            print(f"  Start Order: {start.order}")
            print(f"  End Order: {end.order}")
            if start.order < end.order:
                print(f"  -> VALID Forward Route")
            else:
                print(f"  -> INVALID (Reverse direction requested but not supported by simple comparison)")
        else:
            print(f"Different routes: {start.route.name} vs {end.route.name}")
