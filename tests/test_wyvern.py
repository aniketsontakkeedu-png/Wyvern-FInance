"""
Wyvern Fintech OS - Automated Test Suite (Goal-Curated INR Edition)
Verifies user profile setup & calibration, Money Goals curation, ML models, and API endpoints.
"""
import sys
import os
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.main import app
from server.ml_models import categorizer, forecaster, anomaly_detector
from server.market_service import market_service
from server.budget_engine import budget_engine
from server.data_store import store

client = TestClient(app)

class TestWyvernFintechOS(unittest.TestCase):

    def test_health_check(self):
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["currency"], "INR")

    def test_profile_onboarding_with_money_goals(self):
        # User submits onboarding profile with GROW_WEALTH goal
        profile_payload = {
            "monthly_salary": 110000.0,
            "secondary_income": 15000.0,
            "savings_balance": 400000.0,
            "investment_balance": 850000.0,
            "credit_debt": 25000.0,
            "target_monthly_sip": 30000.0,
            "financial_goal": "GROW_WEALTH",
            "target_goal_amount": 5000000.0,
            "target_goal_timeline_years": 5,
            "category_spending": {
                "Food & Dining": 18000.0,
                "Bills & Utilities": 25000.0,
                "Transportation": 7000.0,
                "Subscriptions & Digital": 3500.0,
                "Shopping & Retail": 10000.0,
                "Health & Fitness": 4500.0,
                "Entertainment & Leisure": 6000.0
            }
        }
        res = client.post("/api/profile/setup", json=profile_payload)
        self.assertEqual(res.status_code, 200)

        # Verify overview reflects user inputs and goal metrics
        ov_res = client.get("/api/overview")
        self.assertEqual(ov_res.status_code, 200)
        ov = ov_res.json()
        self.assertTrue(ov["profile_configured"])
        self.assertEqual(ov["financial_goal"], "GROW_WEALTH")
        self.assertIsNotNone(ov["goal_metrics"])
        self.assertEqual(ov["goal_metrics"]["target_amount"], 5000000.0)

    def test_goal_switching(self):
        # Test switching to SAVE_MONEY
        res_save = client.post("/api/profile/goal", json={"financial_goal": "SAVE_MONEY"})
        self.assertEqual(res_save.status_code, 200)
        self.assertEqual(res_save.json()["financial_goal"], "SAVE_MONEY")

        ov_res = client.get("/api/overview")
        ov = ov_res.json()
        self.assertEqual(ov["financial_goal"], "SAVE_MONEY")
        # Check budget recommendations are curated for SAVE_MONEY
        budget_res = client.get("/api/budget")
        self.assertEqual(budget_res.status_code, 200)
        budget = budget_res.json()
        self.assertEqual(budget["goal"], "SAVE_MONEY")
        # Verify recommended allocation reflects SAVE_MONEY (30% savings)
        self.assertEqual(budget["rule_50_30_20"]["savings"]["ideal_pct"], 30)

        # Test switching to INCREASE_MONEY
        res_inc = client.post("/api/profile/goal", json={"financial_goal": "INCREASE_MONEY"})
        self.assertEqual(res_inc.status_code, 200)
        self.assertEqual(res_inc.json()["financial_goal"], "INCREASE_MONEY")

    def test_ml_categorizer(self):
        res1 = categorizer.predict("Swiggy Koramangala Bangalore delivery")
        self.assertEqual(res1["category"], "Food & Dining")

        res2 = categorizer.predict("Netflix India monthly plan")
        self.assertEqual(res2["category"], "Subscriptions & Digital")

    def test_ml_savings_forecaster(self):
        forecast = forecaster.forecast(store.get_monthly_history(), horizon_months=6)
        self.assertIn("projections", forecast)
        self.assertEqual(len(forecast["projections"]), 6)

    def test_spending_anomaly_detector(self):
        normal_tx = {
            "id": "test_normal",
            "amount": 450.0,
            "category": "Food & Dining",
            "merchant": "Swiggy Cafe",
            "date": "2026-09-29T12:00:00Z"
        }
        res_normal = anomaly_detector.analyze_transaction(normal_tx)
        self.assertFalse(res_normal["is_anomaly"])

    def test_sip_calculator_inr(self):
        payload = {
            "monthly_investment": 15000.0,
            "annual_return_pct": 15.0,
            "years": 10,
            "step_up_pct": 10.0
        }
        response = client.post("/api/calculator/sip", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(data["total_invested"], 0)
        self.assertGreater(data["total_value"], data["total_invested"])

if __name__ == "__main__":
    unittest.main()
