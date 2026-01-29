"""
AI-Powered Worker Productivity Dashboard - Flask Backend
=========================================================
This Flask application serves as the backend for processing AI camera events
and computing productivity metrics for workers, workstations, and factory-level analytics.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from database import init_db, get_db_connection
from datetime import datetime, timezone
import json

app = Flask(__name__)
CORS(app)

# Initialize database on startup
init_db()


def parse_iso_timestamp(ts_string):
    """Parse ISO 8601 timestamp string to datetime object."""
    if ts_string.endswith('Z'):
        ts_string = ts_string[:-1] + '+00:00'
    return datetime.fromisoformat(ts_string)


def get_current_time():
    """Get current UTC time for metric calculations."""
    return datetime.now(timezone.utc)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()})


@app.route('/seed', methods=['POST'])
def seed_database():
    """
    Seed the database with sample data.
    Deletes all existing data and recreates workers, workstations, and sample events.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Clear existing data
        cursor.execute("DELETE FROM events")
        cursor.execute("DELETE FROM workers")
        cursor.execute("DELETE FROM workstations")
        
        # Seed workers (W1-W6)
        workers = [
            ("W1", "Lionel Messi"),
            ("W2", "Neymar Jr."),
            ("W3", "Luiz Saurez"),
            ("W4", "David Beckham"),
            ("W5", "Lautero Martinez"),
            ("W6", "Roberto Carlos")
        ]
        cursor.executemany("INSERT INTO workers (worker_id, name) VALUES (?, ?)", workers)
        
        # Seed workstations (S1-S6)
        workstations = [
            ("S1", "Assembly Line A"),
            ("S2", "Assembly Line B"),
            ("S3", "Quality Control"),
            ("S4", "Packaging Station"),
            ("S5", "Inspection Bay"),
            ("S6", "Finishing Station")
        ]
        cursor.executemany("INSERT INTO workstations (station_id, name) VALUES (?, ?)", workstations)
        
        # Seed sample events - realistic production day simulation
        # Using dates in the past for consistency
        base_date = "2026-01-15"
        
        sample_events = [
            # Worker W1 at Station S1 - Full shift
            (f"{base_date}T08:00:00Z", "W1", "S1", "working", 0.95, None),
            (f"{base_date}T10:00:00Z", "W1", "S1", "product_count", 0.98, 25),
            (f"{base_date}T10:30:00Z", "W1", "S1", "idle", 0.87, None),
            (f"{base_date}T10:45:00Z", "W1", "S1", "working", 0.92, None),
            (f"{base_date}T12:00:00Z", "W1", "S1", "product_count", 0.96, 18),
            (f"{base_date}T12:30:00Z", "W1", "S1", "idle", 0.89, None),
            (f"{base_date}T13:00:00Z", "W1", "S1", "working", 0.94, None),
            (f"{base_date}T15:00:00Z", "W1", "S1", "product_count", 0.97, 30),
            (f"{base_date}T16:00:00Z", "W1", "S1", "absent", 0.91, None),
            
            # Worker W2 at Station S2 - High productivity
            (f"{base_date}T08:00:00Z", "W2", "S2", "working", 0.96, None),
            (f"{base_date}T09:30:00Z", "W2", "S2", "product_count", 0.99, 35),
            (f"{base_date}T11:00:00Z", "W2", "S2", "product_count", 0.97, 40),
            (f"{base_date}T12:00:00Z", "W2", "S2", "idle", 0.85, None),
            (f"{base_date}T12:30:00Z", "W2", "S2", "working", 0.93, None),
            (f"{base_date}T14:00:00Z", "W2", "S2", "product_count", 0.98, 38),
            (f"{base_date}T15:30:00Z", "W2", "S2", "product_count", 0.96, 32),
            (f"{base_date}T16:00:00Z", "W2", "S2", "absent", 0.92, None),
            
            # Worker W3 at Station S3 - Quality Control
            (f"{base_date}T08:30:00Z", "W3", "S3", "working", 0.94, None),
            (f"{base_date}T10:00:00Z", "W3", "S3", "product_count", 0.95, 50),
            (f"{base_date}T11:30:00Z", "W3", "S3", "idle", 0.88, None),
            (f"{base_date}T12:00:00Z", "W3", "S3", "working", 0.91, None),
            (f"{base_date}T13:30:00Z", "W3", "S3", "product_count", 0.97, 55),
            (f"{base_date}T15:00:00Z", "W3", "S3", "product_count", 0.94, 45),
            (f"{base_date}T16:00:00Z", "W3", "S3", "absent", 0.90, None),
            
            # Worker W4 at Station S4 - Packaging
            (f"{base_date}T08:00:00Z", "W4", "S4", "working", 0.93, None),
            (f"{base_date}T09:00:00Z", "W4", "S4", "idle", 0.82, None),
            (f"{base_date}T09:30:00Z", "W4", "S4", "working", 0.95, None),
            (f"{base_date}T11:00:00Z", "W4", "S4", "product_count", 0.96, 60),
            (f"{base_date}T12:30:00Z", "W4", "S4", "idle", 0.86, None),
            (f"{base_date}T13:00:00Z", "W4", "S4", "working", 0.92, None),
            (f"{base_date}T14:30:00Z", "W4", "S4", "product_count", 0.98, 55),
            (f"{base_date}T16:00:00Z", "W4", "S4", "absent", 0.89, None),
            
            # Worker W5 at Station S5 - Inspection
            (f"{base_date}T08:00:00Z", "W5", "S5", "working", 0.97, None),
            (f"{base_date}T10:30:00Z", "W5", "S5", "product_count", 0.95, 70),
            (f"{base_date}T11:00:00Z", "W5", "S5", "idle", 0.84, None),
            (f"{base_date}T11:30:00Z", "W5", "S5", "working", 0.93, None),
            (f"{base_date}T13:00:00Z", "W5", "S5", "product_count", 0.96, 65),
            (f"{base_date}T14:30:00Z", "W5", "S5", "product_count", 0.97, 60),
            (f"{base_date}T16:00:00Z", "W5", "S5", "absent", 0.91, None),
            
            # Worker W6 at Station S6 - Finishing (moves between stations)
            (f"{base_date}T08:00:00Z", "W6", "S6", "working", 0.94, None),
            (f"{base_date}T09:30:00Z", "W6", "S6", "product_count", 0.92, 20),
            (f"{base_date}T10:00:00Z", "W6", "S1", "working", 0.95, None),
            (f"{base_date}T11:00:00Z", "W6", "S1", "product_count", 0.93, 15),
            (f"{base_date}T11:30:00Z", "W6", "S6", "idle", 0.86, None),
            (f"{base_date}T12:00:00Z", "W6", "S6", "working", 0.91, None),
            (f"{base_date}T14:00:00Z", "W6", "S6", "product_count", 0.97, 25),
            (f"{base_date}T15:30:00Z", "W6", "S6", "product_count", 0.94, 22),
            (f"{base_date}T16:00:00Z", "W6", "S6", "absent", 0.90, None),
        ]
        
        cursor.executemany(
            """INSERT INTO events (timestamp, worker_id, station_id, event_type, confidence, count) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            sample_events
        )
        
        conn.commit()
        
        return jsonify({
            "status": "success",
            "message": "Database seeded successfully",
            "data": {
                "workers": len(workers),
                "workstations": len(workstations),
                "events": len(sample_events)
            }
        }), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()


@app.route('/events', methods=['POST'])
def ingest_events():
    """
    Ingest single or batch events from AI cameras.
    
    Accepts either a single event object or an array of events.
    Handles duplicate detection via (timestamp, worker_id, event_type) composite key.
    """
    data = request.get_json()
    
    if data is None:
        return jsonify({"status": "error", "message": "No JSON data provided"}), 400
    
    # Normalize to list for batch processing
    events = data if isinstance(data, list) else [data]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    inserted = 0
    duplicates = 0
    errors = []
    
    try:
        for event in events:
            # Validate required fields
            required_fields = ['timestamp', 'worker_id', 'event_type']
            missing = [f for f in required_fields if f not in event]
            if missing:
                errors.append(f"Missing fields: {missing}")
                continue
            
            # Validate event type
            valid_types = ['working', 'idle', 'absent', 'product_count']
            if event['event_type'] not in valid_types:
                errors.append(f"Invalid event_type: {event['event_type']}")
                continue
            
            # Handle workstation_id vs station_id naming
            station_id = event.get('workstation_id') or event.get('station_id')
            
            # Check for duplicates (timestamp, worker_id, event_type)
            cursor.execute(
                """SELECT id FROM events 
                   WHERE timestamp = ? AND worker_id = ? AND event_type = ?""",
                (event['timestamp'], event['worker_id'], event['event_type'])
            )
            
            if cursor.fetchone():
                duplicates += 1
                continue
            
            # Insert event
            cursor.execute(
                """INSERT INTO events (timestamp, worker_id, station_id, event_type, confidence, count)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    event['timestamp'],
                    event['worker_id'],
                    station_id,
                    event['event_type'],
                    event.get('confidence', 0.0),
                    event.get('count')
                )
            )
            inserted += 1
        
        conn.commit()
        
        return jsonify({
            "status": "success",
            "inserted": inserted,
            "duplicates": duplicates,
            "errors": errors if errors else None
        }), 200 if not errors else 207
        
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()


