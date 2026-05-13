# NexaPlay Monitoring Project — Daily Journal

## Day 1 — Monday
**What I did today:**
- The required tools such as Docker Desktop, Git, VS Code, Python, AWS CLI have been installed. The starter repository was cloned into the working folder. A docker compose file was created to dockerize the apps for the Python app, Prometheus image, Grafana image, Node Exporter image, Alertmanager image. The command docker compose up -d was used to start up the containers. The command docker compose ps was used to start check the all the services were running, and it shows Up. Grafana is currently running on localhost:3000, and Prometheus is also running on localhost:9090. My existing AWS CLI credentials is been used.

**What I learned:**
- I learned how to use docker compose to containerize applications and run services simultaneously.

**What confused me:**
- I was able to navigate this task well.

**Pre-Assessment score:** 10/10


## Day 2 — Tuesday
**What I did today:**
- I studies the difference between data model and metric types. I was able to identify the different metrics, it's type and what it measures. In the Prometheus query box, I ran the 'Up' command, I saw that it was scraping data from nexaplay-app on app:8000, and node-exporter on node-exporter:9100. I checked localhost:8000/health to confirm the status of the app and used it to trigger the request rate to work. When I run http_requests_total on the query, it showed the endpoint being reached was "/health", and it was getting data from nexaplay-app with a status 200. Also, on the graph tab, there was a graph of the request. When I run nexaplay_active_players query, I see from the table tab it is scrapping data from nexaplay-app, also I on the graph tab, I see the graph of the data for the active players. When I run process_resident_memory_bytes query, I see it scrapes data from both nexaplay-app and node-exporter in the table tab. In the graph tab, I can see the memory bytes used. I modified the scrape time from 15s to 10s on Prometheus.yml and executed the code curl -X POST localhost:9090/-/reload to effect the changes, and it showed that everything was still working properly.

**What I learned:**
- http_requests_total 
- Type: Counter 
- Measures: the total number of HTTP requests handled by the app, labeled by endpoint and status.

- nexaplay_active_players 
- Type: Gauge 
- Measures: the current number of active players.

- http_request_duration_seconds 
- Type: Histogram 
- Measures: request latency in seconds, labeled by endpoint.

- nexaplay_matchmaking_queue 
- Type: Gauge 
- Measures: the current number of players waiting in the matchmaking queue.

**What confused me:**
- I initially didn't get a result when I ran http_requests_total until I triggered of the endpoint on localhost:8000/health. Then I was able to get a response.

**Pre-Assessment score:** 10/10

## Day 3 — Wednesday
**What I did today:**
- I studied the difference between time series panel, stat panel and gauge panel. A time series is the default and main graph visualization. Alerts are supported in this panel. Stat panel is used for big stats and optional sparkline. A gauge panels is the traditional rounded visual showing how far a single metric is from a threshold. A dashboard was created in Grafana. A stat panel was added to show the current number of players using the nexaplay_active_players query. A time series panel was added showing the total request rate per second using the http_request_total query. A stat panel was added to show the error rate as percentage. A guage panel showing the current CPU usage from node exporter was added. The dashboard was saved as JSON and commited to the repository.

**What I learned:**
- I learnt how to create the panels in Grafana.

**What confused me:**
- Manipulating the queries to get the desired calculation was confusing. 

**Pre-Assessment score:** 7/10

## Day 4 — Thursday
**What I did today:**
- The alerting rules was studies and its implementation was understood. The ServiceDown rule was created when the metric target app was 0. Also 1 minute of down time was set before firing. The HighErrorRate alert was also created. When the error rate exceed 5% for 2 minutes, it fires. A unique URL was optained with webhook.site and was used to configure the alertmanager.yml to send alert to the URL. The service down alert was also tested when the docker compose stop app was executed, and was triggered when the app target metric was 0.  The alert went from PENDING to FIRING. Also there was a message that was sent to the webhook.site when it was firing. Also, when it was restored, a message was also sent to inform the error has been fixed.

**What I learned:**
- I learned how to design a ServiceDown and HighErrorRate alert. I learned how to configure the alert manager using the URL from webhook.site. I learnt how to trigger the ServiceDown alert and what it looks like when it happens.

**What confused me:**
- This task was interesting to observe, and wasn't confusing.

**Pre-Assessment score:** 10/10

## Day 5 — Friday
**What I did today:**
- I reviewed with my team mate, and we explained sections we were conversant with each other.

**What I learned:**
- In this monitoring stack, each tool has a specific responsibility, and together they form a complete observability workflow for the NexaPlay app. The app is the source of the custom metrics. It exposes a /metrics endpoint that Prometheus can scrape. Inside the app, metrics such as http_requests_total, nexaplay_active_players, http_request_duration_seconds, and nexaplay_matchmaking_queue are created and updated while the app is running. This means the app is where the raw monitoring data begins.

