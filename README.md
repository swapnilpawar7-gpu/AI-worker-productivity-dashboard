# AI-Powered Worker Productivity Dashboard

## Overview

This project is a **production-style analytics web application** that ingests AI-generated CCTV events from a factory floor, stores them in a database, computes productivity metrics, and displays them in a clear dashboard.

> **Important scope note:** The task focuses on *what happens after AI*. No computer-vision or ML models are trained here; the system assumes structured events are already produced by AI cameras.

---

## Architecture Overview

**Edge → Backend → Database → Dashboard**

1. **Edge (AI Cameras)**
   AI-powered CCTV systems emit structured JSON events (e.g., `working`, `idle`, `product_count`).

2. **Backend (Flask API)**

   * Accepts events via APIs
   * Persists all data in SQLite
   * Computes productivity metrics on demand

3. **Database (SQLite)**

   * Stores workers, workstations, and events
   * Auto-created on first run

4. **Frontend (HTML + CSS + JavaScript)**

   * Fetches computed metrics from backend APIs
   * Displays factory-, worker-, and workstation-level insights

This separation mirrors real production systems where ingestion, storage, computation, and visualization are decoupled.

---

## Technology Stack

* **Backend:** Python, Flask
* **Database:** SQLite
* **Frontend:** HTML, CSS, Vanilla JavaScript
* **Containerization:** Docker, Docker Compose (files provided)

---

## Database Schema

### Workers

| Field     | Type      | Description              |
| --------- | --------- | ------------------------ |
| worker_id | TEXT (PK) | Unique worker identifier |
| name      | TEXT      | Worker name              |

### Workstations

| Field      | Type      | Description                   |
| ---------- | --------- | ----------------------------- |
| station_id | TEXT (PK) | Unique workstation identifier |
| name       | TEXT      | Station name/type             |

### Events

| Field          | Type            | Description                                  |
| -------------- | --------------- | -------------------------------------------- |
| id             | INTEGER (PK)    | Auto-incremented ID                          |
| timestamp      | TEXT (ISO-8601) | Event time                                   |
| worker_id      | TEXT            | Associated worker                            |
| workstation_id | TEXT            | Associated workstation                       |
| event_type     | TEXT            | `working`, `idle`, `absent`, `product_count` |
| confidence     | REAL            | AI confidence score                          |
| count          | INTEGER         | Units produced (for `product_count`)         |

All events are persisted; metrics are derived dynamically.

---

## Backend APIs

### Seed / Reset Dummy Data

```
POST /seed
```

* Clears existing data
* Inserts deterministic dummy workers, workstations, and events
* Allows evaluators to reset the system **without editing the database or frontend code**

### Metrics APIs

```
GET /metrics/factory
GET /metrics/workers
GET /metrics/workstations
```

These endpoints return fully computed metrics (no frontend-side calculations).

---

## Metrics Definitions

### Worker-Level Metrics

* **Total Active Time:** Sum of durations between `working` events
* **Total Idle Time:** Sum of durations between `idle` events
* **Utilization %:**
  `active_time / (active_time + idle_time) × 100`
* **Total Units Produced:** Sum of `count` from `product_count` events
* **Units per Hour:**
  `total_units / active_time`

### Workstation-Level Metrics

* **Occupancy Time:** Total time the station is occupied
* **Utilization %:** Occupancy relative to available time
* **Total Units Produced:** Sum of production at that station
* **Throughput Rate:** Units produced per hour

### Factory-Level Metrics

* **Total Productive Time:** Sum of all worker active times
* **Total Production Count:** Sum of all production events
* **Average Production Rate:** Aggregate units per hour
* **Average Utilization:** Mean utilization across workers

---

## Assumptions & Tradeoffs

### Time Modeling

* Events are sorted by timestamp before aggregation
* Time between consecutive events represents the duration of the previous state
* The last event duration is capped at the computation time

### Production Events

* `product_count` events affect production totals
* They do **not** directly contribute to time-based activity

### Deterministic Seed Data

* Seed data is deterministic to ensure reproducibility
* Resetting the database produces the same aggregate metrics by design

### Tradeoffs

* SQLite chosen for simplicity and portability
* Metrics computed on demand instead of pre-aggregation for correctness

---

## Handling Real-World Data Issues

### Intermittent Connectivity

Events are stored whenever they arrive. If a camera sends events late due to network issues, the backend still accepts them and includes them in future metric calculations.

### Duplicate Events

Duplicate events are handled logically by checking key fields such as timestamp, worker ID, and event type. This prevents the same activity from being counted multiple times.

### Out-of-Order Timestamps

Before computing metrics, events are sorted by timestamp. This ensures time-based calculations (like active or idle duration) remain correct even if events arrive out of order.

---

## Model Lifecycle (Theoretical)

### Model Versioning

Each event can include a `model_version` field. This allows tracking which AI model produced which events and comparing performance across versions.

### Detecting Model Drift

Drift can be detected by monitoring changes in confidence scores and activity patterns over time. Significant deviations from historical behavior can indicate model drift.

### Triggering Retraining

Retraining can be triggered periodically (e.g., monthly) or automatically when drift exceeds a defined threshold. This ensures the AI model remains accurate as conditions change.

---

## Scalability

### From 5 Cameras to 100+ Cameras

The backend is stateless, allowing multiple instances to run in parallel. Event ingestion can be scaled using message queues, and database indexing ensures performance at higher volumes.

### Multi-Site Scaling

A `site_id` can be added to events to distinguish between factory locations. Data can be partitioned per site while using a centralized dashboard to monitor all factories.

---

> **One-line takeaway:** This design mirrors real production systems by separating data ingestion, processing, and visualization, making it reliable, scalable, and easy to extend.

---

## Running the Application Locally

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Runs on: `http://127.0.0.1:5000`

### Frontend

```bash
cd frontend
python -m http.server 8080
```

Open: `http://localhost:8080`

### Initialize Dummy Data

```
POST http://127.0.0.1:5000/seed
```

---

## Docker (Optional)

Dockerfiles and `docker-compose.yml` are provided for containerized execution:

```bash
docker compose up --build
```

---

## Web Application Link

When running locally:

```
http://localhost:8080
```

---

## Summary

This project demonstrates backend-centric system design, data modeling, metric computation, and production-style architecture for AI-driven factory analytics, aligned precisely with the assessment requirements.