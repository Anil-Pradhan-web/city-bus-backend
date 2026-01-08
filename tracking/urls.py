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

    # ⏱ ETA 
    path("eta/<str:bus_no>/", BusETAView.as_view()),

    # 🛣 route + stops
    path("route/<str:bus_no>/", BusRouteView.as_view()),

    # 🚌 move bus simulation
    path("move-bus/<str:bus_no>/", MoveBusView.as_view()),
]

