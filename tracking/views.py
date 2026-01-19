from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import random
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from buses.models import Bus
from routes.models import Route
from stops.models import Stop
from .models import LiveLocation
from .serializers import LiveLocationSerializer
from .utils import haversine
from django.utils import timezone
from datetime import timedelta


# =========================
# UPDATE LIVE LOCATION
# =========================
class UpdateLocationView(APIView):
    """
    POST: driver/simulator sends latest lat/lng
    """
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = LiveLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================
# CURRENT BUS LOCATION
# =========================
class CurrentLocationView(APIView):
    """
    GET: frontend fetches current bus location
    """
    def get(self, request, bus_id):
        try:
            bus = Bus.objects.get(id=bus_id)
        except Bus.DoesNotExist:
            return Response(
                {"detail": "Bus not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        location = LiveLocation.objects.filter(bus=bus).first()
        if not location:
            return Response(
                {"detail": "No live location yet"},
                status=status.HTTP_200_OK
            )

        serializer = LiveLocationSerializer(location)
        return Response(serializer.data)


# =========================
# BUS ETA (SIMPLE)
# =========================
class BusETAView(APIView):
    """
    GET: Returns ETAs for all stops on the route for each active bus.
    """
    # Use same speed as MoveBusView for consistency
    def get(self, request, bus_no):
        # Realistic city bus speed for all buses
        bus_speed = 60
        buses = Bus.objects.filter(bus_number=str(bus_no)).select_related('route')
        if not buses.exists():
            return Response({"detail": "Bus not found"}, status=404)

        results = []

        for bus in buses:
            live = LiveLocation.objects.filter(bus=bus).first()
            if not live or not bus.route:
                continue

            stops = list(Stop.objects.filter(route=bus.route).order_by("order"))
            if not stops:
                continue

            current_idx = live.current_stop_index

            # SAFETY CHECK: Valid index?
            if current_idx >= len(stops) or current_idx < 0:
                current_idx = 0
                # Optionally auto-correct DB
                live.current_stop_index = 0
                live.save()
            forward = live.is_moving_forward
            total_stops = len(stops)
            
            # Calculate ETAs for all stops from the current position
            stops_eta = []
            
            # Simple simulation of path
            temp_idx = current_idx
            temp_forward = forward
            temp_lat = live.latitude
            temp_lon = live.longitude
            accumulated_time = 0
            
            # SAFETY CHECK: Fix direction if stuck at terminal
            if current_idx == 0 and not forward:
                forward = True
            elif current_idx == len(stops) - 1 and forward:
                forward = False

            # We calculate ETA for the next 10 stop-steps or until end of route
            stops_to_visit = stops[current_idx+1:] if forward else stops[:current_idx][::-1]
            
            # If at the very end, we might be waiting or about to turn
            if not stops_to_visit:
                pass

            for next_stop in stops_to_visit:
                dist = haversine(temp_lat, temp_lon, next_stop.latitude, next_stop.longitude)
                travel_time_min = (dist / bus_speed) * 60
                
                # Add stop delay if it's not the first segment
                if accumulated_time > 0:
                    accumulated_time += (3 / 60) # 3 seconds wait
                
                accumulated_time += travel_time_min
                
                
                stops_eta.append({
                    "stop_name": next_stop.name,
                    "eta_minutes": max(1, round(accumulated_time)),
                    "order": next_stop.order
                })
                
                # Update temp pos for next segment
                temp_lat = next_stop.latitude
                temp_lon = next_stop.longitude

            # Handle case where no stops provided
            if stops_eta:
                next_stop_name = stops_eta[0]["stop_name"]
                first_eta = stops_eta[0]["eta_minutes"]
            else:
                # Fallback: If no stops in ETA list, we are at terminal.
                # If forward=True at the end, we are at Last Stop. Target is turn around? 
                # Display current stop as "Arrived at X" or just X.
                next_stop_name = stops[current_idx].name
                first_eta = 0

            results.append({
                "bus_id": bus.id,
                "bus_no": bus.bus_number,
                "current_stop": stops[current_idx].name,
                "is_moving_forward": forward,
                "stops_eta": stops_eta,
                # For backward compatibility
                "next_stop": next_stop_name,
                "eta_minutes": first_eta,
                "speed": live.speed,
                "crowding": live.crowding
            })

        return Response(results)


# =========================
# BUS ROUTE (POLYLINE)
# =========================
class BusRouteView(APIView):
    """
    GET: Returns ordered stops for a bus route
    """
    def get(self, request, bus_no):
        # We assume all buses with the same number share the same route
        bus = Bus.objects.filter(bus_number=str(bus_no)).select_related('route').first()
        if not bus:
            return Response({"detail": "Bus not found"}, status=404)

        # Check ForeignKey (bus.route)
        route = bus.route
        if not route:
            return Response({"detail": "No route assigned"}, status=200)

        stops = Stop.objects.filter(route=route).order_by("order")
        if not stops.exists():
            return Response({"detail": "No stops found"}, status=200)

        return Response({
            "bus_number": bus.bus_number,
            "stops": [
                {
                    "stop_name": s.name,  # changed from 'name' to 'stop_name'
                    "latitude": s.latitude,
                    "longitude": s.longitude,
                    "order": s.order
                }
                for s in stops
            ]
        })


# =========================
# MOVE BUS (SMOOTH INTERPOLATION WITH ETA)
# =========================
class MoveBusView(APIView):
    """
    POST: Simulates bus moving with smooth interpolation between stops.
    Includes ETA calculation directly in the response to ensure frontend has all data.
    """
    STOP_DELAY_SECONDS = 0 # No stop delay, continuous movement

    def post(self, request, bus_no):
        buses = Bus.objects.filter(bus_number=str(bus_no)).select_related('route')
        if not buses.exists():
            return Response({"error": "Bus not found"}, status=404)

        # Realistic city bus speed for all buses
        # "Thoda" faster simulation speed for all buses
        bus_speed = 450

        results = []
        now = timezone.now()

        for bus in buses:
            route = bus.route
            if not route:
                continue

            stops = list(Stop.objects.filter(route=route).order_by("order"))
            if not stops:
                continue

            live, _ = LiveLocation.objects.get_or_create(
                bus=bus,
                defaults={
                    "latitude": stops[0].latitude,
                    "longitude": stops[0].longitude,
                    "current_stop_index": 0,
                    "is_moving_forward": True
                }
            )

            # --- Logic 0: Dynamic Data Simulation ---
            if random.random() < 0.2: 
                # INCREASED SPEED range for smoother fast movement
                live.speed = max(40, min(100, live.speed + random.randint(-5, 5)))
            
            # --- Logic 1: Stop Waiting (Start & End Only) ---
            current_status = "MOVING"
            if live.stop_arrival_time:
                time_at_stop = (now - live.stop_arrival_time).total_seconds()
                
                # 5 seconds delay ONLY at Start (0) and End (total_stops - 1)
                required_delay = 0
                if live.current_stop_index == 0 or live.current_stop_index == len(stops) - 1:
                    required_delay = 5.0
                
                if time_at_stop < required_delay:
                    current_status = "WAITING"
                else:
                    live.stop_arrival_time = None
                    live.save()
            
            # Use current state
            current_idx = live.current_stop_index
            
            # SAFETY CHECK
            if current_idx >= len(stops) or current_idx < 0:
                current_idx = 0
                live.current_stop_index = 0
                live.latitude = stops[0].latitude
                live.longitude = stops[0].longitude
                live.save()
            
            forward = live.is_moving_forward
            stop_name = stops[current_idx].name
            
            new_latitude = live.latitude
            new_longitude = live.longitude
            progress_pct = 0

            # --- Logic 2: Movement ---
            if current_status != "WAITING":
                if forward:
                    next_idx = current_idx + 1 if current_idx < len(stops) - 1 else current_idx - 1
                    if current_idx >= len(stops) - 1: forward = False
                else:
                    next_idx = current_idx - 1 if current_idx > 0 else current_idx + 1
                    if current_idx <= 0: forward = True
                
                if next_idx < 0: next_idx = 0
                if next_idx >= len(stops): next_idx = len(stops) - 1

                current_stop = stops[current_idx]
                next_stop = stops[next_idx]

                # Speed Calculation (High speed requested)
                # 800 km/h simulation speed for fast visibility
                simulation_speed = 800 
                
                seg_dist_km = haversine(
                    current_stop.latitude, current_stop.longitude,
                    next_stop.latitude, next_stop.longitude
                )
                
                # Avoid division by zero
                seg_time_sec = (seg_dist_km / simulation_speed) * 3600 if seg_dist_km > 0 else 1.0
                
                # Update interval (2 seconds)
                update_interval = 2.0
                
                # Progress increment
                progress_step = update_interval / seg_time_sec
                
                # Calculate current progress on this segment
                dist_from_start = haversine(
                    current_stop.latitude, current_stop.longitude,
                    live.latitude, live.longitude
                )
                
                current_progress = dist_from_start / seg_dist_km if seg_dist_km > 0 else 1.0
                new_progress = current_progress + progress_step
                
                if new_progress >= 0.99:
                    # Arrived at stop
                    live.latitude = next_stop.latitude
                    live.longitude = next_stop.longitude
                    live.current_stop_index = next_idx
                    live.is_moving_forward = forward
                    live.stop_arrival_time = now # Start waiting timer
                    live.save()
                    
                    new_latitude = next_stop.latitude
                    new_longitude = next_stop.longitude
                    stop_name = next_stop.name
                    current_status = "ARRIVED"
                    progress_pct = 100
                    
                    current_idx = next_idx 

                else:
                    # Interpolation
                    total_lat_diff = next_stop.latitude - current_stop.latitude
                    total_lng_diff = next_stop.longitude - current_stop.longitude
                    
                    new_latitude = current_stop.latitude + (total_lat_diff * new_progress)
                    new_longitude = current_stop.longitude + (total_lng_diff * new_progress)
                    
                    live.latitude = new_latitude
                    live.longitude = new_longitude
                    live.last_moved_at = now
                    live.save()
                    
                    stop_name = f"En route to {next_stop.name}"
                    progress_pct = round(new_progress * 100, 1)

            # --- Logic 3: Calculate ETA (Embedded) ---
            stops_eta = []
            accumulated_time = 0
            temp_lat = new_latitude
            temp_lon = new_longitude
            
            # Determine path
            # SAFETY CHECK: Fix direction if stuck at terminal (same as ETAView)
            temp_forward = live.is_moving_forward
            if current_idx == 0 and not temp_forward:
                temp_forward = True
            elif current_idx == len(stops) - 1 and temp_forward:
                temp_forward = False

            stops_to_visit = stops[current_idx+1:] if temp_forward else stops[:current_idx][::-1]

            for next_s in stops_to_visit:
                dist = haversine(temp_lat, temp_lon, next_s.latitude, next_s.longitude)
                travel_time_min = (dist / bus_speed) * 60
                
                if accumulated_time > 0:
                    accumulated_time += (3 / 60) # 3s delay
                
                accumulated_time += travel_time_min
                
                stops_eta.append({
                    "stop_name": next_s.name,
                    "eta_minutes": max(1, round(accumulated_time)),
                    "order": next_s.order
                })
                
                temp_lat = next_s.latitude
                temp_lon = next_s.longitude
            
            # Robust Next Stop Name
            if stops_eta:
                next_stop_display = stops_eta[0]["stop_name"]
                first_eta = stops_eta[0]["eta_minutes"]
            else:
                next_stop_display = stops[current_idx].name
                first_eta = 0

            results.append({
                "bus_id": bus.id,
                "bus_no": bus.bus_number,
                "latitude": new_latitude,
                "longitude": new_longitude,
                "stop_name": stop_name,
                "status": current_status,
                "progress": progress_pct,
                # Indices for frontend interpolation
                "current_stop_index": current_idx,
                "next_stop_index": next_idx if current_status != "WAITING" else current_idx,
                "is_moving_forward": live.is_moving_forward,
                # Enriched Data
                "stops_eta": stops_eta,
                "next_stop": next_stop_display,
                "eta_minutes": first_eta,
                "speed": live.speed if current_status != "WAITING" else 0,
                "crowding": live.crowding
            })

        return Response(results)
