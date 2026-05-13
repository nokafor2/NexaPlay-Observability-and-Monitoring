# INCIDENT REPORT — NEXAPLAY TECHNOLOGIES

**Incident Name:** Operation Server Meltdown  
**Date and Time:** Approximately 6:23 AM, when the incident was triggered with `curl -X POST http://localhost:8000/admin/incident/start`  
**Resolved at:** 6:28:09 AM  
**Total Duration:** About 5 minutes  

---

## WHAT HAPPENED

A simulated incident was triggered while the load generator was running with `python scripts/load_generator.py`. This pushed the app into a degraded state where matchmaking started failing more often and system behavior changed noticeably on the dashboard.

Players would likely have experienced failed matchmaking requests, reduced active player numbers, and a less stable service during the incident window.

---

## HOW IT WAS DETECTED

The issue was detected by the **HighErrorRate** alert. Alertmanager sent a **firing** message to `webhook.site` by **6:24:19 AM**, which was within about **1 minute** of triggering the incident.

In Grafana, the clearest signs were the **Error Rate** panel and the **Active Players** panel. The request-rate panel also showed a spike during the incident.

---

## INVESTIGATION

I checked the Grafana dashboard panels for active players, request rate, error rate, and memory usage. The dashboard showed that active players dropped from around **1000** to **242**, while the error rate increased from **0%** to **17.5%**. Request rate jumped during the incident, and memory usage also increased.

These metrics confirmed that the application was still receiving traffic, but it was responding badly under the simulated failure conditions.

---

## HOW IT WAS FIXED

The incident was cleared with:

`curl -X POST http://localhost:8000/admin/incident/reset`

After that, the service was also restarted with:

`docker compose restart app`

Recovery was confirmed when the Grafana panels returned to normal, active players went back to their usual level, request rate settled down, error rate returned to **0%**, and Alertmanager sent a **resolved** message to `webhook.site` at **6:28:09 AM**.

---

## WHAT WOULD PREVENT THIS

One thing that could help prevent this kind of failure in a real production environment is **automatic scaling and stronger protection around the matchmaking service**, so sudden load or degraded behavior does not cause a large spike in failed requests.