"""
Wyvern Data Store: In-memory state and transaction repository with anomaly metadata
"""
import copy
from datetime import datetime
from typing import List, Dict, Any
from .synthetic_data import ACCOUNTS, SEED_TRANSACTIONS, MONTHLY_HISTORY
from .ml_models import categorizer, anomaly_detector, forecaster

class DataStore:
    def __init__(self):
        self.accounts = copy.deepcopy(ACCOUNTS)
        self.transactions = copy.deepcopy(SEED_TRANSACTIONS)
        self.monthly_history = copy.deepcopy(MONTHLY_HISTORY)
        self.plaid_status = {
            "connected": True,
            "institution_name": "JPMorgan Chase & Co.",
            "item_id": "item_mock_chase_8912",
            "last_synced": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sync_mode": "Plaid Sandbox API",
            "environment": "sandbox"
        }
        # Fit anomaly detector initially
        anomaly_detector.fit(self.transactions)

    def get_accounts(self) -> List[Dict[str, Any]]:
        return self.accounts

    def get_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        # Augment with anomaly evaluation
        augmented = anomaly_detector.detect_all(self.transactions)
        # Sort descending by date
        augmented.sort(key=lambda x: x.get("date", ""), reverse=True)
        return augmented[:limit]

    def add_transaction(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds a new transaction, runs ML categorization if not specified or to verify,
        evaluates for anomalies, updates account balance, and stores.
        """
        merchant = tx_data.get("merchant", tx_data.get("name", "Unknown Merchant"))
        amount = float(tx_data.get("amount", 0.0))
        date_str = tx_data.get("date", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))

        # ML Categorization
        cat_prediction = categorizer.predict(merchant)
        category = tx_data.get("category") or cat_prediction["category"]

        new_tx = {
            "id": f"tx_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.transactions) + 1}",
            "account_id": tx_data.get("account_id", self.accounts[0]["id"]),
            "amount": amount,
            "date": date_str,
            "merchant": merchant,
            "category": category,
            "pending": tx_data.get("pending", False),
            "channel": tx_data.get("channel", "online"),
            "currency": tx_data.get("currency", "USD"),
            "ml_prediction": cat_prediction
        }

        # Analyze anomaly against recent
        anomaly_eval = anomaly_detector.analyze_transaction(new_tx, self.transactions[-10:])
        new_tx["anomaly_analysis"] = anomaly_eval

        # Append to transactions
        self.transactions.insert(0, new_tx)

        # Update account balance
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
        # Compute total net worth
        total_assets = sum(a["balance"] for a in self.accounts if a["balance"] > 0)
        total_liabilities = sum(abs(a["balance"]) for a in self.accounts if a["balance"] < 0)
        net_worth = total_assets - total_liabilities

        # Current month spending
        recent_expenses = [t["amount"] for t in self.transactions if t.get("category") != "Income & Deposits"]
        current_spending = sum(recent_expenses[:20])

        # Anomaly count
        annotated = anomaly_detector.detect_all(self.transactions)
        anomalies = [t for t in annotated if t.get("anomaly_analysis", {}).get("is_anomaly")]

        # Forecast
        forecast_data = forecaster.forecast(self.monthly_history, horizon_months=6)

        return {
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
