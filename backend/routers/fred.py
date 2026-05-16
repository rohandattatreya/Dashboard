import os
import json
import math
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

# --- Dummy Data Catalog ---
SERIES_CATALOG = {
    "GDP": {"id": "GDP", "title": "Gross Domestic Product", "frequency": "Quarterly",
            "units": "Billions of Dollars", "seasonal_adjustment": "Seasonally Adjusted Annual Rate",
            "observation_start": "2000-01-01", "observation_end": "2024-10-01", "notes": "Gross domestic product (GDP), the featured measure of U.S. output, is the market value of the goods and services produced by labor and property located in the United States."},
    "UNRATE": {"id": "UNRATE", "title": "Unemployment Rate", "frequency": "Monthly",
               "units": "Percent", "seasonal_adjustment": "Seasonally Adjusted",
               "observation_start": "2000-01-01", "observation_end": "2024-12-01", "notes": "The unemployment rate represents the number of unemployed as a percentage of the labor force."},
    "CPIAUCSL": {"id": "CPIAUCSL", "title": "Consumer Price Index for All Urban Consumers: All Items in U.S. City Average", "frequency": "Monthly",
                 "units": "Index 1982-1984=100", "seasonal_adjustment": "Seasonally Adjusted",
                 "observation_start": "2000-01-01", "observation_end": "2024-12-01", "notes": "The Consumer Price Index (CPI) is a measure of the average change over time in the prices paid by urban consumers for a market basket of consumer goods and services."},
    "DFF": {"id": "DFF", "title": "Federal Funds Effective Rate", "frequency": "Daily",
            "units": "Percent", "seasonal_adjustment": "Not Seasonally Adjusted",
            "observation_start": "2000-01-01", "observation_end": "2024-12-31", "notes": "Rate at which depository institutions trade federal funds."},
    "DGS10": {"id": "DGS10", "title": "Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity", "frequency": "Daily",
              "units": "Percent", "seasonal_adjustment": "Not Seasonally Adjusted",
              "observation_start": "2000-01-01", "observation_end": "2024-12-31", "notes": "10-Year Treasury Constant Maturity Rate."},
    "DGS2": {"id": "DGS2", "title": "Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity", "frequency": "Daily",
             "units": "Percent", "seasonal_adjustment": "Not Seasonally Adjusted",
             "observation_start": "2000-01-01", "observation_end": "2024-12-31", "notes": "2-Year Treasury Constant Maturity Rate."},
    "T10Y2Y": {"id": "T10Y2Y", "title": "10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity", "frequency": "Daily",
               "units": "Percent", "seasonal_adjustment": "Not Seasonally Adjusted",
               "observation_start": "2000-01-01", "observation_end": "2024-12-31", "notes": "The 10-2 spread."},
    "VIXCLS": {"id": "VIXCLS", "title": "CBOE Volatility Index: VIX", "frequency": "Daily",
               "units": "Index", "seasonal_adjustment": "Not Seasonally Adjusted",
               "observation_start": "2000-01-01", "observation_end": "2024-12-31", "notes": "VIX measures market expectation of near-term volatility conveyed by S&P 500 stock index option prices."},
    "M2SL": {"id": "M2SL", "title": "M2 Money Supply", "frequency": "Monthly",
             "units": "Billions of Dollars", "seasonal_adjustment": "Seasonally Adjusted",
             "observation_start": "2000-01-01", "observation_end": "2024-12-01", "notes": "M2 includes a broader set of financial assets held principally by households."},
    "MORTGAGE30US": {"id": "MORTGAGE30US", "title": "30-Year Fixed Rate Mortgage Average in the United States", "frequency": "Weekly",
                     "units": "Percent", "seasonal_adjustment": "Not Seasonally Adjusted",
                     "observation_start": "2000-01-06", "observation_end": "2024-12-26", "notes": "30-Year Fixed Rate Mortgage Average in the United States."},
    "PAYEMS": {"id": "PAYEMS", "title": "All Employees, Total Nonfarm", "frequency": "Monthly",
               "units": "Thousands of Persons", "seasonal_adjustment": "Seasonally Adjusted",
               "observation_start": "2000-01-01", "observation_end": "2024-12-01", "notes": "Total nonfarm payroll employment."},
    "HOUST": {"id": "HOUST", "title": "New Privately-Owned Housing Units Started: Total Units", "frequency": "Monthly",
              "units": "Thousands of Units", "seasonal_adjustment": "Seasonally Adjusted Annual Rate",
              "observation_start": "2000-01-01", "observation_end": "2024-12-01", "notes": "Housing starts."},
    "PCE": {"id": "PCE", "title": "Personal Consumption Expenditures", "frequency": "Monthly",
            "units": "Billions of Dollars", "seasonal_adjustment": "Seasonally Adjusted Annual Rate",
            "observation_start": "2000-01-01", "observation_end": "2024-12-01", "notes": "PCE measures the goods and services purchased by US residents."},
    "INDPRO": {"id": "INDPRO", "title": "Industrial Production: Total Index", "frequency": "Monthly",
               "units": "Index 2017=100", "seasonal_adjustment": "Seasonally Adjusted",
               "observation_start": "2000-01-01", "observation_end": "2024-12-01", "notes": "Industrial production index."},
    "SP500": {"id": "SP500", "title": "S&P 500", "frequency": "Daily",
              "units": "Index", "seasonal_adjustment": "Not Seasonally Adjusted",
              "observation_start": "2000-01-03", "observation_end": "2024-12-31", "notes": "S&P 500 Index."},
    "FEDFUNDS": {"id": "FEDFUNDS", "title": "Federal Funds Effective Rate", "frequency": "Monthly",
                 "units": "Percent", "seasonal_adjustment": "Not Seasonally Adjusted",
                 "observation_start": "2000-01-01", "observation_end": "2024-12-01", "notes": "Effective federal funds rate, monthly average."},
}