Prometheus is the main collector and time-series database in the stack. Its job is to scrape metrics from targets at regular intervals, store them, and make them queryable. In this project, Prometheus scrapes the FastAPI app and also scrapes node-exporter. It uses prometheus.yml to define scrape targets and alerts.yml to define alert rules. Prometheus is important because it does not just store the raw metrics; it also evaluates PromQL expressions and determines when alert conditions are true. For example, it can detect when the app is down or when the error rate is too high.

Grafana is the visualization layer. It does not collect metrics by itself in this project. Instead, it connects to Prometheus as a datasource and sends PromQL queries to it. Grafana then takes the results and displays them as panels, charts, gauges, and stat cards on a dashboard. In this stack, Grafana shows things like active players, request rate, error rate, CPU usage, and memory usage. This makes it easier to understand the health of the system at a glance instead of reading raw Prometheus query results.

Node Exporter is used to expose system-level metrics. While the app provides application metrics, Node Exporter provides host-style metrics such as CPU usage and other machine statistics. Prometheus scrapes Node Exporter the same way it scrapes the app. This means the stack can show both application-level behavior and infrastructure-level behavior in the same dashboard. For example, CPU usage in Grafana comes from Prometheus querying metrics originally exposed by Node Exporter.

Alertmanager handles notifications. Prometheus decides when an alert should fire, but Alertmanager decides what to do with that alert after it is triggered. In this project, Alertmanager receives alerts from Prometheus, groups them, applies routing rules, and sends them to a configured webhook. This means Alertmanager is the part of the stack responsible for turning a detected problem into an actual notification. Prometheus detects the issue, and Alertmanager delivers the message.

Docker Compose is what ties the stack together operationally. It defines all the services, their container images, ports, volumes, and shared network. Because all the services are on the same Docker network, they can refer to each other by service name, such as prometheus, app, alertmanager, and node-exporter. This makes the whole monitoring environment easy to start with one command and keeps the setup reproducible.

The tools connect in a clear flow. First, the app and Node Exporter expose metrics. Next, Prometheus scrapes those metrics and stores them. Grafana then queries Prometheus to display dashboards. At the same time, Prometheus evaluates alert rules, and when a rule is true for long enough, it sends the alert to Alertmanager. Alertmanager then sends the notification to the webhook. So the overall flow is: metric producers -> Prometheus -> Grafana for dashboards, and metric producers -> Prometheus -> Alertmanager for alerts.

**What confused me:**
- The most confusing part for me was understanding the difference between the tools that collect data and the tools that display or route it. At first, it was easy to think Grafana was somehow collecting metrics directly, but I learned that Grafana only visualizes data that Prometheus already scraped and stored. Another confusing part was understanding why some Prometheus queries returned no data. I learned that metrics like http_requests_total only appear after the relevant endpoints are actually called, and that some queries, such as the error-rate query, can return empty results if there are no matching 5xx samples yet. Overall, the biggest lesson was that each tool has a separate role, and the stack works best when I think of it as a pipeline rather than one single system.

**Pre-Assessment score:** 10/10

## Day 6 — Monday
**What I did today:**
### ServiceDown

### What this alert means
This alert means Prometheus cannot reach the NexaPlay app anymore. In simple terms, the monitoring system tried to check the app and got no response for at least 1 minute. This usually means the app container has stopped, crashed, or is not responding on its expected port.

### First thing to check
First, check whether the app container is still running:

`docker compose ps`

Then check whether the app responds locally:

`http://localhost:8000/health`

If the app is not running or the health endpoint does not respond, the service is down.

### How to restore the service
Try restarting the app container:

`docker compose restart app`

If that does not fix it, check the app logs:

`docker compose logs app`

If needed, recreate the app container:

`docker compose up -d --build app`

After the app comes back, wait a short time and confirm that:
- `http://localhost:8000/health` works
- Prometheus shows the target as `UP`
- the `ServiceDown` alert clears

**What I learned:**
- I learned how to fix or restart the app again if it went down.

**What confused me:**
- It was one thing to see how the ServiceDown event could look like. It was another thing to understand how to recover from such situation.

**Pre-Assessment score:** 10/10

## Day 7 — Tuesday
**What I did today:**

**What I learned:**

**What confused me:**

**Pre-Assessment score:** ___/10

## Day 8 — Wednesday
**What I did today:**

**What I learned:**

**What confused me:**

**Pre-Assessment score:** ___/10

## Day 9 — Thursday
**What I did today:**

**What I learned:**

**What confused me:**

**Pre-Assessment score:** ___/10

## Day 10 — Friday
**What I did today:**

**What I learned:**

**What confused me:**

**Pre-Assessment score:** ___/10

---

<!-- Add one entry every day through to Day 10 -->