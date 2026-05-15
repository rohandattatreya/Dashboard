import os
import json
import random
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

COMPANY_DB = {
    "320193": {
        "cik": "320193", "entityName": "Apple Inc.", "ticker": "AAPL",
        "revenue": [170910, 182795, 215639, 229234, 265595, 274515, 260174, 365817, 394328, 383285, 391035],
        "net_income": [37037, 39510, 45687, 48351, 55256, 57411, 55930, 94680, 99803, 96995, 100913],
        "eps": [2.31, 2.32, 2.98, 3.00, 3.28, 3.31, 3.28, 5.67, 6.15, 6.13, 6.42],
        "total_assets": [290479, 321686, 375319, 365725, 338516, 323888, 351002, 338516, 352583, 352755, 364980],
        "years": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    },
    "789019": {
        "cik": "789019", "entityName": "Microsoft Corporation", "ticker": "MSFT",
        "revenue": [86833, 93580, 91154, 96571, 110360, 125843, 143015, 168088, 198270, 211915, 245122],
        "net_income": [22074, 12193, 16798, 25489, 16571, 39240, 44281, 61271, 72738, 72361, 88136],
        "eps": [2.63, 1.48, 2.10, 3.25, 2.13, 5.06, 5.76, 8.05, 9.65, 9.68, 11.80],
        "total_assets": [172384, 193468, 193694, 250312, 258848, 286556, 301311, 333779, 364840, 411976, 512163],
        "years": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    },
    "1652044": {
        "cik": "1652044", "entityName": "Alphabet Inc.", "ticker": "GOOGL",
        "revenue": [66001, 74989, 90272, 110855, 136819, 161857, 182527, 257637, 282836, 307394, 350018],
        "net_income": [14136, 16348, 19478, 12662, 34343, 40269, 40269, 76033, 59972, 73795, 100530],
        "eps": [2.02, 2.32, 2.75, 1.77, 4.86, 5.61, 5.51, 5.61, 4.56, 5.80, 8.04],
        "total_assets": [147461, 167497, 197295, 232792, 275909, 319616, 359268, 365264, 359268, 402392, 430230],
        "years": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    },
    "1018724": {
        "cik": "1018724", "entityName": "Amazon.com, Inc.", "ticker": "AMZN",
        "revenue": [88988, 107006, 135987, 177866, 232887, 280522, 386064, 469822, 513983, 574785, 637997],
        "net_income": [-241, 2371, 2371, 3033, 10073, 11588, 21331, 33364, -2722, 30425, 59248],
        "eps": [-0.52, 4.90, 4.90, 6.15, 20.14, 23.01, 41.83, 64.81, -5.12, 2.90, 5.66],
        "total_assets": [54505, 65444, 83402, 131310, 162648, 225248, 321195, 420549, 462675, 527854, 624894],
        "years": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    },
    "1318605": {
        "cik": "1318605", "entityName": "Tesla, Inc.", "ticker": "TSLA",
        "revenue": [3198, 4046, 7000, 11759, 21461, 24578, 31536, 53823, 81462, 96773, 97690],
        "net_income": [-294, -889, -675, -1962, -976, -862, 721, 5519, 12556, 14997, 7091],
        "eps": [-2.36, -6.93, -4.68, -11.83, -4.92, -2.76, 0.64, 4.90, 12.18, 4.73, 2.22],
        "total_assets": [5831, 8068, 22664, 28655, 34309, 34309, 52148, 62131, 82338, 106618, 122070],
        "years": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    },
}

COMPANY_SEARCH = [
    {"cik": "320193", "name": "Apple Inc.", "ticker": "AAPL"},
    {"cik": "789019", "name": "Microsoft Corporation", "ticker": "MSFT"},
    {"cik": "1652044", "name": "Alphabet Inc.", "ticker": "GOOGL"},
    {"cik": "1018724", "name": "Amazon.com, Inc.", "ticker": "AMZN"},
    {"cik": "1318605", "name": "Tesla, Inc.", "ticker": "TSLA"},
]


def _build_xbrl_facts(company):
    """Build an XBRL-like facts structure from our dummy data."""
    def _make_entries(values, years, form="10-K"):
        return [
            {"val": v, "fy": y, "fp": "FY", "form": form,
             "filed": f"{y + 1}-01-28", "start": f"{y}-01-01", "end": f"{y}-12-31"}
            for v, y in zip(values, years)
        ]

    facts = {
        "us-gaap": {
            "Revenues": {
                "label": "Revenues",
                "units": {"USD": _make_entries([v * 1_000_000 for v in company["revenue"]], company["years"])}
            },
            "NetIncomeLoss": {
                "label": "Net Income (Loss)",
                "units": {"USD": _make_entries([v * 1_000_000 for v in company["net_income"]], company["years"])}
            },
            "EarningsPerShareBasic": {
                "label": "Earnings Per Share, Basic",
                "units": {"USD/shares": _make_entries(company["eps"], company["years"])}
            },
            "Assets": {
                "label": "Total Assets",
                "units": {"USD": _make_entries([v * 1_000_000 for v in company["total_assets"]], company["years"])}
            },
        }
    }
    return facts


@router.get("/search")
def search_companies(q: str = Query("", description="Company name or ticker")):
    q_lower = q.lower()
    if not q:
        return {"results": COMPANY_SEARCH}
    results = [c for c in COMPANY_SEARCH
               if q_lower in c["name"].lower() or q_lower in c["ticker"].lower() or q_lower in c["cik"]]
    return {"results": results if results else COMPANY_SEARCH}


@router.get("/companyfacts/{cik}")
def get_company_facts(cik: str):
    cik_clean = cik.lstrip("0") or "0"
    company = COMPANY_DB.get(cik_clean)
    if not company:
        for key, val in COMPANY_DB.items():
            if key == cik or key == cik.zfill(10) or cik_clean == key:
                company = val
                break
    if not company:
        raise HTTPException(status_code=404, detail=f"Company CIK {cik} not found. Try: 320193 (Apple), 789019 (Microsoft)")

    return {
        "cik": company["cik"],
        "entityName": company["entityName"],
        "facts": _build_xbrl_facts(company),
    }
