import asyncio
import random
import time
from threading import Lock

from fastapi import FastAPI, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

# Design step 1:
# Keep this service intentionally small and well-commented so the monitoring
# stack can be exercised before the real NexaPlay application is available.
app = FastAPI(title="NexaPlay Placeholder Game Server", version="0.1.0")

# Design step 2:
# Reuse metric names that match the internship brief so Prometheus, Grafana,
# and alert rules can be tested now and reused later with minimal changes.
HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests handled by the NexaPlay placeholder app.",
    ["method", "endpoint", "status"],
)
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "Observed request duration for placeholder endpoints.",
    ["endpoint"],
)
ACTIVE_PLAYERS = Gauge(
    "nexaplay_active_players",
    "Current number of active players connected to the placeholder app.",
)

state_lock = Lock()
incident_active = False
active_players = 125
ACTIVE_PLAYERS.set(active_players)


def get_state():
    with state_lock:
        return {"incident_active": incident_active, "active_players": active_players}


def set_incident(value: bool) -> None:
    global incident_active
    with state_lock:
        incident_active = value


def change_active_players(delta: int) -> int:
    global active_players
    with state_lock:
        active_players = max(0, active_players + delta)
        ACTIVE_PLAYERS.set(active_players)
        return active_players


@app.middleware("http")
async def instrument_requests(request, call_next):
    # Design step 3:
    # Use middleware instead of per-endpoint counters so every route is covered
    # consistently, including future routes added during the project.
    start_time = time.perf_counter()
    endpoint = request.url.path
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except HTTPException as exc:
        status_code = exc.status_code
        raise
    except Exception:
        status_code = 500
        raise
    finally:
        duration = time.perf_counter() - start_time
        HTTP_REQUESTS.labels(
            method=request.method,
            endpoint=endpoint,
            status=str(status_code),
        ).inc()
        HTTP_REQUEST_DURATION.labels(endpoint=endpoint).observe(duration)


@app.get("/")
async def root():
    return {
        "service": "nexaplay-placeholder",
        "message": "Temporary app scaffold for the monitoring internship project.",
        "state": get_state(),
    }


@app.get("/healthz")
async def healthz():
    return {"status": "ok", **get_state()}


@app.post("/login")
async def login():
    # A small random increment keeps the active-player metric moving for demos.
    updated_total = change_active_players(random.randint(1, 5))
    return {"message": "Player logged in", "active_players": updated_total}


@app.post("/logout")
async def logout():
    updated_total = change_active_players(-random.randint(1, 3))
    return {"message": "Player logged out", "active_players": updated_total}


@app.get("/matchmaking")
async def matchmaking():
    snapshot = get_state()
    if snapshot["incident_active"]:
        # Design step 4:
        # The placeholder incident simulates a degraded but not fully-dead
        # service, which makes the HighErrorRate alert meaningful to test.
        await asyncio.sleep(2.5)
        if random.random() < 0.35:
            raise HTTPException(status_code=500, detail="Matchmaking is degraded")
        return {
            "message": "Matchmaking is slow",
            "queue_time_seconds": round(random.uniform(8.0, 14.0), 2),
        }

    await asyncio.sleep(0.2)
    return {
        "message": "Match found",
        "queue_time_seconds": round(random.uniform(1.0, 2.5), 2),
    }


@app.get("/session/start")
async def session_start():
    await asyncio.sleep(0.1)
    return {"message": "Game session started"}


@app.post("/admin/incident/start")
async def start_incident():
    set_incident(True)
    return {"message": "Incident mode enabled", **get_state()}


@app.post("/admin/incident/reset")
async def reset_incident():
    set_incident(False)
    return {"message": "Incident mode cleared", **get_state()}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
