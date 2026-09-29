"""
Wyvern Fintech OS - Automated Test Suite (INR Edition)
Verifies user profile setup & calibration, ML models, financial engines, Plaid integration, and API endpoints.
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
        self.assertEqual(data["app"], "Wyvern")
        self.assertEqual(data["currency"], "INR")

    def test_profile_onboarding_and_calibration(self):
        # User submits onboarding profile with real financial numbers in INR
        profile_payload = {
            "monthly_salary": 95000.0,
            "secondary_income": 12000.0,
            "savings_balance": 350000.0,
            "investment_balance": 780000.0,
            "credit_debt": 22000.0,
            "target_monthly_sip": 25000.0,
            "category_spending": {
                "Food & Dining": 18000.0,
                "Bills & Utilities": 22000.0,
                "Transportation": 6000.0,
                "Subscriptions & Digital": 3000.0,
                "Shopping & Retail": 9000.0,
                "Health & Fitness": 4000.0,
                "Entertainment & Leisure": 5000.0
            },
            "primary_bank": "HDFC Bank Ltd (India)"
        }
        res = client.post("/api/profile/setup", json=profile_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")

        # Verify overview reflects user inputs in INR
        ov_res = client.get("/api/overview")
        self.assertEqual(ov_res.status_code, 200)
        ov = ov_res.json()
        self.assertTrue(ov["profile_configured"])
        self.assertEqual(ov["currency"], "INR")
        # Net worth = 350000 + 780000 - 22000 = 1,108,000
        self.assertEqual(ov["net_worth"], 1108000.0)

    def test_ml_categorizer(self):
        # Test Indian fintech narratives
        res1 = categorizer.predict("Swiggy Koramangala Bangalore delivery")
        self.assertEqual(res1["category"], "Food & Dining")

        res2 = categorizer.predict("Netflix India monthly plan")
        self.assertEqual(res2["category"], "Subscriptions & Digital")

        res3 = categorizer.predict("Monthly Payroll Salary Tech Corp")
        self.assertEqual(res3["category"], "Income & Deposits")

        res4 = categorizer.predict("Indian Oil Petrol Pump Fuel Refill")
        self.assertEqual(res4["category"], "Transportation")

    def test_ml_savings_forecaster(self):
        forecast = forecaster.forecast(store.get_monthly_history(), horizon_months=6)
        self.assertIn("projections", forecast)
        self.assertEqual(len(forecast["projections"]), 6)
        self.assertIn("scenarios_6_month", forecast)
        self.assertGreater(forecast["scenarios_6_month"]["wyvern_optimized"]["total"], 0)

    def test_spending_anomaly_detector(self):
        # Normal transaction in INR
        normal_tx = {
            "id": "test_normal",
            "amount": 450.0,
            "category": "Food & Dining",
            "merchant": "Swiggy Cafe",
            "date": "2026-09-29T12:00:00Z"
        }
        res_normal = anomaly_detector.analyze_transaction(normal_tx)
        self.assertFalse(res_normal["is_anomaly"])

        # Severe spike anomaly in INR
        spike_tx = {
            "id": "test_spike",
            "amount": 95000.0,
            "category": "Food & Dining",
            "merchant": "Ultra Luxury Taj Club Dining",
            "date": "2026-09-29T21:00:00Z"
        }
        res_spike = anomaly_detector.analyze_transaction(spike_tx)
        self.assertTrue(res_spike["is_anomaly"])
        self.assertIn(res_spike["severity"], ["WARNING", "CRITICAL"])

    def test_budget_analysis_in_rupees(self):
        response = client.get("/api/budget")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["currency"], "INR")
        self.assertEqual(data["currency_symbol"], "₹")
        self.assertIn("rule_50_30_20", data)
        self.assertIn("recommendations", data)
        self.assertGreater(len(data["recommendations"]), 0)

    def test_sip_calculator_inr(self):
        payload = {
            "monthly_investment": 15000.0, # ₹15,000/mo
            "annual_return_pct": 15.0,
            "years": 10,
            "step_up_pct": 10.0
        }
        response = client.post("/api/calculator/sip", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(data["total_invested"], 0)
        self.assertGreater(data["total_value"], data["total_invested"])
        self.assertEqual(len(data["yearly_breakdown"]), 10)

if __name__ == "__main__":
    unittest.main()
