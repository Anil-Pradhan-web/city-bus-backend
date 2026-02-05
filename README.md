# 🚌 City-Bus Live - Backend

The robust Django REST Framework backend powering the City-Bus Live tracking system. This API handles bus management, route coordination, real-time location updates, and ETA calculations.

## 🛠️ Tech Stack

- **Framework**: Django 6.0 + Django REST Framework
- **Database**: SQLite3 (Development) / Scalable to PostgreSQL
- **Real-time**: Custom tracking logic with ETA interpolation
- **Security**: Token-based authentication for Admin actions

## 📂 Project Structure

```
transport_backend/
├── buses/          # Bus entity management & Schedules
├── routes/         # Route paths & sequences
├── stops/          # Bus stop locations (Lat/Lng)
├── tracking/       # Live location updates & ETA engine
├── feedback/       # User feedback collection
└── transport_backend/  # Project settings & configuration
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

## 🔌 API Endpoints

### 📍 Tracking
- `GET /api/tracking/live/`: Get all live buses
- `POST /api/tracking/move/<bus_id>/`: Update bus location (Admin/Driver)
- `GET /api/tracking/eta/<bus_id>/`: Get estimated arrival times

### 🚌 Buses & Routes
- `GET /api/buses/`: List all buses
- `GET /api/routes/`: List all routes
- `GET /api/routes/<id>/stops/`: Get stops for a specific route

### 📝 Feedback
- `POST /api/feedback/`: Submit user feedback

## 🔐 Admin Access

Django defines a built-in admin interface for managing data.
- URL: `http://127.0.0.1:8000/admin/`
- **Note**: You must create a superuser first using `python manage.py createsuperuser`.

## ⚙️ Configuration

Settings are located in `transport_backend/settings.py`.
- **CORS**: Configured to allow `localhost:5173` (Frontend).
- **DEBUG**: Set to `True` for development.
