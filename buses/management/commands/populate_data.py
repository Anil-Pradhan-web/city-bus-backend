from django.core.management.base import BaseCommand
from buses.models import Bus, Schedule
from routes.models import Route
from stops.models import Stop
from tracking.models import LiveLocation
import datetime

class Command(BaseCommand):
    help = 'Populates the database with dummy data for Routes, Buses, and Schedules'

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Starting Data Population...")

        # 1. Create Route 300
        r300, _ = Route.objects.get_or_create(name="Berhampur First Gate-Berhampur Railway Station")
        stops_300 = ["First Gate", "New Bus Stand", "Old Bus Stand", "Railway Station"]
        self.create_stops(r300, stops_300, base_lat=19.3150, base_lng=84.7940)
        
        # 2. Create Route 301
        r301, _ = Route.objects.get_or_create(name="Engineering School-Gopalpur Sea Beach")
        stops_301 = ["Engineering School", "Court Peta", "University", "Gopalpur"]
        self.create_stops(r301, stops_301, base_lat=19.3100, base_lng=84.8000)

        # 3. Create Route 100
        r100, _ = Route.objects.get_or_create(name="Khandagiri Square-Bhubaneswar Railway Station")
        stops_100 = ["Khandagiri Square", "Jagamara", "Iter College", "Aerodrome", "Siripur", "Ganga Nagar", "Ouat", "Kalpana", "Master Canteen", "Bhubaneswar Railway Station"]
        self.create_stops(r100, stops_100, base_lat=20.2592, base_lng=85.7894)

        # 4. Create Buses & Schedules
        self.setup_bus("300", r300, start_hour=7)
        self.setup_bus("301", r301, start_hour=7)
        self.setup_bus("100", r100, start_hour=8)
        
        # 5. Add Live Tracking for Bus 100 (One Forward, One Backward)
        self.setup_tracking("100", r100)

        self.stdout.write(self.style.SUCCESS("✅ SUCCESS: Database Populated! Ready to Roll! 🚌"))

    def create_stops(self, route, stop_names, base_lat, base_lng):
        for i, name in enumerate(stop_names):
            Stop.objects.get_or_create(
                route=route,
                name=name,
                defaults={
                    'latitude': base_lat + (i * 0.01),
                    'longitude': base_lng + (i * 0.01),
                    'order': i + 1
                }
            )

    def setup_bus(self, number, route, start_hour):
        # Create 2 buses per route for variety
        for i in range(2):
            bus, _ = Bus.objects.get_or_create(
                bus_number=number,
                route=route,
                defaults={'is_active': True}
            )
            # Create Schedule
            stops = list(Stop.objects.filter(route=route).order_by('order'))
            if stops:
                # Clear old
                bus.schedules.all().delete()
                
                # Generate times
                current_time = datetime.datetime(2024, 1, 1, start_hour, (i*30))
                for stop in stops:
                    Schedule.objects.create(bus=bus, stop=stop, arrival_time=current_time.time())
                    current_time += datetime.timedelta(minutes=5)

    def setup_tracking(self, bus_no, route):
        buses = Bus.objects.filter(bus_number=bus_no)
        stops = list(Stop.objects.filter(route=route).order_by('order'))
        if not stops or not buses.exists(): return

        # Bus 1: Start -> End
        b1 = buses.first()
        LiveLocation.objects.update_or_create(
            bus=b1,
            defaults={
                'latitude': stops[0].latitude,
                'longitude': stops[0].longitude,
                'current_stop_index': 0,
                'is_moving_forward': True
            }
        )

        # Bus 2: End -> Start (if exists)
        if buses.count() > 1:
            b2 = buses[1]
            LiveLocation.objects.update_or_create(
                bus=b2,
                defaults={
                    'latitude': stops[-1].latitude,
                    'longitude': stops[-1].longitude,
                    'current_stop_index': len(stops)-1,
                    'is_moving_forward': False
                }
            )