@app.route('/events', methods=['GET'])
def get_events():
    """Get all events (for debugging/inspection)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT 100")
    events = cursor.fetchall()
    conn.close()
    
    return jsonify({
        "events": [dict(e) for e in events],
        "count": len(events)
    })


@app.route('/metrics/workers', methods=['GET'])
def get_worker_metrics():
    """
    Compute and return worker-level productivity metrics.
    
    Metrics computed:
    - Total active time (working)
    - Total idle time
    - Utilization % = active / (active + idle)
    - Total units produced
    - Units per hour
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all workers
    cursor.execute("SELECT worker_id, name FROM workers")
    workers = cursor.fetchall()
    
    # Get evaluation cutoff (latest event timestamp or current time)
    cursor.execute("SELECT MAX(timestamp) FROM events")
    result = cursor.fetchone()
    cutoff_str = result[0] if result[0] else get_current_time().isoformat()
    cutoff = parse_iso_timestamp(cutoff_str)
    
    worker_metrics = []
    
    for worker in workers:
        worker_id = worker['worker_id']
        
        # Get all events for this worker, sorted by timestamp
        cursor.execute(
            """SELECT timestamp, event_type, count 
               FROM events 
               WHERE worker_id = ? 
               ORDER BY timestamp ASC""",
            (worker_id,)
        )
        events = cursor.fetchall()
        
        active_seconds = 0
        idle_seconds = 0
        total_units = 0
        
        for i, event in enumerate(events):
            event_time = parse_iso_timestamp(event['timestamp'])
            event_type = event['event_type']
            
            # Accumulate production counts
            if event_type == 'product_count' and event['count']:
                total_units += event['count']
            
            # Calculate duration to next event or cutoff
            if i < len(events) - 1:
                next_time = parse_iso_timestamp(events[i + 1]['timestamp'])
            else:
                next_time = cutoff
            
            duration = (next_time - event_time).total_seconds()
            
            # Only count working and idle for time metrics
            if event_type == 'working':
                active_seconds += duration
            elif event_type == 'idle':
                idle_seconds += duration
        
        # Calculate derived metrics
        total_tracked_time = active_seconds + idle_seconds
        utilization = (active_seconds / total_tracked_time * 100) if total_tracked_time > 0 else 0
        active_hours = active_seconds / 3600
        units_per_hour = total_units / active_hours if active_hours > 0 else 0
        
        worker_metrics.append({
            "worker_id": worker_id,
            "name": worker['name'],
            "active_time_hours": round(active_hours, 2),
            "idle_time_hours": round(idle_seconds / 3600, 2),
            "utilization_percent": round(utilization, 1),
            "total_units_produced": total_units,
            "units_per_hour": round(units_per_hour, 1)
        })
    
    conn.close()
    
    return jsonify({
        "metrics": worker_metrics,
        "cutoff_time": cutoff_str,
        "computed_at": datetime.now(timezone.utc).isoformat()
    })


