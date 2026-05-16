# FinDash — Macro & Fundamental Financial Dashboard

FinDash is a comprehensive full-stack dashboard designed to pull, analyze, and visualize macroeconomic and fundamental data from the Federal Reserve Economic Data (FRED), SEC EDGAR, and U.S. Treasury Direct platforms.

## Architecture

The application uses a containerized multi-service architecture:
- **Frontend**: Next.js (React) App Router for server-side rendering, using Vanilla CSS for a premium dark-mode, glassmorphic aesthetic.
- **Backend**: FastAPI (Python) for high-performance, asynchronous data aggregation.
- **Caching**: Redis is utilized to prevent rate-limiting when requesting data from external financial APIs.
- **Containerization**: Docker Compose manages the orchestration of the three services.

## Features

- **Macroeconomic Indicators (FRED)**: Search and visualize key macroeconomic series (like GDP, Unemployment, CPI, Fed Funds Rate) using interactive TradingView Lightweight Charts.
- **Fundamental Analysis (SEC)**: View extracted GAAP fundamentals (Revenue, Net Income, EPS, Total Assets) from 10-K filings for major companies, displayed via Recharts.
- **Treasury Direct**: Monitor the latest US Yield Curve, National Debt levels, Treasury Auction Results, and Exchange Rates.

## Getting Started

### Prerequisites
- Docker and Docker Compose
- API Keys for FRED and SEC EDGAR (configured via `.env`)

### Installation

1. Clone the repository.
2. Navigate to the `backend` directory and configure the environment variables:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and insert your FRED_API_KEY and SEC_USER_AGENT
   ```
3. From the root directory, build and run the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```
4. Access the frontend dashboard at `http://localhost:3000` and the API documentation at `http://localhost:8000/docs`.