"""
Wyvern Data Store: User Profile State, Transactions Repository, and INR Financial Ledger
Supports interactive user onboarding questionnaire with dynamic Money Goals curation:
- GROW_WEALTH (Long-Term Compounding & Step-Up SIPs)
- INCREASE_MONEY (Aggressive Capital Growth & High-Alpha Equities)
- SAVE_MONEY (Capital Preservation, Expense Trimming & Emergency Runway)
"""
import os
import json
import copy
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from .ml_models import categorizer, anomaly_detector, forecaster

PROFILE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_profile.json")

class DataStore:
    def __init__(self):
        self.profile_configured = False
        self.profile_data: Dict[str, Any] = {}
        self.financial_goal = "GROW_WEALTH" # "GROW_WEALTH" | "INCREASE_MONEY" | "SAVE_MONEY"
        self.target_goal_amount = 0.0
        self.target_goal_timeline_years = 5
        self.accounts: List[Dict[str, Any]] = []
        self.transactions: List[Dict[str, Any]] = []
        self.monthly_history: List[Dict[str, Any]] = []
        self.plaid_status = {
            "connected": True,
            "institution_name": "Account Aggregator / Bank API",
            "item_id": "item_in_active_01",
            "last_synced": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "sync_mode": "Fintech API (INR)",
            "environment": "sandbox"
        }
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(PROFILE_FILE):
            try:
                with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if saved and saved.get("monthly_salary", 0) > 0:
                        self.setup_user_profile(saved, persist=False)
                        return
            except Exception as e:
                print(f"Error loading saved profile: {e}")

        # Fresh unconfigured state
        self.profile_configured = False
        self.profile_data = {}
        self.financial_goal = "GROW_WEALTH"
        self.target_goal_amount = 0.0
        self.target_goal_timeline_years = 5
        self.accounts = [
            {
                "id": "acc_sav_01",
                "name": "Bank Savings & Cash",
                "institution": "Primary Bank",
                "type": "depository",
                "subtype": "savings",
                "balance": 0.0,
                "currency": "INR",
                "mask": "----",
                "status": "awaiting_calibration"
            },
            {
                "id": "acc_inv_02",
                "name": "Investments & Mutual Funds",
                "institution": "Brokerage / Demat",
                "type": "investment",
                "subtype": "brokerage",
                "balance": 0.0,
                "currency": "INR",
                "mask": "----",
                "status": "awaiting_calibration"
            },
            {
                "id": "acc_cc_03",
                "name": "Credit Card / Liabilities",
                "institution": "Card Issuer",
                "type": "credit",
                "subtype": "credit card",
                "balance": 0.0,
                "limit": 0.0,
                "currency": "INR",
                "mask": "----",
                "status": "awaiting_calibration"
            }
        ]
        self.transactions = []
        self.monthly_history = []

    def setup_user_profile(self, profile: Dict[str, Any], persist: bool = True):
        """
        Takes real user inputs from onboarding questionnaire including money goals and builds profile.
        """
        salary = float(profile.get("monthly_salary", 0.0))
        secondary = float(profile.get("secondary_income", 0.0))
        total_income = salary + secondary

        savings_bal = float(profile.get("savings_balance", 0.0))
        invest_bal = float(profile.get("investment_balance", 0.0))
        debt_bal = float(profile.get("credit_debt", 0.0))
        target_sip = float(profile.get("target_monthly_sip", 0.0))

        # Money Goal Configuration
        self.financial_goal = profile.get("financial_goal", "GROW_WEALTH").upper()
        if self.financial_goal not in ["GROW_WEALTH", "INCREASE_MONEY", "SAVE_MONEY"]:
            self.financial_goal = "GROW_WEALTH"

        self.target_goal_amount = float(profile.get("target_goal_amount", 0.0))
        if self.target_goal_amount <= 0:
            # Smart default target based on goal and current net worth
            curr_nw = savings_bal + invest_bal - debt_bal
            if self.financial_goal == "GROW_WEALTH":
                self.target_goal_amount = max(2500000.0, curr_nw * 2.5)
            elif self.financial_goal == "INCREASE_MONEY":
                self.target_goal_amount = max(5000000.0, curr_nw * 3.5)
            else: # SAVE_MONEY
                self.target_goal_amount = max(1000000.0, curr_nw * 1.5)

        self.target_goal_timeline_years = int(profile.get("target_goal_timeline_years", 5))

        cat_spend = profile.get("category_spending", {})
        total_expense = sum(float(v) for v in cat_spend.values())

        # Update accounts
        self.accounts = [
            {
                "id": "acc_sav_01",
                "name": "Primary Bank Savings & Liquid Cash",
                "institution": profile.get("primary_bank", "HDFC / SBI / ICICI Bank"),
                "type": "depository",
                "subtype": "savings",
                "balance": round(savings_bal, 2),
                "currency": "INR",
                "mask": "8921",
                "status": "active"
            },
            {
                "id": "acc_inv_02",
                "name": "Equity, Stocks & Mutual Funds Portfolio",
                "institution": profile.get("broker_name", "Zerodha / Groww"),
                "type": "investment",
                "subtype": "brokerage",
                "balance": round(invest_bal, 2),
                "currency": "INR",
                "mask": "4412",
                "status": "active"
            },
            {
                "id": "acc_cc_03",
                "name": "Credit Card & Outstanding Liabilities",
                "institution": "Card Issuer / Bank",
                "type": "credit",
                "subtype": "credit card",
                "balance": round(-abs(debt_bal), 2),
                "limit": max(100000.0, debt_bal * 2.0),
                "currency": "INR",
                "mask": "7810",
                "status": "active"
            }
        ]

        # Generate realistic initial transactions representing the user's declared spending
        now = datetime.now(timezone.utc)
        tx_list = []

        # 1. Primary Salary credit
        if total_income > 0:
            tx_list.append({
                "id": f"tx_inc_{now.strftime('%Y%m%d')}_01",
                "account_id": "acc_sav_01",
                "amount": round(total_income, 2),
                "date": (now - timedelta(days=2)).isoformat(),
                "merchant": "Monthly Take-Home Salary & Inflow",
                "category": "Income & Deposits",
                "pending": False,
                "channel": "online",
                "currency": "INR"
            })

        # 2. SIP Investment
        if target_sip > 0:
            tx_list.append({
                "id": f"tx_sip_{now.strftime('%Y%m%d')}_02",
                "account_id": "acc_sav_01",
                "amount": round(target_sip, 2),
                "date": (now - timedelta(days=3)).isoformat(),
                "merchant": "Monthly Systematic Investment Plan (SIP)",
                "category": "Investments & Savings",
                "pending": False,
                "channel": "online",
                "currency": "INR"
            })

        # 3. Category spending distribution
        merchant_map = {
            "Food & Dining": [("Swiggy / Zomato Online Orders", 0.45), ("Supermarket & Grocery Delivery", 0.55)],
            "Bills & Utilities": [("Electricity & Broadband Bill Payment", 0.3), ("House Rent & Maintenance", 0.7)],
            "Transportation": [("Fuel & Metro / Ride Commute", 1.0)],
            "Subscriptions & Digital": [("OTT Streaming & Digital Subscriptions", 1.0)],
            "Shopping & Retail": [("E-Commerce & Retail Shopping", 1.0)],
            "Health & Fitness": [("Pharmacy & Gym / Fitness Dues", 1.0)],
            "Entertainment & Leisure": [("Weekend Movies & Dining Outings", 1.0)]
        }

        counter = 10
        for cat, amt in cat_spend.items():
            amt = float(amt)
            if amt <= 0:
                continue
            splits = merchant_map.get(cat, [(f"{cat} Spend", 1.0)])
            for m_name, fraction in splits:
                counter += 1
                sub_amt = round(amt * fraction, 2)
                tx_list.append({
                    "id": f"tx_user_{now.strftime('%Y%m%d')}_{counter}",
                    "account_id": "acc_cc_03" if cat in ["Food & Dining", "Shopping & Retail", "Subscriptions & Digital"] else "acc_sav_01",
                    "amount": sub_amt,
                    "date": (now - timedelta(days=(counter % 18) + 1)).isoformat(),
                    "merchant": m_name,
                    "category": cat,
                    "pending": False,
                    "channel": "online" if counter % 2 == 0 else "in_store",
                    "currency": "INR"
                })

        self.transactions = tx_list

        # Historical monthly trend tailored to goal
        self.monthly_history = []
        for i in range(5, -1, -1):
            m_date = now - timedelta(days=30 * i)
            var_pct = 1.0 + ((-1)**i * 0.03)
            hist_inc = round(total_income * var_pct, 2)
            hist_sp = round((total_expense + target_sip) * var_pct, 2)
            self.monthly_history.append({
                "month": m_date.strftime("%Y-%m"),
                "income": hist_inc,
                "spending": hist_sp,
                "savings": round(hist_inc - hist_sp, 2)
            })

        self.profile_data = profile
        self.profile_configured = True

        if len(self.transactions) >= 5:
            anomaly_detector.fit(self.transactions)

        if persist:
            try:
                os.makedirs(os.path.dirname(PROFILE_FILE), exist_ok=True)
                with open(PROFILE_FILE, "w", encoding="utf-8") as f:
                    json.dump(profile, f, indent=2)
            except Exception as e:
                print(f"Failed to persist profile: {e}")

        return self.get_summary_stats()

    def reset_profile(self):
        if os.path.exists(PROFILE_FILE):
            try:
                os.remove(PROFILE_FILE)
            except:
                pass
        self._load_or_init()

    def get_accounts(self) -> List[Dict[str, Any]]:
        return self.accounts

    def get_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.profile_configured or not self.transactions:
            return []
        augmented = anomaly_detector.detect_all(self.transactions)
        augmented.sort(key=lambda x: x.get("date", ""), reverse=True)
        return augmented[:limit]

    def add_transaction(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        merchant = tx_data.get("merchant", tx_data.get("name", "Unknown Merchant"))
        amount = float(tx_data.get("amount", 0.0))
        date_str = tx_data.get("date", datetime.now(timezone.utc).isoformat())

        cat_prediction = categorizer.predict(merchant)
        category = tx_data.get("category") or cat_prediction["category"]

        new_tx = {
            "id": f"tx_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.transactions) + 1}",
            "account_id": tx_data.get("account_id", self.accounts[0]["id"] if self.accounts else "acc_sav_01"),
            "amount": amount,
            "date": date_str,
            "merchant": merchant,
            "category": category,
            "pending": tx_data.get("pending", False),
            "channel": tx_data.get("channel", "online"),
            "currency": "INR",
            "ml_prediction": cat_prediction
        }

        anomaly_eval = anomaly_detector.analyze_transaction(new_tx, self.transactions[-10:])
        new_tx["anomaly_analysis"] = anomaly_eval

        self.transactions.insert(0, new_tx)

        for acc in self.accounts:
            if acc["id"] == new_tx["account_id"]:
                if new_tx["category"] == "Income & Deposits":
                    acc["balance"] += amount
                else:
                    if acc["type"] == "credit":
                        acc["balance"] -= amount
                    else:
                        acc["balance"] -= amount
                break

        return new_tx

    def get_monthly_history(self) -> List[Dict[str, Any]]:
        return self.monthly_history

    def get_goal_metrics(self, net_worth: float, monthly_savings: float) -> Dict[str, Any]:
        """Calculates progress and pacing metrics for the user's specific money goal."""
        goal = self.financial_goal
        target = self.target_goal_amount
        timeline_yrs = self.target_goal_timeline_years
        total_months = max(12, timeline_yrs * 12)

        # Baseline progress
        progress_val = max(0.0, net_worth)
        progress_pct = round(min(100.0, (progress_val / target * 100.0)), 1) if target > 0 else 0.0
        remaining_corpus = max(0.0, target - progress_val)

        # Required monthly savings pacing
        required_monthly = round(remaining_corpus / total_months, 2) if total_months > 0 else 0.0

        goal_meta = {
            "GROW_WEALTH": {
                "title": "GROW WEALTH // COMPOUNDING ALPHA",
                "tagline": "Long-Term Systematic Wealth Compounding & Step-Up Equity Portfolio",
                "focus_areas": ["Top-Quartile Mutual Fund SIPs", "Annual Step-Up Disciplined Compounding", "Diversified Global Index Hedges"],
                "recommended_asset_split": "60% Equity SIPs / 25% Liquid Reserves / 15% Thematic Growth",
                "curated_badge": "MISSION: GROW WEALTH"
            },
            "INCREASE_MONEY": {
                "title": "INCREASE MONEY // AGGRESSIVE CASHFLOW & GROWTH",
                "tagline": "Maximizing Income Velocity, Momentum Equities & High-Growth Opportunities",
                "focus_areas": ["High-Alpha Growth Equities", "Income Velocity Scaling", "High-Beta Sectoral Expansion"],
                "recommended_asset_split": "75% High-Growth Equities / 15% Swing Allocation / 10% Cash",
                "curated_badge": "MISSION: INCREASE MONEY"
            },
            "SAVE_MONEY": {
                "title": "SAVE MONEY // CAPITAL PRESERVATION & LEAK TRIMMING",
                "tagline": "Aggressive Expense Reduction, 12-Month Emergency Vault & Zero Debt",
                "focus_areas": ["Discretionary Outflow Lockdown", "Subscription Creep Eradication", "High-Yield Arbitrage & Liquid Parking"],
                "recommended_asset_split": "50% High-Yield Liquid Vaults / 30% Debt Elimination / 20% Safe Debt Index",
                "curated_badge": "MISSION: SAVE MONEY"
            }
        }.get(goal, {
            "title": "GROW WEALTH // COMPOUNDING ALPHA",
            "tagline": "Long-Term Systematic Wealth Compounding",
            "focus_areas": ["Equity SIPs", "Index Hedges"],
            "recommended_asset_split": "60% Equity / 40% Liquid",
            "curated_badge": "MISSION: GROW WEALTH"
        })

        return {
            "goal": goal,
            "target_amount": round(target, 2),
            "timeline_years": timeline_yrs,
            "current_progress_amount": round(progress_val, 2),
            "progress_pct": progress_pct,
            "remaining_amount": round(remaining_corpus, 2),
            "required_monthly_savings": required_monthly,
            "current_monthly_savings": round(monthly_savings, 2),
            "is_on_track": monthly_savings >= required_monthly,
            "velocity_ratio": round((monthly_savings / required_monthly * 100), 1) if required_monthly > 0 else 100.0,
            **goal_meta
        }

    def get_summary_stats(self) -> Dict[str, Any]:
        if not self.profile_configured:
            return {
                "profile_configured": False,
                "profile_data": {},
                "financial_goal": "GROW_WEALTH",
                "currency": "INR",
                "currency_symbol": "₹",
                "net_worth": 0.0,
                "total_assets": 0.0,
                "total_liabilities": 0.0,
                "current_period_spending": 0.0,
                "anomaly_count": 0,
                "anomalies": [],
                "goal_metrics": None,
                "forecast": {
                    "current_monthly_avg_savings": 0.0,
                    "current_monthly_avg_spending": 0.0,
                    "current_savings_rate_pct": 0.0,
                    "emergency_runway_months": 0.0,
                    "projections": [],
                    "scenarios_6_month": {
                        "conservative": {"total": 0.0, "monthly_avg": 0.0, "label": "Conservative (-18%)"},
                        "baseline": {"total": 0.0, "monthly_avg": 0.0, "label": "Baseline Trajectory"},
                        "wyvern_optimized": {"total": 0.0, "monthly_avg": 0.0, "extra_accumulated": 0.0, "label": "Wyvern Optimized"}
                    }
                },
                "plaid_status": self.plaid_status
            }

        total_assets = sum(a["balance"] for a in self.accounts if a["balance"] > 0)
        total_liabilities = sum(abs(a["balance"]) for a in self.accounts if a["balance"] < 0)
        net_worth = total_assets - total_liabilities

        recent_expenses = [t["amount"] for t in self.transactions if t.get("category") != "Income & Deposits"]
        current_spending = sum(recent_expenses)

        annotated = anomaly_detector.detect_all(self.transactions)
        anomalies = [t for t in annotated if t.get("anomaly_analysis", {}).get("is_anomaly")]

        forecast_data = forecaster.forecast(self.monthly_history, horizon_months=6)

        current_savings = forecast_data.get("current_monthly_avg_savings", 0.0)
        goal_metrics = self.get_goal_metrics(net_worth, current_savings)

        return {
            "profile_configured": True,
            "profile_data": self.profile_data,
            "financial_goal": self.financial_goal,
            "currency": "INR",
            "currency_symbol": "₹",
            "net_worth": round(net_worth, 2),
            "total_assets": round(total_assets, 2),
            "total_liabilities": round(total_liabilities, 2),
            "current_period_spending": round(current_spending, 2),
            "anomaly_count": len(anomalies),
            "anomalies": anomalies[:5],
            "goal_metrics": goal_metrics,
            "forecast": forecast_data,
            "plaid_status": self.plaid_status
        }

store = DataStore()
