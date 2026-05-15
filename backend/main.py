import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import fred, sec, treasury
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Macro & Fundamental Financial Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fred.router, prefix="/api/fred", tags=["FRED"])
app.include_router(sec.router, prefix="/api/sec", tags=["SEC"])
app.include_router(treasury.router, prefix="/api/treasury", tags=["Treasury"])


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Macro & Fundamental Financial Dashboard API"}


@app.get("/api/overview")
def get_overview():
    """Returns summary stats for the dashboard home page."""
    return {
        "metrics": [
            {"label": "GDP (Q4 2024)", "value": "$28.27T", "change": "+2.8%", "positive": True},
            {"label": "Unemployment", "value": "3.7%", "change": "-0.1%", "positive": True},
            {"label": "CPI YoY", "value": "3.1%", "change": "-0.2%", "positive": True},
            {"label": "Fed Funds Rate", "value": "5.33%", "change": "0.0%", "positive": None},
            {"label": "10Y Treasury", "value": "4.35%", "change": "+0.05%", "positive": False},
            {"label": "S&P 500", "value": "5,235", "change": "+1.2%", "positive": True},
        ]
    }
