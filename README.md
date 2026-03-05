# Smart Parking Detection System – YOLOv8 + FastAPI + React

An AI-powered parking monitoring system that detects vehicles using YOLOv8 and automatically updates parking slot availability in real time. The system includes an admin dashboard, live detection stream, slot booking system, and video analysis pipeline.

## Features

- AI vehicle detection using YOLOv8
- Real-time parking slot monitoring
- Admin dashboard with analytics
- Parking slot booking system
- Live detection video stream
- Exit-line tracking for vehicle departure
- Automatic database updates
- FastAPI backend
- React + Vite frontend

## System Architecture

**Backend:**
- FastAPI API server
- YOLOv8 detection engine
- SQLite database
- OpenCV video processing

**Frontend:**
- React + Vite dashboard
- Admin panel
- Slot monitoring UI

## Project Folder Structure

```text
parksmart-dashboard/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── parking_detection.py
│   ├── routes/
│   │   ├── upload_video.py
│   │   ├── booking.py
│   │   └── slots.py
│   ├── uploads/
│   └── parksmart.db
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   └── package.json
│
└── README.md
```

## Local Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/SriRamkunamsetty/parksmart-dashboard.git
cd parksmart-dashboard
```

### 2. Install Backend Dependencies

Go to the backend folder:
```bash
cd backend
```

Create a virtual environment:
```bash
python -m venv venv
```

Activate the environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run Backend Server
```bash
uvicorn main:app --reload
```

Server will run on:
`http://localhost:8000`

API documentation:
`http://localhost:8000/docs`

## Frontend Setup

Go to the frontend folder:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

Run the development server:
```bash
npm run dev
```

Frontend runs at:
`http://localhost:8080` (or depending on your Vite config, often `http://localhost:5173`)

## How to Use the System

### 1. Open Admin Dashboard
Navigate to `http://localhost:8080/admin` in your web browser.

### 2. Upload Parking Video
1. Upload a `.mp4` parking lot video on the admin panel.
2. The system will start YOLO vehicle detection, detect cars in parking slots, and automatically update slot availability.

### 3. Live Detection
The admin dashboard displays:
- Parking slot polygons
- Vehicle bounding boxes
- Exit detection line
- Slot status directly overlaid on the live stream

### 4. Slot Status Logic
- **Blue** → Available
- **Red** → Occupied
- **Yellow** → Reserved

### 5. Exit Line Tracking
When a vehicle crosses the exit line, the system automatically marks the slot as available.

## Database

- **Database used:** SQLite
- **File location:** `backend/parksmart.db`
- **Slots table contains:** `slot_id`, `slot_number`, `status`

## API Endpoints

- `POST /upload-parking-video`
- `GET /slots`
- `GET /slot-stats`
- `GET /analysis-status`
- `POST /start-analysis`
- `POST /stop-analysis`
- `POST /reset-slots`

## Demo Workflow

1. Start backend
2. Start frontend
3. Open admin dashboard
4. Upload parking video
5. Watch real-time detection as slot availability updates automatically

## Technologies Used

- Python
- FastAPI
- YOLOv8
- OpenCV
- React
- Vite
- SQLite

## License

MIT License

## Contribution

Contributions are welcome. Please fork the repository and submit pull requests.

## Author

**SriRam Kunamsetty**
Smart Parking Detection System Project
