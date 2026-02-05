# 🚌 City-Bus Live - Backend

The robust Django REST Framework backend powering the City-Bus Live tracking system. This API handles bus management, route coordination, real-time location updates, distance-based fare logic, and intelligent trip planning.

## 🛠️ Tech Stack

- **Framework**: Django 4.2+ & Django REST Framework
- **Authentication**: JWT & SimpleJWT for secure API access
- **Real-time Engine**: Smooth interpolation logic for bus movement simulation
- **Geography**: Haversine formula for precise KM-based distance and fare calculation
- **Database**: SQLite3 (Development)

## 📂 Project Structure

```
transport_backend/
├── buses/          # Bus entity management & registrations
├── routes/         # Intelligent Trip Planning & Route sequence logic
├── stops/          # Geo-coordinated stop locations
├── tracking/       # Live location engine & ETA calculations
├── users/          # Custom User model & Auth logic
├── feedback/       # Contact & User feedback storage
└── transport_backend/ # Core project settings
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip (Python package manager)

### Installation

1. **Navigate to the backend directory:**
   ```bash
   cd transport_backend
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start the Server:**
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://127.0.0.1:8000/`.

## 🧠 Advanced Features

### 🗺️ Intelligent Trip Planner
The backend implements a sophisticated search algorithm:
- **Direct Routes**: Finds single buses connecting two points.
- **One-Hop Transfers**: Identifies optimal transfer points between intersecting routes.
- **Directional Logic**: Handles both forward and return route sequences.

### 💸 Distance-Based Fare System
Replaced stop-based pricing with actual geographic distance:
- **Logic**: Uses the Haversine formula to compute KM distance between stops.
- **Rate**: Standardized at ₹5 per Kilometer.
- **Minimums**: Guaranteed minimum fare for short hops.

### 🛰️ Live Tracking Engine
- **Interpolation**: Smooth movement between stops (no teleporting).
- **ETA**: Dynamic arrival estimates for all upcoming stops based on current bus speed.

## 🔐 Data Management (Django Admin)
The system is designed to be managed primarily through the built-in Django Admin panel.
- URL: `http://127.0.0.1:8000/admin/`
- **Setup**: Use `python manage.py createsuperuser` to set up access.

---
Maintained by [Anil](https://github.com/Anil-Pradhan-web)
