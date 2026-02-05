from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .models import Route
from .serializers import RouteSerializer

from buses.models import Bus
from stops.models import Stop

class RouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def update_route(request, route_id):
    try:
        route = Route.objects.get(id=route_id)
    except Route.DoesNotExist:
        return Response(
           {"error": "Route not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'DELETE':
        route.delete()
        return Response({"message": "Route deleted successfully"}, status=status.HTTP_200_OK)
    
    if request.method == 'GET':
        serializer = RouteSerializer(route)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    serializer = RouteSerializer(route, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BusRouteView(APIView):
    def get(self, request, bus_no):
        bus = Bus.objects.filter(bus_number=str(bus_no)).first()
        if not bus:
            return Response({"error": "Bus not found"}, status=status.HTTP_404_NOT_FOUND)

        route = bus.route
        if not route:
            return Response({"error": "No route assigned", "stops": []}, status=status.HTTP_200_OK)

        stops = Stop.objects.filter(route=route).order_by("order")
        return Response({
            "bus_no": bus.bus_number,
            "stops": [{"stop_name": s.name, "latitude": s.latitude, "longitude": s.longitude} for s in stops]
        })

class TripPlannerView(APIView):
    def get(self, request):
        from_stop_name = request.query_params.get('from', '').strip()
        to_stop_name = request.query_params.get('to', '').strip()

        if not from_stop_name or not to_stop_name:
            return Response({"error": "Please provide 'from' and 'to' stop names"}, status=400)

        # 1. Find all potential start and end stop records
        start_stops = Stop.objects.filter(name__icontains=from_stop_name)
        end_stops = Stop.objects.filter(name__icontains=to_stop_name)

        if not start_stops.exists() or not end_stops.exists():
            return Response({"error": "Stops not found", "results": []})

        trip_results = []
        direct_routes_found = False

        from tracking.utils import haversine

        # Helper to calculate route distance
        def get_route_distance(route_id, start_order, end_order):
            if start_order == end_order: return 0
            
            # Ensure order
            s_ord = min(start_order, end_order)
            e_ord = max(start_order, end_order)
            
            stops = list(Stop.objects.filter(route_id=route_id, order__gte=s_ord, order__lte=e_ord).order_by('order'))
            total_dist = 0
            for i in range(len(stops) - 1):
                total_dist += haversine(
                    stops[i].latitude, stops[i].longitude,
                    stops[i+1].latitude, stops[i+1].longitude
                )
            return total_dist

        # --- Strategy 1: Direct Routes ---
        for start in start_stops:
            for end in end_stops:
                # Case 1: Forward Direction
                if start.route == end.route and start.order < end.order:
                    route = start.route
                    buses = route.buses.filter(is_active=True)
                    bus_numbers = [b.bus_number for b in buses]
                    
                    dist_km = get_route_distance(route.id, start.order, end.order)
                    fare = max(5, round(dist_km * 5)) # Min fare 5 rs

                    trip_results.append({
                        "type": "Direct",
                        "route_name": route.name,
                        "bus_numbers": bus_numbers,
                        "start_stop": start.name,
                        "end_stop": end.name,
                        "stops_count": end.order - start.order,
                        "fare_estimate": fare
                    })
                    direct_routes_found = True

                # Case 2: Reverse Direction (Heuristic Support)
                elif start.route == end.route and start.order > end.order:
                    route = start.route
                    buses = route.buses.filter(is_active=True)
                    bus_numbers = [b.bus_number for b in buses]
                    
                    dist_km = get_route_distance(route.id, start.order, end.order)
                    fare = max(5, round(dist_km * 5))

                    trip_results.append({
                        "type": "Direct",
                        "route_name": f"{route.name} (Return)",
                        "bus_numbers": bus_numbers,
                        "start_stop": start.name,
                        "end_stop": end.name,
                        "stops_count": start.order - end.order,
                        "fare_estimate": fare
                    })
                    direct_routes_found = True

        # --- Strategy 2: One-Hop Transfer ---
        start_routes = {s.route.id: s for s in start_stops}
        end_routes = {s.route.id: s for s in end_stops}

        for r1_id, s1_obj in start_routes.items():
            potential_transfer_stops = Stop.objects.filter(route_id=r1_id, order__gt=s1_obj.order)
            
            for t_stop in potential_transfer_stops:
                for r2_id, s2_obj in end_routes.items():
                    if r1_id == r2_id: continue 
                    
                    matching_transfer = Stop.objects.filter(
                        route_id=r2_id, 
                        name__iexact=t_stop.name, 
                        order__lt=s2_obj.order
                    ).first()
                    
                    if matching_transfer:
                        route1 = s1_obj.route
                        route2 = s2_obj.route
                        
                        dist1 = get_route_distance(route1.id, s1_obj.order, t_stop.order)
                        dist2 = get_route_distance(route2.id, matching_transfer.order, s2_obj.order)
                        
                        total_fare = max(10, round((dist1 + dist2) * 5)) # Min 10 for transfer

                        buses1 = [b.bus_number for b in route1.buses.filter(is_active=True)]
                        buses2 = [b.bus_number for b in route2.buses.filter(is_active=True)]

                        trip_results.append({
                            "type": "Transfer",
                            "start_stop": s1_obj.name,
                            "end_stop": s2_obj.name,
                            "total_stops": (t_stop.order - s1_obj.order) + (s2_obj.order - matching_transfer.order),
                            "fare_estimate": total_fare,
                            "legs": [
                                {
                                    "route_name": route1.name,
                                    "bus_numbers": buses1,
                                    "from": s1_obj.name,
                                    "to": t_stop.name,
                                    "stops": t_stop.order - s1_obj.order
                                },
                                {
                                    "route_name": route2.name,
                                    "bus_numbers": buses2,
                                    "from": matching_transfer.name,
                                    "to": s2_obj.name,
                                    "stops": s2_obj.order - matching_transfer.order
                                }
                            ],
                            "transfer_at": t_stop.name
                        })


        # Deduplicate results roughly (by route names)
        # Using a dictionary key for uniqueness
        unique_results = {}
        for res in trip_results:
            if res['type'] == 'Direct':
                key = f"D-{res['route_name']}"
            else:
                key = f"T-{res['legs'][0]['route_name']}-{res['legs'][1]['route_name']}"
            
            if key not in unique_results:
                unique_results[key] = res
                
        final_list = list(unique_results.values())
        
        # Sort: Direct first, then by total stops
        final_list.sort(key=lambda x: (0 if x['type'] == 'Direct' else 1, x.get('stops_count', x.get('total_stops', 999))))

        return Response({"results": final_list})

class SearchSuggestionsView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', 'all') # 'stop', 'bus', 'all'
        
        if not query:
            return Response([])
            
        results = []
        
        # Search Stops
        if search_type in ['all', 'stop']:
            stops = Stop.objects.filter(name__icontains=query).values_list('name', flat=True).distinct()[:5]
            for stop in stops:
                results.append({"type": "stop", "value": stop, "label": f"📍 {stop}"})
                
        # Search Buses/Routes
        if search_type in ['all', 'bus']:
            # Search by bus number
            buses = Bus.objects.filter(bus_number__icontains=query).values_list('bus_number', flat=True).distinct()[:5]
            for bus in buses:
                results.append({"type": "bus", "value": bus, "label": f"🚌 Bus {bus}"})
                
            # Search by route name
            routes = Route.objects.filter(name__icontains=query).values_list('name', flat=True).distinct()[:3]
            for route_name in routes:
                 # Try to find a bus on this route to give a bus context, or just show route name
                 # Here we just show route name, client can interpret
                 results.append({"type": "route", "value": route_name, "label": f"🛣️ {route_name}"})

        return Response(results)
