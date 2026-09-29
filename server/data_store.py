"""
Wyvern Data Store: User Profile State, Transactions Repository, and INR Financial Ledger
Supports interactive user onboarding questionnaire, dynamic profile recalibration, and persistence.
"""
import os
import json
import copy
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from .ml_models import categorizer, anomaly_detector, forecaster

PROFILE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_profile.json")

DEFAULT_CATEGORIES = [
    "Food & Dining",
    "Bills & Utilities",
    "Transportation",
    "Subscriptions & Digital",
    "Shopping & Retail",
    "Health & Fitness",
    "Entertainment & Leisure"
]

class DataStore:
    def __init__(self):
        self.profile_configured = False
        self.profile_data: Dict[str, Any] = {}
        self.accounts: List[Dict[str, Any]] = []
        self.transactions: List[Dict[str, Any]] = []
        self.monthly_history: List[Dict[str, Any]] = []
        self.plaid_status = {
            "connected": True,
            "institution_name": "HDFC Bank / RBI Account Aggregator",
            "item_id": "item_in_hdfc_8921",
            "last_synced": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "sync_mode": "Fintech API Sandbox (INR)",
            "environment": "sandbox"
        }
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(PROFILE_FILE):
            try:
                with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.setup_user_profile(saved, persist=False)
                    return
            except Exception as e:
                print(f"Error loading saved profile: {e}")

        # Fresh unconfigured state - requires user input via onboarding questionnaire
        self.profile_configured = False
        self.accounts = [
            {
                "id": "acc_sav_01",
                "name": "Primary Savings Account",
                "institution": "HDFC Bank",
                "type": "depository",
                "subtype": "savings",
                "balance": 0.0,
                "currency": "INR",
                "mask": "8921",
                "status": "pending_setup"
            },
            {
                "id": "acc_inv_02",
                "name": "Direct Mutual Fund Portfolio",
                "institution": "Zerodha / Groww",
                "type": "investment",
                "subtype": "brokerage",
                "balance": 0.0,
                "currency": "INR",
                "mask": "4412",
                "status": "pending_setup"
            },
            {
                "id": "acc_cc_03",
                "name": "RuPay / Visa Platinum Card",
                "institution": "ICICI Bank",
                "type": "credit",
                "subtype": "credit card",
                "balance": 0.0,
                "limit": 150000.0,
                "currency": "INR",
                "mask": "7810",
                "status": "pending_setup"
            }
        ]
        self.transactions = []
        self.monthly_history = []

    def setup_user_profile(self, profile: Dict[str, Any], persist: bool = True):
        """
        Takes real user inputs from onboarding questionnaire and builds financial profile in INR (₹).
        """
        salary = float(profile.get("monthly_salary", 0.0))
        secondary = float(profile.get("secondary_income", 0.0))
        total_income = salary + secondary

        savings_bal = float(profile.get("savings_balance", 0.0))
        invest_bal = float(profile.get("investment_balance", 0.0))
        debt_bal = float(profile.get("credit_debt", 0.0))
        target_sip = float(profile.get("target_monthly_sip", 0.0))

        cat_spend = profile.get("category_spending", {})
        total_expense = sum(float(v) for v in cat_spend.values())

        # Update accounts
        self.accounts = [
            {
                "id": "acc_sav_01",
                "name": "Primary Savings Account",
                "institution": profile.get("primary_bank", "HDFC Bank Ltd"),
                "type": "depository",
                "subtype": "savings",
                "balance": round(savings_bal, 2),
                "currency": "INR",
                "mask": "8921",
                "status": "active"
            },
            {
                "id": "acc_inv_02",
                "name": "Equity & Mutual Fund Vault",
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
                "name": "Credit Card Account",
                "institution": "ICICI / HDFC Bank",
                "type": "credit",
                "subtype": "credit card",
                "balance": round(-abs(debt_bal), 2),
                "limit": max(150000.0, debt_bal * 2.5),
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
                "merchant": "Monthly Payroll Salary Inflow",
                "category": "Income & Deposits",
                "pending": False,
                "channel": "online",
                "currency": "INR"
            })

        # 2. SIP Investment if specified
        if target_sip > 0:
            tx_list.append({
                "id": f"tx_sip_{now.strftime('%Y%m%d')}_02",
                "account_id": "acc_sav_01",
                "amount": round(target_sip, 2),
                "date": (now - timedelta(days=3)).isoformat(),
                "merchant": "Monthly Direct Mutual Fund SIP Auto-Debit",
                "category": "Investments & Savings",
                "pending": False,
                "channel": "online",
                "currency": "INR"
            })

        # 3. Category spending distribution
        merchant_map = {
            "Food & Dining": [("Swiggy / Zomato Food Orders", 0.4), ("Blinkit / Instamart Groceries", 0.6)],
            "Bills & Utilities": [("Electricity & Broadband Bill Payment", 0.5), ("House Rent & Maintenance", 0.5)],
            "Transportation": [("Fuel & Metro / Ola Cabs Transit", 1.0)],
            "Subscriptions & Digital": [("Streaming Services (Netflix/Spotify/Prime)", 1.0)],
            "Shopping & Retail": [("Amazon / Myntra Retail Purchases", 1.0)],
            "Health & Fitness": [("Pharmacy & Gym / Fitness Membership", 1.0)],
            "Entertainment & Leisure": [("Weekend Movie / Dining Outings", 1.0)]
        }

        counter = 10
        for cat, amt in cat_spend.items():
            amt = float(amt)
            if amt <= 0:
                continue
            splits = merchant_map.get(cat, [(f"{cat} Expenses", 1.0)])
            for m_name, fraction in splits:
                counter += 1
                sub_amt = round(amt * fraction, 2)
                tx_list.append({
                    "id": f"tx_user_{now.strftime('%Y%m%d')}_{counter}",
                    "account_id": "acc_cc_03" if cat in ["Food & Dining", "Shopping & Retail", "Subscriptions & Digital"] else "acc_sav_01",
                    "amount": sub_amt,
                    "date": (now - timedelta(days=(counter % 15) + 1)).isoformat(),
                    "merchant": m_name,
                    "category": cat,
                    "pending": False,
                    "channel": "online" if counter % 2 == 0 else "in_store",
                    "currency": "INR"
                })

        self.transactions = tx_list

        # Historical monthly trend for forecasting based on the user's real numbers
        monthly_net = total_income - total_expense - target_sip
        self.monthly_history = []
        for i in range(5, -1, -1):
            m_date = now - timedelta(days=30 * i)
            # Add slight realistic past variance around user baseline
            var_pct = 1.0 + ((-1)**i * 0.04)
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

        # Fit ML models to user data
        if len(self.transactions) >= 5:
            anomaly_detector.fit(self.transactions)

        if persist:
            try:
                with open(PROFILE_FILE, "w", encoding="utf-8") as f:
                    json.dump(profile, f, indent=2)
            except Exception as e:
                print(f"Failed to persist profile: {e}")

        return self.get_summary_stats()

    def reset_profile(self):
        """Clears user profile and prompts onboarding wizard."""
        if os.path.exists(PROFILE_FILE):
            try:
                os.remove(PROFILE_FILE)
            except:
                pass
        self._load_or_init()

    def get_accounts(self) -> List[Dict[str, Any]]:
        return self.accounts

    def get_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
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

    def get_summary_stats(self) -> Dict[str, Any]:
        total_assets = sum(a["balance"] for a in self.accounts if a["balance"] > 0)
        total_liabilities = sum(abs(a["balance"]) for a in self.accounts if a["balance"] < 0)
        net_worth = total_assets - total_liabilities

        recent_expenses = [t["amount"] for t in self.transactions if t.get("category") != "Income & Deposits"]
        current_spending = sum(recent_expenses)

        annotated = anomaly_detector.detect_all(self.transactions)
        anomalies = [t for t in annotated if t.get("anomaly_analysis", {}).get("is_anomaly")]

        forecast_data = forecaster.forecast(self.monthly_history, horizon_months=6)

        return {
            "profile_configured": self.profile_configured,
            "profile_data": self.profile_data,
            "currency": "INR",
            "currency_symbol": "₹",
            "net_worth": round(net_worth, 2),
            "total_assets": round(total_assets, 2),
            "total_liabilities": round(total_liabilities, 2),
            "current_period_spending": round(current_spending, 2),
            "anomaly_count": len(anomalies),
            "anomalies": anomalies[:5],
            "forecast": forecast_data,
            "plaid_status": self.plaid_status
        }

store = DataStore()
