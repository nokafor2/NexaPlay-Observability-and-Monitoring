# NexaPlay Monitoring Project - Daily Journal

## Day 1 - Monday
### What I did today
- Installed the required tools: Docker Desktop, Git, VS Code, Python, and AWS CLI.
- Cloned the starter repository into the working folder.
- Created a Docker Compose file to run the Python app, Prometheus, Grafana, Node Exporter, and Alertmanager.
- Started the containers with `docker compose up -d`.
- Verified that the services were running with `docker compose ps`.
- Confirmed that Grafana was available on `localhost:3000` and Prometheus on `localhost:9090`.
- Used my existing AWS CLI credentials.

### What I learned
- I learned how to use Docker Compose to containerize applications and run services at the same time.

### What confused me
- I was able to navigate this task well.

**Pre-Assessment score:** `7/10`

## Day 2 - Tuesday
### What I did today
- Studied the difference between the Prometheus data model and metric types.
- Identified the different metrics, their types, and what they measure.
- Ran the `up` query in Prometheus and confirmed it was scraping data from `nexaplay-app` on `app:8000` and `node-exporter` on `node-exporter:9100`.
- Checked `localhost:8000/health` to confirm the app status and to trigger request traffic.
- Ran `http_requests_total` and saw that the endpoint reached was `/health`, with data coming from `nexaplay-app` and a `200` status.
- Ran `nexaplay_active_players` and saw the metric in both the table and graph views.
- Ran `process_resident_memory_bytes` and saw it scraping data from both `nexaplay-app` and `node-exporter`.
- Modified the scrape interval from `15s` to `10s` in `prometheus.yml`.
- Reloaded Prometheus with `curl -X POST localhost:9090/-/reload` and confirmed the stack was still working.

### What I learned
- `http_requests_total`
  - Type: `Counter`
  - Measures: the total number of HTTP requests handled by the app, labeled by endpoint and status.
- `nexaplay_active_players`
  - Type: `Gauge`
  - Measures: the current number of active players.
- `http_request_duration_seconds`
  - Type: `Histogram`
  - Measures: request latency in seconds, labeled by endpoint.
- `nexaplay_matchmaking_queue`
  - Type: `Gauge`
  - Measures: the current number of players waiting in the matchmaking queue.

### What confused me
- I initially did not get a result when I ran `http_requests_total` until I triggered the endpoint on `localhost:8000/health`. After that, I was able to get a response.

**Pre-Assessment score:** `7/10`

## Day 3 - Wednesday
### What I did today
- Studied the difference between the time series, stat, and gauge panels in Grafana.
- Learned that a time series panel is the default graph visualization and supports alerts.
- Learned that a stat panel is used for large single values and optional sparklines.
- Learned that a gauge panel shows how far a single metric is from a threshold.
- Created a Grafana dashboard.
- Added a stat panel to show the current number of players using the `nexaplay_active_players` query.
- Added a time series panel showing the total request rate per second.
- Added a stat panel to show the error rate as a percentage.
- Added a gauge panel showing the current CPU usage from Node Exporter.
- Saved the dashboard as JSON and committed it to the repository.

### What I learned
- I learned how to create panels in Grafana.

### What confused me
- Manipulating the queries to get the desired calculations was confusing.

**Pre-Assessment score:** `7/10`

## Day 4 - Thursday
### What I did today
- Studied alerting rules and understood how they are implemented.
- Created the `ServiceDown` rule to fire when the app target metric becomes `0`.
- Configured the alert to wait for `1 minute` before firing.
- Created the `HighErrorRate` alert to fire when the error rate exceeds `5%` for `2 minutes`.
- Obtained a unique URL from `webhook.site` and used it in `alertmanager.yml`.
- Tested the `ServiceDown` alert by running `docker compose stop app`.
- Observed the alert move from `PENDING` to `FIRING`.
- Confirmed that a message was sent to `webhook.site` when the alert fired.
- Confirmed that another message was sent when the service was restored.

### What I learned
- I learned how to design `ServiceDown` and `HighErrorRate` alerts.
- I learned how to configure Alertmanager using a `webhook.site` URL.
- I learned how to trigger the `ServiceDown` alert and what it looks like when it happens.

