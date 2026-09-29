"""
Wyvern Fintech OS - Main FastAPI Backend Application (INR Edition)
"""
import os
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .data_store import store
from .ml_models import categorizer, forecaster, anomaly_detector
from .market_service import market_service
from .budget_engine import budget_engine
from .plaid_service import plaid_service

app = FastAPI(
    title="Wyvern Fintech OS",
    description="Intelligent financial operating system in Indian Rupees (₹) with real user profile ingestion, ML spending categorization, anomaly detection, savings forecasting, Plaid/Account Aggregator integration, and India & Global investment intelligence.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schemas
class UserProfileSetupRequest(BaseModel):
    monthly_salary: float
    secondary_income: Optional[float] = 0.0
    savings_balance: float
    investment_balance: float
    credit_debt: Optional[float] = 0.0
    target_monthly_sip: Optional[float] = 0.0
    category_spending: Dict[str, float]
    primary_bank: Optional[str] = "HDFC Bank Ltd"

class CategorizeRequest(BaseModel):
    description: str

class TransactionCreateRequest(BaseModel):
    merchant: str
    amount: float
    category: Optional[str] = None
    account_id: Optional[str] = None
    channel: Optional[str] = "online"

class SipCalculateRequest(BaseModel):
    monthly_investment: float
    annual_return_pct: float
    years: int
    step_up_pct: Optional[float] = 0.0

class PlaidExchangeRequest(BaseModel):
    public_token: str
    institution_name: Optional[str] = "HDFC Bank Ltd (India)"

# API Endpoints
@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "Wyvern", "currency": "INR", "engine": "online"}

@app.get("/api/profile")
def get_profile():
    return {
        "profile_configured": store.profile_configured,
        "profile_data": store.profile_data
    }

@app.post("/api/profile/setup")
def setup_profile(req: UserProfileSetupRequest):
    """Configures Wyvern with real user earnings, spending by category, and asset balances."""
    res = store.setup_user_profile(req.model_dump())
    return {"status": "success", "summary": res}

@app.post("/api/profile/reset")
def reset_profile():
    """Resets the profile to unconfigured state so the user can re-enter numbers."""
    store.reset_profile()
    return {"status": "reset", "profile_configured": False}

@app.get("/api/overview")
def get_overview():
    """Provides high-level dashboard metrics, net worth, forecast snapshot, and anomaly alerts in INR."""
    summary = store.get_summary_stats()
    accounts = store.get_accounts()
    budget = budget_engine.analyze_budget(store.get_transactions(), accounts)
    return {
        **summary,
        "accounts": accounts,
        "rule_50_30_20": budget["rule_50_30_20"],
        "top_recommendations": budget["recommendations"][:3],
        "potential_monthly_savings": budget["total_potential_monthly_savings"]
    }

@app.get("/api/transactions")
def get_transactions(limit: int = 50):
    """Returns list of user transactions augmented with ML category and anomaly diagnosis."""
    return store.get_transactions(limit=limit)

@app.post("/api/transactions")
def add_transaction(req: TransactionCreateRequest):
    """Adds a new real transaction, processes it through ML models, and saves it."""
    tx = store.add_transaction(req.model_dump())
    return {"status": "success", "transaction": tx}

@app.post("/api/ml/categorize")
def ml_categorize(req: CategorizeRequest):
    """Runs the spending categorizer model on any raw transaction narrative."""
    result = categorizer.predict(req.description)
    return result

@app.get("/api/ml/forecast")
def ml_forecast(horizon: int = 6):
    """Calculates ML savings forecast, confidence bounds, and scenario simulations based on user profile."""
    history = store.get_monthly_history()
    return forecaster.forecast(history, horizon_months=horizon)

@app.get("/api/ml/anomalies")
def ml_anomalies():
    """Returns all transactions with detected anomalies and severity scoring."""
    txs = store.get_transactions(limit=100)
    anomalies = [t for t in txs if t.get("anomaly_analysis", {}).get("is_anomaly")]
    return {
        "count": len(anomalies),
        "anomalies": anomalies
    }

@app.get("/api/budget")
def get_budget_analysis():
    """Returns comprehensive budget breakdown, 50/30/20 metrics, subscription audits, and personalized tips."""
    txs = store.get_transactions(limit=100)
    accs = store.get_accounts()
    return budget_engine.analyze_budget(txs, accs)

@app.get("/api/market/indices")
def get_market_indices():
    """Fetches live stock market index feeds (India & Global)."""
    return market_service.get_indices()

@app.get("/api/market/india")
def get_india_market():
    """Returns India specific top performing SIPs and stocks with live quotes."""
    return market_service.get_india_recommendations()

@app.get("/api/market/global")
def get_global_market():
    """Returns Global specific top performing SIPs/ETFs and stocks with live quotes."""
    return market_service.get_global_recommendations()

@app.post("/api/calculator/sip")
def calculate_sip(req: SipCalculateRequest):
    """Calculates monthly compound growth for SIP investments with step-up in INR."""
    return market_service.calculate_sip(
        monthly_investment=req.monthly_investment,
        annual_return_pct=req.annual_return_pct,
        years=req.years,
        step_up_pct=req.step_up_pct or 0.0
    )

# Plaid / Account Aggregator API Endpoints
@app.post("/api/plaid/create-link-token")
def plaid_create_link_token():
    return plaid_service.create_link_token()

@app.post("/api/plaid/exchange-token")
def plaid_exchange_token(req: PlaidExchangeRequest):
    result = plaid_service.exchange_public_token(req.public_token, req.institution_name)
    store.plaid_status["connected"] = True
    store.plaid_status["institution_name"] = req.institution_name
    store.plaid_status["last_synced"] = result.get("synced_at", "Just now")
    return result

@app.post("/api/plaid/sync")
def plaid_sync():
    res = plaid_service.sync_transactions()
    store.plaid_status["last_synced"] = res["last_synced"]
    return res

# Mount static directory
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Wyvern Fintech OS backend running. Index page missing."}
