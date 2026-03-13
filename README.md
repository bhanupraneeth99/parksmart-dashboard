# A Real-Time Intelligent Parking Management System using YOLOv11 and FastAPI

A full-stack intelligent parking management system using **YOLOv11 computer vision** to detect vehicle occupancy from CCTV footage in real-time. Features an Admin Dashboard for monitoring and a Customer Dashboard for booking available slots.

---

## 🚀 Quick Start

### One-Command Launch

**Windows (PowerShell):**
```powershell
.\run_system.ps1
```

**Linux / macOS (Bash):**
```bash
chmod +x run_system.sh
./run_system.sh
```

This automatically sets up the environment, starts all services, and opens the dashboard.

> 📖 For detailed manual setup, see [HOW_TO_RUN.md](HOW_TO_RUN.md)

---

## 🧠 Tech Stack

### Frontend
- React + TypeScript
- Vite
- TailwindCSS
- Zustand (State Management)
- WebSockets (Real-Time Updates)

### Backend
- FastAPI + Uvicorn
- SQLAlchemy + SQLite
- APScheduler (Booking Expiry)

### AI / Computer Vision
- YOLOv11 (Ultralytics)
- OpenCV
- MJPEG Video Streaming

---

## ✨ Core Features

### AI Parking Detection
- Detects **Cars, Motorcycles, Buses, and Trucks** using YOLOv11
- Determines slot occupancy via **centroid-inside-polygon** and **IoU > 0.25**
- **Temporal smoothing**: 3 consecutive frame detections required to confirm occupancy

### Detection Worker Pipeline
- `DetectionManager` spawns `CameraWorker` threads
- Reads video frames → Runs YOLO inference → Evaluates slot occupancy → Updates database → Broadcasts via WebSocket

### Real-Time WebSocket Updates
```json
{
  "event": "slot_update",
  "slot_id": "S1",
  "status": "occupied",
  "timestamp": "2026-03-11T09:00:00Z"
}
```

### Admin Dashboard (`/admin`)
- Live CCTV video monitoring
- Parking slot polygon configuration
- Slot editing, deletion, and heatmap analytics

### Customer Dashboard (`/dashboard`)
- View live slot availability
- Book available slots
- Cancel bookings and view history

Slot colors: 🟢 Available → 🟡 Reserved → 🔴 Occupied

### Booking System
- Reservations auto-expire after 10 minutes if the vehicle doesn't arrive
- Background scheduler handles expired reservations

---

## 🏗️ System Architecture

```text
CCTV / Video File
       ↓
CameraWorker (YOLOv11 Detection)
       ↓
Slot Occupancy Engine (Polygon + Centroid)
       ↓
SQLite Database
       ↓
FastAPI API Server
       ↓
WebSocket Broadcast
       ↓
React Frontend (Admin + Customer Dashboards)
```

---

## 📁 Project Structure

```text
parksmart-dashboard/
│
├── backend/
│   ├── main.py                  # FastAPI application entry point
│   ├── worker.py                # AI detection worker pipeline
│   ├── models.py                # SQLAlchemy database models
│   ├── database.py              # Database connection and session
│   ├── init_db_and_seed.py      # Database initialization and seeding
│   ├── routes/
│   │   ├── booking.py           # Booking API endpoints
│   │   ├── slots.py             # Parking slot API endpoints
│   │   ├── upload_video.py      # Video upload and demo trigger
│   │   ├── debug.py             # Pipeline diagnostics
│   │   └── system.py            # System health endpoints
│   ├── services/
│   │   ├── slot_service.py      # Slot evaluation logic
│   │   ├── detection_service.py # YOLO detection service
│   │   └── tracking_service.py  # Vehicle tracking
│   └── utils/
│       ├── frame_utils.py       # Frame processing and overlay
│       ├── geometry_utils.py    # Polygon geometry helpers
│       └── logging_utils.py     # Logging configuration
│
├── src/                         # React frontend source
│   ├── pages/
│   │   ├── AdminDashboard.tsx   # Admin monitoring interface
│   │   └── Index.tsx            # Customer booking interface
│   ├── store/
│   │   └── parkingStore.ts      # Zustand state management
│   └── components/              # Reusable UI components
│
├── run_system.ps1               # Windows one-command startup
├── run_system.sh                # Linux one-command startup
├── worker_watchdog.py           # Auto-recovery watchdog
├── verify_system.py             # System health verification
├── trigger_worker.py            # Manual worker trigger
├── parking_video.mp4            # Demo parking video
└── HOW_TO_RUN.md                # Detailed setup guide
```

---

## 🗄️ Database Schema

### ParkingSlot
| Column | Type | Description |
|--------|------|-------------|
| id | String | Slot ID (S1–S7) |
| number | String | Slot number |
| status | String | available / occupied / reserved |
| polygon | JSON | 4-point polygon coordinates |

### Booking
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Booking ID |
| slot_id | String | Foreign key to ParkingSlot |
| status | String | active / expired / cancelled |
| booking_time | DateTime | When booking was made |
| expiry_time | DateTime | Auto-expiry timestamp |

### ProcessingJob
| Column | Type | Description |
|--------|------|-------------|
| job_id | String | Unique job identifier |
| video_path | String | Path to video file |
| status | String | processing / completed / failed |

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/system/health` | System health check |
| GET | `/api/debug/pipeline` | AI pipeline diagnostics |
| GET | `/api/slots` | List all parking slots |
| GET | `/api/slots/{id}` | Get specific slot |
| POST | `/api/jobs/start-demo` | Trigger AI worker |
| GET | `/api/video/stream` | Live MJPEG video stream |
| POST | `/api/bookings` | Create a booking |
| GET | `/api/bookings` | List bookings |

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 5173 refused | Run `npm run dev` in project root |
| Port 8000 refused | Run `uvicorn main:app` in backend/ |
| Video not found | Place `parking_video.mp4` in project root |
| Database errors | Delete `parksmart.db` and re-run `python init_db_and_seed.py` |
| Worker stuck | Run `python worker_watchdog.py` for auto-recovery |

---

## 📄 License

This project is for educational and demonstration purposes.
