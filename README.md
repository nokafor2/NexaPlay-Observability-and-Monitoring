# NexaPlay Monitoring and Observability

This repository scaffolds the NexaPlay internship monitoring project around Prometheus, Grafana, Alertmanager, Node Exporter, and a temporary FastAPI game-server stub.

The real `app/main.py` and `app/requirements.txt` were not available yet, so this setup includes a clearly marked placeholder service that exposes the same kinds of metrics and incident controls the internship exercises expect. You can swap in the real app later without changing the repository layout.

## Repository Structure

```text
nexaplay-monitoring/
  app/
    main.py
    requirements.txt
    Dockerfile
  prometheus/
    prometheus.yml
    rules/
      alerts.yml
  alertmanager/
    alertmanager.yml
  grafana/
    provisioning/
    dashboards/
  scripts/
    export_to_s3.py
  .github/
    workflows/
      validate.yml
  docker-compose.yml
  .env.example
  runbook.md
  JOURNAL.md
```

## What Is Included

- A Docker Compose stack for all five services.
- A temporary FastAPI app with Prometheus metrics and an incident toggle.
- Prometheus scrape configuration and two starter alert rules.
- Grafana provisioning plus a starter dashboard JSON.
- An S3 export script for dashboard backups.
- A GitHub Actions workflow to validate the main config files.
- A runbook and journal template for the internship deliverables.

## Prerequisites

Install these locally before testing:

- Docker Desktop
- Git
- Python 3.11
- AWS CLI v2

Optional for the S3 export script:

- `boto3`
- `python-dotenv`

Install the optional Python packages with:

```bash
python -m pip install boto3 python-dotenv
```

## Quick Start

1. Copy `.env.example` to `.env`.
2. If you want live alert notifications, replace the placeholder webhook URL inside `alertmanager/alertmanager.yml` with your own [webhook.site](https://webhook.site) URL.
3. Start the monitoring stack:

```bash
docker compose up -d --build
```

4. Open the services:
   - Grafana: [http://localhost:3000](http://localhost:3000)
   - Prometheus: [http://localhost:9090](http://localhost:9090)
   - Alertmanager: [http://localhost:9093](http://localhost:9093)
   - App health check: [http://localhost:8000/healthz](http://localhost:8000/healthz)

5. Sign in to Grafana with the values from `.env` (`admin` / `admin` by default).

## How To Verify The Stack

Run these Prometheus queries after the stack is up:

- `up`
- `nexaplay_active_players`
- `rate(http_requests_total[1m])`
- `process_resident_memory_bytes{job="nexaplay-app"} / 1024 / 1024`

The pre-provisioned Grafana dashboard is named `NexaPlay Overview`.

## Generate Test Traffic

You need some traffic before the request and error-rate graphs become useful.

### PowerShell example

```powershell
1..20 | ForEach-Object {
  Invoke-WebRequest -Method Post http://localhost:8000/login | Out-Null
  Invoke-WebRequest http://localhost:8000/matchmaking | Out-Null
}
```

### Bash example

```bash
for i in {1..20}; do
  curl -s -X POST http://localhost:8000/login > /dev/null
  curl -s http://localhost:8000/matchmaking > /dev/null
done
```

## Test The Alert Rules

### `ServiceDown`

1. Stop the app:

```bash
docker compose stop app
```

2. Wait at least one minute.
3. Confirm the alert is `PENDING` and then `FIRING` in Prometheus.
4. Confirm the notification appears in Alertmanager and your webhook receiver.
5. Restore the app:

```bash
docker compose start app
```

### `HighErrorRate`

1. Start the incident:

```bash
curl -X POST http://localhost:8000/admin/incident/start
```

2. Generate traffic for 2 to 3 minutes using the loop above.
3. Watch the `Error Rate` panel in Grafana and the alert state in Prometheus.
4. Reset the incident when finished:

```bash
curl -X POST http://localhost:8000/admin/incident/reset
```

## Suggested Incident Drill

This mirrors the internship exercise:

1. Capture a healthy baseline screenshot of Grafana.
2. Start test traffic.
3. Trigger the incident.
4. Watch dashboard changes first.
5. Check Prometheus alerts.
6. Check Alertmanager delivery.
7. Describe the failure before restarting anything.
8. Recover the app and confirm the graphs return to normal.
9. Fill in the incident notes in `JOURNAL.md`.

## Export The Dashboard To S3

1. Fill in these values inside `.env`:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_DEFAULT_REGION`
   - `S3_BUCKET_NAME`
2. Confirm the target dashboard file exists at `grafana/dashboards/nexaplay-overview.json`.
3. Run:

```bash
python scripts/export_to_s3.py
```

4. Verify with the AWS CLI:

```bash
aws s3 ls s3://YOUR_BUCKET_NAME/grafana-dashboards/
```

## Validate The Repository

Local validation:

```bash
docker compose config
```

GitHub Actions also validates:

- `docker-compose.yml`
- `prometheus/prometheus.yml`
- `prometheus/rules/alerts.yml`
- `alertmanager/alertmanager.yml`
- Python syntax for the two Python scripts

## Placeholder App Notes

The stub in `app/main.py` is intentionally small and heavily commented so you can understand how the monitoring pieces connect. Once the real NexaPlay app arrives:

1. Replace `app/main.py`.
2. Replace `app/requirements.txt`.
3. Rebuild the stack with `docker compose up -d --build`.
4. Keep the metric names stable where possible so the dashboard and alerts continue to work.