def _generate_dummy_series(series_id: str):
    """Generate realistic dummy time series data."""
    random.seed(hash(series_id) % 2**31)
    info = SERIES_CATALOG.get(series_id)
    if not info and series_id != "__GENERIC__":
        return None

    freq = info["frequency"] if info else "Monthly"
    start = datetime(2000, 1, 1)
    end = datetime(2024, 12, 31)
    records = []

    if series_id == "GDP":
        d = datetime(2000, 1, 1)
        val = 10000.0
        while d <= end:
            growth = 1 + random.gauss(0.007, 0.004)
            if d.year == 2008 and d.month >= 7: growth = 1 + random.gauss(-0.01, 0.005)
            if d.year == 2009 and d.month < 7: growth = 1 + random.gauss(-0.008, 0.005)
            if d.year == 2020 and d.month in (4, 7): growth = 1 + random.gauss(-0.08, 0.02)
            if d.year == 2020 and d.month == 10: growth = 1 + random.gauss(0.07, 0.01)
            val *= growth
            records.append({"date": d.strftime("%Y-%m-%d"), "value": round(val, 1)})
            month = d.month + 3
            year = d.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            d = datetime(year, month, 1)
    elif series_id == "UNRATE":
        d, val = datetime(2000, 1, 1), 4.0
        while d <= end:
            target = 4.0
            if 2001 <= d.year <= 2003: target = 5.5 + (d.year - 2001) * 0.3
            elif 2004 <= d.year <= 2007: target = 5.0 - (d.year - 2004) * 0.3
            elif d.year == 2008: target = 6.0 + d.month * 0.15
            elif d.year == 2009: target = 9.0 + d.month * 0.1
            elif d.year == 2010: target = 9.6
            elif 2011 <= d.year <= 2019: target = max(3.5, 9.0 - (d.year - 2010) * 0.7)
            elif d.year == 2020 and d.month <= 4: target = 14.7
            elif d.year == 2020: target = 14.7 - (d.month - 4) * 1.2
            elif d.year == 2021: target = max(3.9, 6.7 - d.month * 0.2)
            elif d.year >= 2022: target = 3.6 + random.gauss(0, 0.1)
            val += (target - val) * 0.3 + random.gauss(0, 0.1)
            val = max(2.5, min(15.0, val))
            records.append({"date": d.strftime("%Y-%m-%d"), "value": round(val, 1)})
            month = d.month + 1
            year = d.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            d = datetime(year, month, 1)
    elif series_id == "CPIAUCSL":
        d, val = datetime(2000, 1, 1), 169.3
        while d <= end:
            rate = 0.002
            if 2021 <= d.year <= 2022: rate = 0.006
            elif d.year == 2023: rate = 0.003
            val *= (1 + rate + random.gauss(0, 0.001))
            records.append({"date": d.strftime("%Y-%m-%d"), "value": round(val, 1)})
            month = d.month + 1
            year = d.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            d = datetime(year, month, 1)
    elif series_id in ("DFF", "FEDFUNDS"):
        d, val = datetime(2000, 1, 1), 5.5
        step = 7 if freq == "Daily" else 30
        while d <= end:
            target = 5.5
            if d.year == 2001: target = max(1.75, 5.5 - d.month * 0.35)
            elif 2002 <= d.year <= 2003: target = 1.25
            elif 2004 <= d.year <= 2006: target = 1.0 + (d.year - 2003) * 1.3
            elif d.year == 2007: target = 5.25 - max(0, d.month - 8) * 0.5
            elif d.year == 2008: target = max(0.25, 4.25 - d.month * 0.35)
            elif 2009 <= d.year <= 2015: target = 0.15
            elif 2016 <= d.year <= 2018: target = 0.25 + (d.year - 2015) * 0.6
            elif d.year == 2019: target = 2.4 - max(0, d.month - 7) * 0.25
            elif 2020 <= d.year <= 2021: target = 0.08
            elif d.year == 2022: target = min(4.33, d.month * 0.35)
            elif d.year >= 2023: target = 5.33
            val += (target - val) * 0.15 + random.gauss(0, 0.02)
            val = max(0.0, val)
            records.append({"date": d.strftime("%Y-%m-%d"), "value": round(val, 2)})
            d += timedelta(days=step)
    elif series_id in ("DGS10", "DGS2"):
        d, val = datetime(2000, 1, 1), 6.5 if series_id == "DGS10" else 6.2
        while d <= end:
            base = 4.5 if series_id == "DGS10" else 4.2
            if d.year <= 2003: base = 5.0 - (d.year - 2000) * 0.5
            elif 2004 <= d.year <= 2007: base = 4.5
            elif 2008 <= d.year <= 2012: base = 2.5
            elif 2013 <= d.year <= 2019: base = 2.3
            elif 2020 <= d.year <= 2021: base = 1.0 if series_id == "DGS10" else 0.2
            elif d.year >= 2022: base = 4.0 if series_id == "DGS10" else 4.5
            val += (base - val) * 0.05 + random.gauss(0, 0.03)
            val = max(0.1, val)
            records.append({"date": d.strftime("%Y-%m-%d"), "value": round(val, 2)})
            d += timedelta(days=1)
            if d.weekday() >= 5: d += timedelta(days=(7 - d.weekday()))
    elif series_id == "SP500":
        d, val = datetime(2000, 1, 3), 1455.0
        while d <= end:
            drift = 0.0003
            if 2001 <= d.year <= 2002: drift = -0.0005
            elif d.year == 2008: drift = -0.002
            elif d.year == 2009 and d.month >= 3: drift = 0.002
            elif d.year == 2020 and d.month in (2, 3): drift = -0.005
            elif d.year == 2020 and d.month >= 4: drift = 0.003
            val *= (1 + drift + random.gauss(0, 0.008))
            records.append({"date": d.strftime("%Y-%m-%d"), "value": round(val, 2)})
            d += timedelta(days=1)
            if d.weekday() >= 5: d += timedelta(days=(7 - d.weekday()))
    elif series_id == "VIXCLS":
        d, val = datetime(2000, 1, 3), 24.0
        while d <= end:
            target = 18.0
            if d.year in (2001, 2002): target = 28.0
            elif d.year == 2008: target = 40.0 + max(0, d.month - 8) * 8
            elif d.year == 2009 and d.month <= 3: target = 50.0
            elif d.year == 2020 and d.month in (3, 4): target = 60.0
            elif d.year >= 2022: target = 22.0
            val += (target - val) * 0.05 + random.gauss(0, 1.5)
            val = max(9.0, val)
            records.append({"date": d.strftime("%Y-%m-%d"), "value": round(val, 2)})
            d += timedelta(days=1)
            if d.weekday() >= 5: d += timedelta(days=(7 - d.weekday()))
    elif series_id == "M2SL":
        d, val = datetime(2000, 1, 1), 4600.0
        while d <= end:
            rate = 0.005
            if d.year == 2020 and d.month >= 3: rate = 0.03
            elif d.year == 2021: rate = 0.01
            elif d.year >= 2022: rate = -0.001
            val *= (1 + rate + random.gauss(0, 0.002))
            records.append({"date": d.strftime("%Y-%m-%d"), "value": round(val, 1)})
            month = d.month + 1
            year = d.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            d = datetime(year, month, 1)
    else:
        # Generic monthly series
        d, val = datetime(2000, 1, 1), 100.0
        while d <= end:
            val *= (1 + random.gauss(0.002, 0.008))
            val = max(10.0, val)
            records.append({"date": d.strftime("%Y-%m-%d"), "value": round(val, 2)})
            month = d.month + 1
            year = d.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            d = datetime(year, month, 1)

    return records


@router.get("/search")
def search_series(q: str = Query("", description="Search query")):
    """Search FRED series catalog."""
    q_lower = q.lower()
    results = []
    for sid, info in SERIES_CATALOG.items():
        if q_lower in sid.lower() or q_lower in info["title"].lower() or q_lower in info.get("notes", "").lower():
            results.append(info)
    if not results and q:
        results = list(SERIES_CATALOG.values())[:5]
    elif not q:
        results = list(SERIES_CATALOG.values())
    return {"results": results}


@router.get("/series/{series_id}")
def get_fred_series(series_id: str):
    """Return time-series data for a FRED series ID."""
    series_id_upper = series_id.upper()
    metadata = SERIES_CATALOG.get(series_id_upper)
    if not metadata:
        metadata = {
            "id": series_id_upper, "title": f"Series {series_id_upper}",
            "frequency": "Monthly", "units": "Units",
            "seasonal_adjustment": "N/A",
            "observation_start": "2000-01-01", "observation_end": "2024-12-01",
            "notes": "Custom series."
        }

    data = _generate_dummy_series(series_id_upper)
    if data is None:
        data = _generate_dummy_series("__GENERIC__")

    return {"metadata": metadata, "data": data}
