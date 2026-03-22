# AdTech KPI Health Monitor
**Power BI · SQL Server**

---

## Overview

An interactive Power BI dashboard monitoring KPI health across 4 global ad markets (NA, EMEA, LATAM, APAC) over 90 days. Tracks CTR, CPC, ROAS, Revenue, and Impressions — with market-level drill-down, date filtering, and an incident alert log that surfaces 5 anomaly events with severity classification.

**Pipeline:** Python generates the dataset → exported as CSV → loaded into SQL Server → Power BI connects to SQL Server for visualisation.

---

## KPIs Tracked

| Metric | Definition |
|--------|-----------|
| CTR % | Click-through rate |
| CPC (USD) | Cost per click |
| ROAS | Return on ad spend |
| Revenue (USD) | Total revenue |
| Ad Spend (USD) | Total advertiser spend |
| Impressions | Total ad impressions |

---

## Anomaly Events

| Date | Market | Type | Severity |
|------|--------|------|----------|
| Jan 19 | NA | CTR Spike +65% | High |
| Feb 15 | EMEA | CPC Drop -62% | Medium |
| Mar 7 | LATAM | Impression Drop -71% | High |
| Mar 12 | NA | CPC Spike +82% | High |
| Mar 24 | APAC | CTR Drop -49% | Medium |

---

## Files

| File | Description |
|------|-------------|
| `adtech_pipeline.py` | Generates the dataset |
| `adtech_dashboard_sql.sql` | SQL Server table and views |
| `dashboard_preview.png` | Dashboard screenshot |
| `Dinesh_AdTech_Dashboard.pdf` | Exported PDF |

---

**Dinesh R** · [LinkedIn](https://linkedin.com/in/dinesh-r-24b606149)
