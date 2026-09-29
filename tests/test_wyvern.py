"""
Wyvern Fintech OS - Automated Test Suite
Verifies all ML models, financial engines, Plaid integration, and API endpoints.
"""
import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add project root to sys.path
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

    def test_ml_categorizer(self):
        # Test distinct narratives
        res1 = categorizer.predict("Starbucks Pike Place Roast Coffee")
        self.assertEqual(res1["category"], "Food & Dining")
        self.assertGreater(res1["confidence"], 0.1)

        res2 = categorizer.predict("Netflix monthly streaming subscription")
        self.assertEqual(res2["category"], "Subscriptions & Digital")

        res3 = categorizer.predict("Direct Deposit Payroll Tech Corp Salary")
        self.assertEqual(res3["category"], "Income & Deposits")

        res4 = categorizer.predict("Shell Gas Fuel Station")
        self.assertEqual(res4["category"], "Transportation")

    def test_ml_savings_forecaster(self):
        forecast = forecaster.forecast(store.get_monthly_history(), horizon_months=6)
        self.assertIn("projections", forecast)
        self.assertEqual(len(forecast["projections"]), 6)
        self.assertIn("scenarios_6_month", forecast)
        self.assertGreater(forecast["scenarios_6_month"]["wyvern_optimized"]["total"], 0)
        # Check projection values
        first_proj = forecast["projections"][0]
        self.assertIn("projected_savings", first_proj)
        self.assertIn("lower_bound", first_proj)
        self.assertIn("upper_bound", first_proj)
        self.assertGreaterEqual(first_proj["upper_bound"], first_proj["lower_bound"])

    def test_spending_anomaly_detector(self):
        # Test normal transaction
        normal_tx = {
            "id": "test_normal",
            "amount": 25.0,
            "category": "Food & Dining",
            "merchant": "Chipotle",
            "date": "2026-09-29T12:00:00Z"
        }
        res_normal = anomaly_detector.analyze_transaction(normal_tx)
        self.assertFalse(res_normal["is_anomaly"])

        # Test massive spike anomaly
        spike_tx = {
            "id": "test_spike",
            "amount": 1450.0,
            "category": "Food & Dining",
            "merchant": "Ultra Luxury Caviar Bar",
            "date": "2026-09-29T21:00:00Z"
        }
        res_spike = anomaly_detector.analyze_transaction(spike_tx)
        self.assertTrue(res_spike["is_anomaly"])
        self.assertIn(res_spike["severity"], ["WARNING", "CRITICAL"])

    def test_overview_endpoint(self):
        response = client.get("/api/overview")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("net_worth", data)
        self.assertIn("rule_50_30_20", data)
        self.assertIn("forecast", data)
        self.assertIn("top_recommendations", data)

    def test_transactions_endpoints(self):
        # Get transactions
        get_res = client.get("/api/transactions?limit=10")
        self.assertEqual(get_res.status_code, 200)
        txs = get_res.json()
        self.assertIsInstance(txs, list)
        self.assertGreater(len(txs), 0)

        # Add new transaction
        new_payload = {
            "merchant": "Zomato Delivery Gurgaon",
            "amount": 34.50,
            "category": "Food & Dining"
        }
        post_res = client.post("/api/transactions", json=new_payload)
        self.assertEqual(post_res.status_code, 200)
        created = post_res.json()["transaction"]
        self.assertEqual(created["merchant"], "Zomato Delivery Gurgaon")
        self.assertIn("anomaly_analysis", created)

    def test_budget_analysis_endpoint(self):
        response = client.get("/api/budget")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("rule_50_30_20", data)
        self.assertIn("subscriptions", data)
        self.assertIn("recommendations", data)
        self.assertGreater(len(data["recommendations"]), 0)

    def test_market_indices(self):
        indices = market_service.get_indices()
        self.assertEqual(len(indices), 6)
        symbols = [i["symbol"] for i in indices]
        self.assertIn("^NSEI", symbols)
        self.assertIn("^GSPC", symbols)

    def test_market_india_and_global(self):
        # India
        ind_res = client.get("/api/market/india")
        self.assertEqual(ind_res.status_code, 200)
        ind_data = ind_res.json()
        self.assertEqual(ind_data["region"], "India")
        self.assertGreater(len(ind_data["sips"]), 0)
        self.assertGreater(len(ind_data["stocks"]), 0)

        # Global
        glb_res = client.get("/api/market/global")
        self.assertEqual(glb_res.status_code, 200)
        glb_data = glb_res.json()
        self.assertEqual(glb_data["region"], "Global")
        self.assertGreater(len(glb_data["sips"]), 0)
        self.assertGreater(len(glb_data["stocks"]), 0)

    def test_sip_calculator_endpoint(self):
        payload = {
            "monthly_investment": 10000.0,
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

    def test_plaid_endpoints(self):
        # Link token
        lt_res = client.post("/api/plaid/create-link-token")
        self.assertEqual(lt_res.status_code, 200)
        self.assertIn("link_token", lt_res.json())

        # Exchange token
        ex_res = client.post("/api/plaid/exchange-token", json={
            "public_token": "public-test-token",
            "institution_name": "HDFC Bank Ltd (India)"
        })
        self.assertEqual(ex_res.status_code, 200)
        self.assertEqual(ex_res.json()["status"], "connected")

        # Sync
        sync_res = client.post("/api/plaid/sync")
        self.assertEqual(sync_res.status_code, 200)
        self.assertEqual(sync_res.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
