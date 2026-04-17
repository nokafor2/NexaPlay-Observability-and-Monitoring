# NexaPlay Alert Runbook

This runbook is written for a teammate who needs quick, plain-language guidance during an incident.

## Alert: `ServiceDown`

### What it means

Prometheus cannot scrape the NexaPlay app target anymore. In practice, that usually means the service stopped, the container crashed, or the metrics endpoint is unreachable.

### First thing to check

Run:

```bash
docker compose ps
```

Confirm whether the `app` container is still running.

### Common causes

- The `app` container stopped or failed to start.
- The app is running but not listening on port `8000`.
- The `/metrics` endpoint is broken.
- A recent code or dependency change stopped the service from booting.

### How to resolve it

1. Restart the app:

```bash
docker compose restart app
```

2. Confirm the health endpoint responds:

```bash
curl http://localhost:8000/healthz
```

3. Confirm Prometheus sees the target as `up` again.
4. Confirm the alert resolves in Prometheus and Alertmanager.

## Alert: `HighErrorRate`

### What it means

More than 5% of recent app requests are returning `5xx` responses for at least 2 minutes. The service is still reachable, but it is failing too many requests.

### First thing to check

Open the `NexaPlay Overview` dashboard and compare:

- `Error Rate`
- `Request Rate`
- `CPU Usage`
- `App Memory Usage`

This helps you tell whether the issue is isolated to request failures or caused by wider resource pressure.

### Common causes

- A broken endpoint, especially `matchmaking`.
- A bad deployment or missing dependency.
- A runaway incident mode or load spike.
- Upstream failures causing the app to return `500` errors.

### How to resolve it

1. Identify which endpoint is misbehaving by checking Prometheus and Grafana.
2. If this is the internship drill, reset or restart the app:

```bash
curl -X POST http://localhost:8000/admin/incident/reset
docker compose restart app
```

3. Generate a small amount of traffic again and verify the error rate drops back below the threshold.
4. Record what happened in `JOURNAL.md` while the details are still fresh.
