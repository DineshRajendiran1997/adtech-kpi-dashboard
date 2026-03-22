import pandas as pd
import numpy as np
from datetime import date, timedelta
import random

# seed for reproducibility
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

START_DATE = date(2024, 1, 1)
DAYS = 90
OUTPUT = "adtech_raw_data.csv"

# base metrics per market - NA leads, LATAM lowest
MARKETS = {
    "NA": {
        "impressions": 950000,
        "ctr": 0.048,
        "cpc": 1.85,
        "conv_rate": 0.032
    },
    "EMEA": {
        "impressions": 720000,
        "ctr": 0.041,
        "cpc": 1.42,
        "conv_rate": 0.027
    },
    "LATAM": {
        "impressions": 380000,
        "ctr": 0.037,
        "cpc": 0.98,
        "conv_rate": 0.021
    },
    "APAC": {
        "impressions": 540000,
        "ctr": 0.040,
        "cpc": 1.15,
        "conv_rate": 0.026
    }
}

DEVICES = {
    "Desktop": 0.52,
    "Mobile": 0.38,
    "Tablet": 0.10
}

# injected anomalies - offset is days from start date
ANOMALIES = [
    {"offset": 18, "market": "NA",    "type": "CTR Spike",       "kpi": "ctr",         "factor": 1.65},
    {"offset": 45, "market": "EMEA",  "type": "CPC Anomaly",     "kpi": "cpc",         "factor": 0.38},
    {"offset": 66, "market": "LATAM", "type": "Impression Drop", "kpi": "impressions", "factor": 0.29},
    {"offset": 71, "market": "NA",    "type": "CPC Spike",       "kpi": "cpc",         "factor": 1.82},
    {"offset": 83, "market": "APAC",  "type": "CTR Drop",        "kpi": "ctr",         "factor": 0.51},
]

def weekend_factor(weekday):
    # weekends see ~22% lower traffic in B2B search
    return 0.78 if weekday >= 5 else 1.0

def apply_noise(value, pct=0.08):
    return value * random.uniform(1 - pct, 1 + pct)

def get_anomaly(day_offset, market):
    for a in ANOMALIES:
        if a["offset"] == day_offset and a["market"] == market:
            return a
    return None

rows = []

for day in range(DAYS):
    current_date = START_DATE + timedelta(days=day)
    wf = weekend_factor(current_date.weekday())

    for market, base in MARKETS.items():
        for device, split in DEVICES.items():

            anomaly = get_anomaly(day, market)

            impressions = int(base["impressions"] * split * wf * apply_noise(1.0))
            if anomaly and anomaly["kpi"] == "impressions":
                impressions = int(impressions * anomaly["factor"])

            ctr = base["ctr"] * wf * apply_noise(1.0, pct=0.06)
            if anomaly and anomaly["kpi"] == "ctr":
                ctr *= anomaly["factor"]

            cpc = base["cpc"] * apply_noise(1.0, pct=0.05)
            if anomaly and anomaly["kpi"] == "cpc":
                cpc *= anomaly["factor"]

            clicks = int(impressions * ctr)
            spend = round(clicks * cpc, 2)
            conversions = int(clicks * base["conv_rate"] * apply_noise(1.0))
            revenue = round(conversions * random.uniform(18, 42), 2)
            roas = round(revenue / spend, 2) if spend > 0 else 0

            rows.append({
                "Date": current_date,
                "Market": market,
                "Device": device,
                "Impressions": impressions,
                "CTR_Pct": round(ctr * 100, 3),
                "CPC_USD": round(cpc, 2),
                "Clicks": clicks,
                "Ad_Spend_USD": spend,
                "Conversions": conversions,
                "Revenue_USD": revenue,
                "ROAS": roas,
                "Alert_Fired": 1 if anomaly else 0,
                "Alert_Type": anomaly["type"] if anomaly else "None"
            })

df = pd.DataFrame(rows)
df = df.sort_values(["Date", "Market", "Device"]).reset_index(drop=True)
df.to_csv(OUTPUT, index=False)

print(f"done - {len(df)} rows written to {OUTPUT}")
print(f"alert days: {df[df['Alert_Fired']==1]['Date'].nunique()}")