### What confused me
- This task was interesting to observe and was not confusing.

**Pre-Assessment score:** `5/10`

## Day 5 - Friday
### What I did today
- Reviewed the project with my teammate and explained the sections each of us understood best.

### What I learned
- The app is the source of the custom metrics. It exposes a `/metrics` endpoint that Prometheus can scrape. Metrics such as `http_requests_total`, `nexaplay_active_players`, `http_request_duration_seconds`, and `nexaplay_matchmaking_queue` are created and updated while the app is running.
- Prometheus is the main collector and time-series database in the stack. It scrapes metrics from targets, stores them, and makes them queryable. It also evaluates alert rules.
- Grafana is the visualization layer. It connects to Prometheus as a datasource, runs PromQL queries, and displays the results as panels, charts, gauges, and stat cards.
- Node Exporter exposes system-level metrics such as CPU usage and other machine statistics. Prometheus scrapes it just like it scrapes the app.
- Alertmanager handles notifications. Prometheus decides when an alert should fire, and Alertmanager decides how to route and send that alert.
- Docker Compose ties the stack together by defining all services, ports, volumes, and the shared network.
- The tools connect in a clear flow: metric producers -> Prometheus -> Grafana for dashboards, and metric producers -> Prometheus -> Alertmanager for alerts.

### What confused me
- The most confusing part for me was understanding the difference between the tools that collect data and the tools that display or route it. At first, it was easy to think Grafana was collecting metrics directly, but I learned that Grafana only visualizes data that Prometheus has already scraped and stored. Another confusing part was understanding why some Prometheus queries returned no data. I learned that metrics like `http_requests_total` only appear after the relevant endpoints are called, and that some queries, such as the error-rate query, can return empty results if there are no matching `5xx` samples yet.

**Pre-Assessment score:** `5/10`

## Day 6 - Monday
### What I did today
- Wrote the runbook entry for the `ServiceDown` alert.

#### ServiceDown
##### What this alert means
- This alert means Prometheus cannot reach the NexaPlay app anymore. In simple terms, the monitoring system tried to check the app and got no response for at least `1 minute`. This usually means the app container has stopped, crashed, or is not responding on its expected port.

##### First thing to check
- First, check whether the app container is still running:
  - `docker compose ps`
- Then check whether the app responds locally:
  - `http://localhost:8000/health`
- If the app is not running or the health endpoint does not respond, the service is down.

##### How to restore the service
- Try restarting the app container:
  - `docker compose restart app`
- If that does not fix it, check the app logs:
  - `docker compose logs app`
- If needed, recreate the app container:
  - `docker compose up -d --build app`
- After the app comes back, wait a short time and confirm that:
  - `http://localhost:8000/health` works
  - Prometheus shows the target as `UP`
  - The `ServiceDown` alert clears

### What I learned
- I learned how to fix or restart the app again if it goes down.

### What confused me
- It was one thing to see what the `ServiceDown` event could look like. It was another thing to understand how to recover from such a situation.

**Pre-Assessment score:** `5/10`

## Day 7 - Tuesday
### What I did today
- Executed the load generator to simulate active players with `python scripts/load_generator.py`.
- Triggered the incident with `curl -X POST http://localhost:8000/admin/incident/start`.
- Observed in Grafana that active players dropped from around `1000` to `242`.
- Observed that the request rate jumped.
- Observed that the error rate increased from `0%` to `17.5%`.
- Observed that memory usage also increased.
- By `6:24:19 AM`, Alertmanager had triggered an alert and a message with status `firing` was received in `webhook.site` within a minute.
- After the incident and the 5-minute load-generator window elapsed, the request rate dropped back, the error rate returned to `0%`, and a `resolved` message was sent to `webhook.site` by `6:28:09 AM`.
- Reset the incident with `curl -X POST http://localhost:8000/admin/incident/reset`.
- Restarted the service with `docker compose restart app` and confirmed that the Grafana panels were displaying again.

### What I learned
- I learned how to use the panels to detect problems when they occur.
- I learned how to identify the messages sent by Alertmanager.
- I learned how to resolve issues such as restarting the app and ensuring that all panels are running.

### What confused me
- It was useful practice to see how such an incident could occur.