@app.route('/metrics/workstations', methods=['GET'])
def get_workstation_metrics():
    """
    Compute and return workstation-level productivity metrics.
    
    Metrics computed:
    - Occupancy time (time when any worker is present)
    - Utilization % (productive time / total occupancy)
    - Total units produced
    - Throughput rate (units per hour)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all workstations
    cursor.execute("SELECT station_id, name FROM workstations")
    workstations = cursor.fetchall()
    
    # Get evaluation cutoff
    cursor.execute("SELECT MAX(timestamp) FROM events")
    result = cursor.fetchone()
    cutoff_str = result[0] if result[0] else get_current_time().isoformat()
    cutoff = parse_iso_timestamp(cutoff_str)
    
    station_metrics = []
    
    for station in workstations:
        station_id = station['station_id']
        
        # Get all events for this workstation, sorted by timestamp
        cursor.execute(
            """SELECT timestamp, worker_id, event_type, count 
               FROM events 
               WHERE station_id = ? 
               ORDER BY timestamp ASC""",
            (station_id,)
        )
        events = cursor.fetchall()
        
        occupancy_seconds = 0
        productive_seconds = 0
        total_units = 0
        
        for i, event in enumerate(events):
            event_time = parse_iso_timestamp(event['timestamp'])
            event_type = event['event_type']
            
            # Accumulate production counts
            if event_type == 'product_count' and event['count']:
                total_units += event['count']
            
            # Calculate duration
            if i < len(events) - 1:
                next_time = parse_iso_timestamp(events[i + 1]['timestamp'])
            else:
                next_time = cutoff
            
            duration = (next_time - event_time).total_seconds()
            
            # Count occupancy (working or idle = someone is there)
            if event_type in ['working', 'idle']:
                occupancy_seconds += duration
                if event_type == 'working':
                    productive_seconds += duration
        
        # Calculate derived metrics
        utilization = (productive_seconds / occupancy_seconds * 100) if occupancy_seconds > 0 else 0
        occupancy_hours = occupancy_seconds / 3600
        throughput_rate = total_units / occupancy_hours if occupancy_hours > 0 else 0
        
        station_metrics.append({
            "station_id": station_id,
            "name": station['name'],
            "occupancy_hours": round(occupancy_hours, 2),
            "utilization_percent": round(utilization, 1),
            "total_units_produced": total_units,
            "throughput_rate": round(throughput_rate, 1)
        })
    
    conn.close()
    
    return jsonify({
        "metrics": station_metrics,
        "cutoff_time": cutoff_str,
        "computed_at": datetime.now(timezone.utc).isoformat()
    })


@app.route('/metrics/factory', methods=['GET'])
def get_factory_metrics():
    """
    Compute and return factory-level aggregate metrics.
    
    Metrics computed:
    - Total productive time across all workers
    - Total production count
    - Average production rate
    - Average worker utilization
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get evaluation cutoff
    cursor.execute("SELECT MAX(timestamp) FROM events")
    result = cursor.fetchone()
    cutoff_str = result[0] if result[0] else get_current_time().isoformat()
    cutoff = parse_iso_timestamp(cutoff_str)
    
    # Get all workers
    cursor.execute("SELECT worker_id FROM workers")
    workers = cursor.fetchall()
    
    total_active_seconds = 0
    total_idle_seconds = 0
    total_units = 0
    worker_utilizations = []
    
    for worker in workers:
        worker_id = worker['worker_id']
        
        cursor.execute(
            """SELECT timestamp, event_type, count 
               FROM events 
               WHERE worker_id = ? 
               ORDER BY timestamp ASC""",
            (worker_id,)
        )
        events = cursor.fetchall()
        
        worker_active = 0
        worker_idle = 0
        
        for i, event in enumerate(events):
            event_time = parse_iso_timestamp(event['timestamp'])
            event_type = event['event_type']
            
            if event_type == 'product_count' and event['count']:
                total_units += event['count']
            
            if i < len(events) - 1:
                next_time = parse_iso_timestamp(events[i + 1]['timestamp'])
            else:
                next_time = cutoff
            
            duration = (next_time - event_time).total_seconds()
            
            if event_type == 'working':
                worker_active += duration
                total_active_seconds += duration
            elif event_type == 'idle':
                worker_idle += duration
                total_idle_seconds += duration
        
        # Calculate worker utilization
        total_tracked = worker_active + worker_idle
        if total_tracked > 0:
            worker_utilizations.append(worker_active / total_tracked * 100)
    
    # Calculate factory-level metrics
    total_productive_hours = total_active_seconds / 3600
    avg_utilization = sum(worker_utilizations) / len(worker_utilizations) if worker_utilizations else 0
    avg_production_rate = total_units / total_productive_hours if total_productive_hours > 0 else 0
    
    conn.close()
    
    return jsonify({
        "metrics": {
            "total_productive_hours": round(total_productive_hours, 2),
            "total_idle_hours": round(total_idle_seconds / 3600, 2),
            "total_production_count": total_units,
            "average_production_rate": round(avg_production_rate, 1),
            "average_worker_utilization": round(avg_utilization, 1),
            "active_workers": len(workers),
            "workers_with_activity": len(worker_utilizations)
        },
        "cutoff_time": cutoff_str,
        "computed_at": datetime.now(timezone.utc).isoformat()
    })


@app.route('/workers', methods=['GET'])
def get_workers():
    """Get list of all workers."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workers")
    workers = cursor.fetchall()
    conn.close()
    return jsonify({"workers": [dict(w) for w in workers]})


@app.route('/workstations', methods=['GET'])
def get_workstations():
    """Get list of all workstations."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workstations")
    stations = cursor.fetchall()
    conn.close()
    return jsonify({"workstations": [dict(s) for s in stations]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
