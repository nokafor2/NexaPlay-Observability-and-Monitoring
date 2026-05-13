# NexaPlay Alert Runbook

This runbook is written for a teammate who needs quick, plain-language guidance during an incident.

## Alert: `ServiceDown`

### What it means

Prometheus cannot scrape the NexaPlay app target anymore for at least 1 minute. In plain language, the app is either down, stuck, or no longer reachable on its metrics endpoint.

### First thing to check

Check whether the app container is running and whether the app responds locally.

```bash
docker compose ps
curl http://localhost:8000/health
```

If the `app` container is missing, restarting, or the health endpoint does not respond, start there.

### Common causes

- The `app` container stopped or failed to start.
- The app is running but not listening on port `8000`.
- The `/metrics` endpoint is broken or blocked.
- A recent code or dependency change stopped the service from booting.
- The container restarted after an error and never became healthy again.

### How to resolve it

1. Read the app logs to see whether it crashed or failed to boot:

```bash
docker compose logs app
```

2. Restart the app:

```bash
docker compose restart app
```

3. If the restart does not help, rebuild and recreate the service:

```bash
docker compose up -d --build app
```

4. Confirm the health endpoint responds again:

```bash
curl http://localhost:8000/health
```

5. Confirm Prometheus shows the `nexaplay-app` target as `UP` again.
6. Confirm the alert clears in Prometheus and Alertmanager.

## Alert: `HighErrorRate`

### What it means

More than 5% of recent app requests are returning `5xx` responses for at least 2 minutes. The app is still reachable, but too many requests are failing.

### First thing to check

Open the `NexaPlay Overview` dashboard and check whether the error rate spike lines up with higher traffic, CPU pressure, or a drop in active players. Also check whether the issue is isolated to one endpoint such as matchmaking.

- `Error Rate`
- `Request Rate`
- `CPU Usage`
- `App Memory Usage`
- `Active Players`

This gives you a quick picture of whether the app is overloaded or whether one feature is failing while the service stays up.

### Common causes

- A broken endpoint, especially `matchmaking`.
- A bad deployment or missing dependency.
- A runaway incident mode or load spike.
- Upstream failures causing the app to return `500` errors.
- The app is alive but too slow, causing requests to fail under load.

### How to resolve it

1. Identify which endpoint is failing by checking Grafana and Prometheus for recent `5xx` responses.
2. If this is the internship drill and incident mode was enabled, reset it:

```bash
curl -X POST http://localhost:8000/admin/incident/reset
```

3. Restart the app if errors continue:

```bash
docker compose restart app
```

4. Generate a small amount of traffic again and verify the error rate falls back below 5%.
5. Confirm the dashboard stabilizes, the alert resolves, and Alertmanager sends a resolved notification.
6. Record the incident and the fix in `JOURNAL.md` while the details are still fresh.