**Pre-Assessment score:** `5/10`

## Day 8 - Wednesday
### What I did today
- Created the S3 bucket using the AWS CLI.
- Created the IAM user.
- Attached a policy for `s3:PutObject`.
- Generated the access keys for the IAM user, saved them in `.env`, and added `.env` to `.gitignore`.
- Created `scripts/export_to_s3.py` to read the Grafana dashboard JSON file and upload it to the S3 bucket using `boto3`.
- Installed `boto3` in the working directory environment.
- Verified that the JSON file was safely uploaded to the S3 bucket.
- Created the `validate.yml` workflow to run on every push and validate that `docker-compose.yml` and `prometheus.yml` were error free.
- Pushed the commit to GitHub and confirmed there was no error.

### What I learned
- I learned how to use the AWS CLI to create an S3 bucket, IAM user, access key, and attach a policy.
- I learned how to upload the Grafana JSON to the S3 bucket.
- I learned how to push the work to GitHub successfully.

### What confused me
- I got confused when I was trying to commit to AWS with the newly created IAM user. I already had an IAM user configured for my AWS CLI, so when I created and attached the policy, I ran into permission issues during deployment. I got an error saying that the IAM user I was using did not have the privilege to perform the task, so I had to switch IAM users and ensure the correct policy was attached before I could upload successfully to the S3 bucket.

**Pre-Assessment score:** `5/10`

## Day 9 - Thursday
### What I did today
- Updated `runbook.md` to include entries for the `ServiceDown` and `HighErrorRate` alerts.
- Completed a security check with `git log --all -S 'AKIA'` and confirmed that no AWS access key had been committed.
- Ensured that `.env` was listed in `.gitignore`.
- Cleaned up the AWS resources created with the AWS CLI.
- Deleted the contents of the S3 bucket before deleting the bucket itself.
- Listed all access keys, then deleted them.
- Detached the policies from the IAM user and deleted them before deleting the IAM user.
- Brought the stack down with `docker compose down -v` and started it again with `docker compose up -d`.
- Confirmed that everything was working again.

### What I learned
- I learned how to delete access keys and the IAM user.
- I learned that I first had to list the available access keys, delete each key, then detach the policies attached to the user before deleting the user itself.
- I learned how to confirm that the user had been deleted.

#### Cleanup commands used
- List the access keys for the user:
  - `aws iam list-access-keys --user-name nexaplay-dashboard-exporter`
- Delete each key:
  - `aws iam delete-access-key --user-name nexaplay-dashboard-exporter --access-key-id YOUR_ACCESS_KEY_ID`
- Confirm the keys are gone:
  - `aws iam list-access-keys --user-name nexaplay-dashboard-exporter`
- List the attached policies:
  - `aws iam list-attached-user-policies --user-name nexaplay-dashboard-exporter`
- Detach the policy from the user:
  - `aws iam detach-user-policy --user-name nexaplay-dashboard-exporter --policy-arn arn:aws:iam::policy-number:policy/NexaPlayDashboardPutObjectPolicy`
- Confirm it is no longer attached:
  - `aws iam list-attached-user-policies --user-name nexaplay-dashboard-exporter`
- Delete the policy from AWS:
  - `aws iam delete-policy --policy-arn arn:aws:iam::policy-number:policy/NexaPlayDashboardPutObjectPolicy`
- Delete the user:
  - `aws iam delete-user --user-name nexaplay-dashboard-exporter`
- Confirm the user is gone:
  - `aws iam get-user --user-name nexaplay-dashboard-exporter`

### What confused me
- It was confusing at first that I could not delete the user until I had detached the policies attached to it.

**Pre-Assessment score:** `5/10`

## Day 10 - Friday
### What I did today
- Made a presentation to my instructor and fellow colleagues to show how the Grafana panels work and how all the services interact together.
- In the pre-assessment test, I scored `87%`.
- In the final assessment, I scored `100%`, which showed improvement after the project.
- Confirmed that all code had been pushed to GitHub and that the repository link had been submitted.

### What I learned
- I made a very good presentation after the project.

### What confused me
- None.

**Pre-Assessment score:** `10/10`

---

<!-- Add one entry every day through to Day 10 -->