import os
import json
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


def _generate_yield_curve_data():
    """Generate dummy daily yield curve data."""
    maturities = ["1 Mo", "2 Mo", "3 Mo", "6 Mo", "1 Yr", "2 Yr", "3 Yr", "5 Yr", "7 Yr", "10 Yr", "20 Yr", "30 Yr"]
    fields = ["d1_mo", "d2_mo", "d3_mo", "d6_mo", "d1_yr", "d2_yr", "d3_yr", "d5_yr", "d7_yr", "d10_yr", "d20_yr", "d30_yr"]
    records = []
    d = datetime(2024, 1, 2)
    end = datetime(2024, 12, 31)
    base_curve = [5.53, 5.53, 5.47, 5.37, 5.12, 4.73, 4.44, 4.27, 4.31, 4.35, 4.61, 4.50]

    while d <= end:
        if d.weekday() < 5:
            row = {"record_date": d.strftime("%Y-%m-%d")}
            shift = random.gauss(0, 0.03)
            for i, field in enumerate(fields):
                val = base_curve[i] + shift + random.gauss(0, 0.02)
                # Simulate gradual rate changes
                if d.month >= 9:
                    val -= (d.month - 8) * 0.04
                row[field] = str(round(max(0.01, val), 2))
            records.append(row)
        d += timedelta(days=1)
    return records


def _generate_debt_data():
    """Generate dummy debt-to-penny data."""
    records = []
    d = datetime(2023, 1, 3)
    end = datetime(2024, 12, 31)
    public_debt = 24_200_000_000_000
    intra_debt = 6_800_000_000_000

    while d <= end:
        if d.weekday() < 5:
            public_debt += random.gauss(3e9, 2e9)
            intra_debt += random.gauss(0.5e9, 0.5e9)
            total = public_debt + intra_debt
            records.append({
                "record_date": d.strftime("%Y-%m-%d"),
                "debt_held_public_amt": f"{public_debt:,.2f}",
                "intragov_hold_amt": f"{intra_debt:,.2f}",
                "tot_pub_debt_out_amt": f"{total:,.2f}",
                "src_line_nbr": "1",
            })
        d += timedelta(days=1)

    records.reverse()
    return records[:100]


def _generate_auction_data():
    """Generate dummy Treasury auction data."""
    security_types = ["Bill", "Note", "Bond", "TIPS", "FRN"]
    terms = {"Bill": ["4-Week", "8-Week", "13-Week", "26-Week", "52-Week"],
             "Note": ["2-Year", "3-Year", "5-Year", "7-Year", "10-Year"],
             "Bond": ["20-Year", "30-Year"],
             "TIPS": ["5-Year", "10-Year", "30-Year"],
             "FRN": ["2-Year"]}
    records = []
    d = datetime(2024, 12, 1)

    for i in range(50):
        sec_type = random.choice(security_types)
        term = random.choice(terms[sec_type])
        rate = round(random.uniform(3.5, 5.8), 3)
        amount = round(random.uniform(20, 80), 0)
        records.append({
            "record_date": d.strftime("%Y-%m-%d"),
            "security_type": sec_type,
            "security_term": term,
            "high_yield": f"{rate}%",
            "offering_amt": f"{amount}B",
            "bid_to_cover_ratio": str(round(random.uniform(2.1, 3.5), 2)),
        })
        d -= timedelta(days=random.randint(1, 5))

    return records


def _generate_exchange_rates():
    """Generate dummy exchange rate data."""
    currencies = [
        ("Euro Zone", "EUR", 0.92), ("United Kingdom", "GBP", 0.79),
        ("Japan", "JPY", 149.5), ("Canada", "CAD", 1.36),
        ("Australia", "AUD", 1.53), ("Switzerland", "CHF", 0.88),
        ("China", "CNY", 7.24), ("India", "INR", 83.2),
        ("Brazil", "BRL", 4.97), ("Mexico", "MXN", 17.15),
    ]
    records = []
    d = datetime(2024, 12, 31)
    for i in range(30):
        for country, code, base in currencies:
            records.append({
                "record_date": d.strftime("%Y-%m-%d"),
                "country": country,
                "currency": code,
                "exchange_rate": str(round(base + random.gauss(0, base * 0.005), 4)),
                "effective_date": d.strftime("%Y-%m-%d"),
            })
        d -= timedelta(days=1)
    return records


@router.get("/yield-curve")
def get_yield_curve():
    """Return yield curve data."""
    data = _generate_yield_curve_data()
    return {"data": data, "meta": {"total-count": len(data)}}


@router.get("/yield-curve/latest")
def get_latest_yield_curve():
    """Return the latest yield curve snapshot."""
    random.seed(42)
    maturities = [
        {"label": "1 Mo", "months": 1, "rate": 5.53},
        {"label": "2 Mo", "months": 2, "rate": 5.53},
        {"label": "3 Mo", "months": 3, "rate": 5.47},
        {"label": "6 Mo", "months": 6, "rate": 5.37},
        {"label": "1 Yr", "months": 12, "rate": 5.12},
        {"label": "2 Yr", "months": 24, "rate": 4.73},
        {"label": "3 Yr", "months": 36, "rate": 4.44},
        {"label": "5 Yr", "months": 60, "rate": 4.27},
        {"label": "7 Yr", "months": 84, "rate": 4.31},
        {"label": "10 Yr", "months": 120, "rate": 4.35},
        {"label": "20 Yr", "months": 240, "rate": 4.61},
        {"label": "30 Yr", "months": 360, "rate": 4.50},
    ]
    return {"date": "2024-12-31", "maturities": maturities}


@router.get("/debt")
def get_debt():
    """Return debt-to-penny data."""
    data = _generate_debt_data()
    return {"data": data, "meta": {"total-count": len(data)}}


@router.get("/auctions")
def get_auctions():
    """Return recent Treasury auction results."""
    data = _generate_auction_data()
    return {"data": data, "meta": {"total-count": len(data)}}


@router.get("/exchange-rates")
def get_exchange_rates():
    """Return exchange rate data."""
    data = _generate_exchange_rates()
    return {"data": data, "meta": {"total-count": len(data)}}


@router.get("/data/{endpoint:path}")
def get_treasury_data(
    endpoint: str,
    fields: str = Query(None),
    filter: str = Query(None),
    sort: str = Query(None),
    page_size: int = Query(100),
    page_number: int = Query(1)
):
    """Generic Treasury Fiscal Data API proxy. Returns dummy data."""
    if "yield" in endpoint.lower():
        return get_yield_curve()
    elif "debt" in endpoint.lower():
        return get_debt()
    elif "exchange" in endpoint.lower() or "rates_of_exchange" in endpoint.lower():
        return get_exchange_rates()
    else:
        return get_auctions()
