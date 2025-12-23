from django.urls import path
from .views import (
    UpdateLocationView,
    CurrentLocationView,
    BusETAView,
    BusRouteView,
    MoveBusView,
)

urlpatterns = [
    # 🛰 live location update
    path("update/", UpdateLocationView.as_view()),

    # 📍 current bus location
    path("location/<int:bus_id>/", CurrentLocationView.as_view()),

    # ⏱ ETA (🔥 THIS WAS MISSING)
    path("eta/<int:bus_no>/", BusETAView.as_view()),

    # 🛣 route + stops
    path("route/<int:bus_no>/", BusRouteView.as_view()),

    # 🚌 move bus simulation
    path("move-bus/<int:bus_no>/", MoveBusView.as_view()),
]

