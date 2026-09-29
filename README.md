# WYVERN // FINTECH OPERATING SYSTEM

> **Wyvern** is an intelligent, agentic fintech operating system featuring a stark **Nothing OS-inspired aesthetic** (monochrome, dot-matrix typography, glyph lighting, and signature red accents). It pairs production-ready machine learning intelligence with real-time financial APIs to categorize transaction narratives, forecast monthly savings with confidence bands, detect spending anomalies, manage Plaid banking connections, stream live stock markets, and recommend top-performing SIPs and equity assets for both India and Global markets.

---

## ⚡ Core Capabilities

### 1. Machine Learning Intelligence Engine
* **Spending Categorization (`TF-IDF + Calibrated Logistic Regression`)**:
  * Real-time semantic categorization trained across hundreds of US & Indian fintech transaction narratives (Swiggy, Blinkit, Zomato, Starbucks, Vanguard, Netflix, ConEdison, Nike, etc.).
  * Interactive categorization sandbox with confidence scoring and probability distributions.
* **Monthly Savings Forecaster (`Polynomial Ridge Time-Series Regression`)**:
  * Predicts monthly savings and cumulative wealth accumulation for 1 to 12 months.
  * Calculates 80% confidence intervals (p10 and p90 bounds) and savings rates.
  * Generates 3 multi-variable scenarios: **Conservative** (-18%), **Baseline**, and **Wyvern AI-Optimized** (+24%).
* **Spending Anomaly Radar (`Isolation Forest + Category Median Absolute Deviation`)**:
  * Flags spending spikes, outlier amounts, rapid duplicate charges within 10 minutes, and subscription tier creep.
  * Classifies severity as `CRITICAL`, `WARNING`, or `INFO` with explanations and dispute recommendations.

### 2. Nothing OS Inspired Interface
* **Monochrome & Dot Matrix Typography**: Custom NDOT styling, glyph status beacons, flip-clock headers, and bento-box grid layouts.
* **Tactile Haptic Audio Engine**: Synthesizes authentic mechanical click acoustics via native browser Web Audio API (with instant mute toggle).
* **Glyph Interface**: Pulsing status diodes and LED strips reflecting Plaid connection health and security radar status.
* **Dual Currency Engine**: Instant 1-click toggle between **USD ($)** and **INR (₹)**.

### 3. Plaid API Integration
* Built for Plaid Sandbox & Production.
* Full Link workflow: Link token creation (`/api/plaid/create-link-token`), OAuth institution selection simulator (Chase, Bank of America, HDFC Bank, ICICI Bank, Wells Fargo, SVB), public token exchange (`/api/plaid/exchange-token`), and transaction synchronization (`/api/plaid/sync`).

### 4. Stock Market Live Feed
* **Live World & Domestic Indices**: Real-time quotes for NIFTY 50 (`^NSEI`), SENSEX (`^BSESN`), NIFTY BANK (`^NSEBANK`), S&P 500 (`^GSPC`), NASDAQ (`^IXIC`), and DOW JONES (`^DJI`).
* Low-latency caching engine with resilient fallbacks and automatic 30-second interval updates.

### 5. Curated SIP & Stock Recommendations (India vs Global)
* **India Specific (🇮🇳)**:
  * **Top Performing SIPs**: Quant Small Cap Fund (34.8% 5Y CAGR), Parag Parikh Flexi Cap Fund (24.2% 5Y CAGR), Nippon India Small Cap (31.5% 5Y CAGR), Mirae Asset Large & Midcap, ICICI Prudential Technology, Motilal Oswal Midcap Fund.
  * **Top Performing Stocks**: Reliance Industries, TCS, HDFC Bank, Tata Motors, Larsen & Toubro, Infosys, Bharti Airtel, Trent (with live prices and analyst ratings).
* **Global Specific (🌐)**:
  * **Top Index SIPs / DCA ETFs**: Vanguard S&P 500 ETF (VOO), Invesco QQQ Trust, Schwab US Dividend Equity (SCHD), iShares Semiconductor (SOXX), Vanguard Total World Stock (VT).
  * **Top Global Stocks**: NVIDIA (NVDA), Microsoft (MSFT), Apple (AAPL), Amazon (AMZN), Alphabet (GOOGL), Meta (META), Broadcom (AVGO), Tesla (TSLA).
* **Interactive Compound SIP Calculator**:
  * Dynamic sliders for Monthly Investment, Expected CAGR, Tenure (1-30 yrs), and Annual Step-Up % (+10%/yr).
  * Visualizes Total Invested, Wealth Gained, Maturity Corpus, and interactive growth curves.

### 6. Personal Budget Engine
* **50/30/20 Diagnostics**: Live tracking of Needs vs Wants vs Savings against institutional benchmarks.
* **Subscription Creep Auditor**: Audits all recurring streaming, SaaS, and gym memberships with monthly burn and annual drag calculations.
* **Actionable Advice**: Prioritized recommendation cards with estimated financial ROI.

---

## 🚀 Quickstart & Launching

### Launch the Application Server
Run the startup script:
```bash
bash /home/eqzinit/wyvern/run.sh
```
Or start via Uvicorn directly:
```bash
python3 -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open your browser at:
```
http://localhost:8000
```

---

## 🧪 Running Automated Tests
Run the unit test suite:
```bash
python3 -m unittest /home/eqzinit/wyvern/tests/test_wyvern.py
```

---

## 📁 Project Architecture
```
/home/eqzinit/wyvern/
├── server/
│   ├── __init__.py
│   ├── main.py              # FastAPI server & API endpoints
│   ├── ml_models.py         # Categorization, Forecasting, Anomaly ML models
│   ├── plaid_service.py     # Plaid API client & Sandbox OAuth simulator
│   ├── market_service.py    # Live market quotes & SIP/Stock recommendations
│   ├── budget_engine.py     # 50/30/20 diagnostics & subscription auditor
│   ├── data_store.py        # Transaction ledger & state management
│   └── synthetic_data.py    # Realistic initial financial profiles & seeded anomalies
├── static/
│   ├── css/
│   │   └── nothing_theme.css# Nothing OS NDOT typography, bento cards & glyphs
│   ├── js/
│   │   ├── app.js           # Frontend state, event listeners & tab views
│   │   ├── charts.js        # Minimalist Chart.js dark theme visualizations
│   │   └── haptics.js       # Synthesized Web Audio API tactile acoustic clicks
│   └── index.html           # Single-page interactive Nothing OS dashboard
├── tests/
│   └── test_wyvern.py       # Comprehensive unit test suite
├── requirements.txt         # Python dependencies
├── run.sh                   # App launcher
└── README.md                # Documentation
```
