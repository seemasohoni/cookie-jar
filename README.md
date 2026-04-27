# Cookie Jar 🍪

**Master your habits, fill your jar.**

Cookie Jar is a habit-tracking web application that helps you track both good and bad habits. It visualizes your progress by filling up a virtual Glassmorphism "Cookie Jar" as you successfully complete your good habits, while helping you analyze your bad habit triggers and times of vulnerability.

## Architecture

The project is split up into two main components:

### Frontend
A pure, static Javascript & CSS frontend, using `Chart.js` for dynamic SVG charting to help visualize your vulnerability zones and triggers.
- No build tools required! It runs natively in your browser.
- Uses stunning glassmorphism design parameters and rich aesthetics.

### Backend
A lightweight, fast Python `FastAPI` server. 
- Serves the frontend by managing habits, persisting logs, tracking streaks, and calculating complex analytical pattern graphs for your habits.

## How to Run

### 1. Start the Backend API
First, ensure you have Python 3 installed.
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
This will start the hot-reloading backend on `http://localhost:8000`.

### 2. Start the Frontend Application
In a new terminal window, serve the static frontend files:
```bash
cd frontend
python3 -m http.server 8001
```
Open `http://localhost:8001` in your browser to view the application!

## Features

- **The Cookie Jar:** Visual progression metric showing your completion towards your next 100-cookie milestone.
- **Pattern Analyzer:** Identifies your most vulnerable times of day (when you're most likely to give into a bad habit) plotted on a time-series graph.
- **Trigger Identifiers:** Categorize exactly *why* a habit occurred (e.g. Social, Time, Location) with donut charts mapping out your primary causes.
- **Inline Logbooks:** Keep detailed, timestamped records for every specific habit you track.
