from django.core.management.base import BaseCommand
from buses.models import Bus
from routes.models import Route
from tracking.models import LiveLocation
from stops.models import Stop

class Command(BaseCommand):
    help = 'Repopulates transport data (Buses and initial Locations) based on existing Routes'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting setup using EXISTING DATABASE ROUTES...")
        
        # 1. Clear existing buses
        Bus.objects.all().delete()
        self.stdout.write("Cleared existing buses.")

        # 2. Identify the Real Routes
        r300_real = Route.objects.filter(name__icontains="Berhampur First Gate").first()
        r301_real = Route.objects.filter(name__icontains="Gopalpur Junction").first()

        if not r300_real:
            self.stdout.write(self.style.ERROR("Error: Could not find route for 300 (Berhampur First Gate...)"))
        else:
            self.stdout.write(f"Mapped 300 -> {r300_real.name} (ID: {r300_real.id})")
            stops300 = list(Stop.objects.filter(route=r300_real).order_by('order'))
            if stops300:
                # Bus 1: Forward
                b300_1 = Bus.objects.create(bus_number="300", route=r300_real, is_active=True)
                LiveLocation.objects.create(
                    bus=b300_1,
                    latitude=stops300[0].latitude,
                    longitude=stops300[0].longitude,
                    current_stop_index=0,
                    is_moving_forward=True
                )
                # Bus 2: Backward
                b300_2 = Bus.objects.create(bus_number="300", route=r300_real, is_active=True)
                last_idx = len(stops300) - 1
                LiveLocation.objects.create(
                    bus=b300_2,
                    latitude=stops300[last_idx].latitude,
                    longitude=stops300[last_idx].longitude,
                    current_stop_index=last_idx,
                    is_moving_forward=False
                )
                self.stdout.write(self.style.SUCCESS("Created 2 buses for Route 300."))
            else:
                self.stdout.write(self.style.WARNING("Warning: Route 300 (Real) has no stops!"))

        if not r301_real:
            self.stdout.write(self.style.ERROR("Error: Could not find route for 301 (Gopalpur Junction...)"))
        else:
            self.stdout.write(f"Mapped 301 -> {r301_real.name} (ID: {r301_real.id})")
            stops301 = list(Stop.objects.filter(route=r301_real).order_by('order'))
            if stops301:
                # Bus 1: Forward
                b301_1 = Bus.objects.create(bus_number="301", route=r301_real, is_active=True)
                LiveLocation.objects.create(
                    bus=b301_1,
                    latitude=stops301[0].latitude,
                    longitude=stops301[0].longitude,
                    current_stop_index=0,
                    is_moving_forward=True
                )
                # Bus 2: Backward
                b301_2 = Bus.objects.create(bus_number="301", route=r301_real, is_active=True)
                last_idx = len(stops301) - 1
                LiveLocation.objects.create(
                    bus=b301_2,
                    latitude=stops301[last_idx].latitude,
                    longitude=stops301[last_idx].longitude,
                    current_stop_index=last_idx,
                    is_moving_forward=False
                )
                self.stdout.write(self.style.SUCCESS("Created 2 buses for Route 301."))
            else:
                self.stdout.write(self.style.WARNING("Warning: Route 301 (Real) has no stops!"))
