# How to Run — Smart Parking AI System

A step-by-step guide to run the entire Smart Parking AI system locally.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |
| Git | Latest |

---

## Option A — One-Command Startup (Recommended)

### Windows (PowerShell)
```powershell
.\run_system.ps1
```

### Linux / macOS (Bash)
```bash
chmod +x run_system.sh
./run_system.sh
```

This will automatically:
1. Setup the Python virtual environment
2. Install all backend and frontend dependencies
3. Initialize the SQLite database and seed parking slots S1–S7
4. Start the Backend API on `http://localhost:8000`
5. Start the Frontend Dashboard on `http://localhost:5173`
6. Trigger the AI Worker to process `parking_video.mp4`
7. Start the Worker Watchdog for auto-recovery
8. Open the Admin Dashboard in your browser

---

## Option B — Manual Step-by-Step

### Step 1 — Clone the Repository
```bash
git clone https://github.com/SriRamkunamsetty/parksmart-dashboard.git
cd parksmart-dashboard
```

### Step 2 — Setup Python Environment
```bash
cd backend
python -m venv venv
```

Activate the virtual environment:

**Windows:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### Step 3 — Initialize the Database
```bash
python init_db_and_seed.py
```

This will:
- Create the SQLite database (`parksmart.db`)
- Create all required tables (ParkingSlot, ProcessingJob, Booking, etc.)
- Seed parking slots S1–S7 with polygon coordinates

### Step 4 — Start the Backend Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Verify it's running:
- Health check: http://localhost:8000/api/system/health
- API docs: http://localhost:8000/docs

### Step 5 — Start the Frontend Dashboard
Open a **new terminal** in the project root:
```bash
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

### Step 6 — Trigger the AI Worker
Open a **new terminal** and call the demo endpoint:

**Using curl:**
```bash
curl -X POST http://localhost:8000/api/jobs/start-demo \
     -H "Content-Type: application/json" \
     -d '{"video":"parking_video.mp4"}'
```

**Using PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/jobs/start-demo" -Method POST -Body '{"video":"parking_video.mp4"}' -ContentType "application/json"
```

### Step 7 — Open the Dashboard
Open your browser and navigate to:
- **Admin Dashboard:** http://localhost:5173/admin
- **Customer Dashboard:** http://localhost:5173/dashboard

### Step 8 — Verify the System
Check the AI pipeline status:
```bash
curl http://localhost:8000/api/debug/pipeline
```

Expected output:
```json
{
  "worker_state": "RUNNING",
  "frames_processed": 120,
  "model_loaded": true,
  "inference_time_ms": 64
}
```

---

## Optional — Worker Watchdog

The watchdog monitors the AI pipeline and auto-restarts it on failure:
```bash
python worker_watchdog.py
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ERR_CONNECTION_REFUSED` on port 5173 | Run `npm run dev` in the project root |
| `ERR_CONNECTION_REFUSED` on port 8000 | Run `uvicorn main:app` in the backend directory |
| Backend timeout during startup | Ensure no other process is using port 8000 |
| `parking_video.mp4` not found | Place the video file in the project root directory |
| Database errors | Delete `parksmart.db` and re-run `python init_db_and_seed.py` |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/system/health` | System health check |
| GET | `/api/debug/pipeline` | AI pipeline diagnostics |
| GET | `/api/slots` | List all parking slots |
| POST | `/api/jobs/start-demo` | Trigger AI worker |
| GET | `/api/video/stream` | Live MJPEG video stream |
| POST | `/api/bookings` | Book a parking slot |
