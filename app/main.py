import random
import time
import threading

from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

# Create the FastAPI application object used by Uvicorn.
app = FastAPI()

# ── Metrics ───────────────────────────────────────────────────────────────────

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    # Label requests by endpoint and response status for later filtering in Prometheus.
    ["endpoint", "status"]
)

ACTIVE_PLAYERS = Gauge(
    "nexaplay_active_players",
    "Number of currently active players"
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "Request duration in seconds",
    # Track latency separately for each endpoint.
    ["endpoint"]
)

MATCHMAKING_QUEUE = Gauge(
    "nexaplay_matchmaking_queue",
    "Number of players currently in matchmaking queue"
)

# ── Incident state ────────────────────────────────────────────────────────────

incident_active = False

# ── Background: simulate active players ──────────────────────────────────────

def simulate_players():
    while True:
        if incident_active:
            # During an incident, active players dip while the queue grows.
            ACTIVE_PLAYERS.set(random.randint(200, 400))
            MATCHMAKING_QUEUE.set(random.randint(80, 150))
        else:
            # In normal operation, player count is higher and queue pressure is lower.
            ACTIVE_PLAYERS.set(random.randint(800, 1200))
            MATCHMAKING_QUEUE.set(random.randint(10, 40))
        # Update the simulation every 5 seconds so dashboards keep moving.
        time.sleep(5)

# Start the background simulator without blocking the main API server.
threading.Thread(target=simulate_players, daemon=True).start()

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    # Count health-check requests as successful 200 responses.
    REQUEST_COUNT.labels(endpoint="/health", status="200").inc()
    return {"status": "ok"}

@app.get("/player/login")
def player_login():
    # Record the start time so the request duration can be measured.
    start = time.time()
    # Simulate a small amount of application processing time.
    time.sleep(random.uniform(0.05, 0.15))
    # Count the request as a successful login endpoint call.
    REQUEST_COUNT.labels(endpoint="/player/login", status="200").inc()
    # Save the observed latency to the histogram metric.
    REQUEST_DURATION.labels(endpoint="/player/login").observe(time.time() - start)
    return {"message": "Player logged in"}

@app.get("/matchmaking/find")
def find_match():
    start = time.time()
    if incident_active:
        # Simulate slow matchmaking responses during the incident drill.
        time.sleep(random.uniform(2.0, 5.0))
        if random.random() < 0.6:
            # Emit a 500 response often enough to trigger the HighErrorRate alert.
            REQUEST_COUNT.labels(endpoint="/matchmaking/find", status="500").inc()
            REQUEST_DURATION.labels(endpoint="/matchmaking/find").observe(time.time() - start)
            return Response(content="Matchmaking error", status_code=500)
    else:
        # Normal matchmaking should be much faster.
        time.sleep(random.uniform(0.1, 0.3))

    # Count successful matchmaking requests.
    REQUEST_COUNT.labels(endpoint="/matchmaking/find", status="200").inc()
    # Record how long the matchmaking request took.
    REQUEST_DURATION.labels(endpoint="/matchmaking/find").observe(time.time() - start)
    return {"match_id": f"match_{random.randint(1000, 9999)}", "players": 2}

@app.get("/game/session")
def game_session():
    start = time.time()
    # Simulate session lookup work.
    time.sleep(random.uniform(0.05, 0.2))
    REQUEST_COUNT.labels(endpoint="/game/session", status="200").inc()
    REQUEST_DURATION.labels(endpoint="/game/session").observe(time.time() - start)
    return {"session_id": f"session_{random.randint(1000, 9999)}", "status": "active"}

# ── Incident controls ─────────────────────────────────────────────────────────

@app.post("/admin/incident/start")
def start_incident():
    global incident_active
    # Turn on degraded-mode behavior for the matchmaking endpoint.
    incident_active = True
    return {"message": "Incident started. Matchmaking is now degraded."}

@app.post("/admin/incident/reset")
def reset_incident():
    global incident_active
    # Return the placeholder app to healthy behavior.
    incident_active = False
    return {"message": "Incident resolved. System back to normal."}

# ── Metrics endpoint ──────────────────────────────────────────────────────────

@app.get("/metrics")
def metrics():
    # Expose all Prometheus metrics in the text format Prometheus expects.
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)