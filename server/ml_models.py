"""
Wyvern ML Engine: Spending Categorization, Savings Forecasting & Spending Anomaly Detection
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.ensemble import IsolationForest
import logging

logger = logging.getLogger("wyvern.ml")

CATEGORIES = [
    "Food & Dining",
    "Shopping & Retail",
    "Transportation",
    "Subscriptions & Digital",
    "Bills & Utilities",
    "Health & Fitness",
    "Investments & Savings",
    "Entertainment & Leisure",
    "Income & Deposits",
    "Travel & Lodging"
]

# Rich training corpus covering both Global & Indian fintech transaction narratives
TRAINING_DATA = [
    # Food & Dining
    ("Starbucks Coffee Seattle", "Food & Dining"),
    ("Uber Eats order #8921", "Food & Dining"),
    ("Zomato Online Ordering Gurgaon", "Food & Dining"),
    ("Swiggy Delivery Koramangala Bangalore", "Food & Dining"),
    ("McDonald's Drive Thru 1421", "Food & Dining"),
    ("Chipotle Mexican Grill NYC", "Food & Dining"),
    ("Whole Foods Market Grocery", "Food & Dining"),
    ("Trader Joe's Brooklyn", "Food & Dining"),
    ("Blinkit Quick Commerce Delivery", "Food & Dining"),
    ("Instamart Swiggy Grocery", "Food & Dining"),
    ("Zepto 10 min groceries", "Food & Dining"),
    ("Subway Sandwiches SF", "Food & Dining"),
    ("Dominos Pizza Online", "Food & Dining"),
    ("Blue Tokai Coffee Roasters", "Food & Dining"),
    ("Haldiram Sweets and Restaurant", "Food & Dining"),
    ("Dunkin Donuts Breakfast", "Food & Dining"),
    ("Burger King Express", "Food & Dining"),
    ("Safeway Grocery Store", "Food & Dining"),
    ("KFC Fried Chicken", "Food & Dining"),
    ("Taco Bell Late Night", "Food & Dining"),
    ("Costa Coffee Airport Terminal", "Food & Dining"),
    ("Tim Hortons Cafe", "Food & Dining"),
    ("Local Bakery & Cafe Pastries", "Food & Dining"),
    ("Nature's Basket Organic Supermarket", "Food & Dining"),
    ("BigBasket Fresh Produce Online", "Food & Dining"),

    # Shopping & Retail
    ("Amazon.com Marketplace Purchase", "Shopping & Retail"),
    ("Amazon India Retail Private Ltd", "Shopping & Retail"),
    ("Flipkart Internet Pvt Ltd Bangalore", "Shopping & Retail"),
    ("Myntra Fashion Marketplace", "Shopping & Retail"),
    ("Nike Store Flagship", "Shopping & Retail"),
    ("Zara Clothing Mall", "Shopping & Retail"),
    ("Apple Store Soho iPhone purchase", "Shopping & Retail"),
    ("Target Store Minneapolis", "Shopping & Retail"),
    ("Walmart Supercenter Store", "Shopping & Retail"),
    ("Best Buy Electronics Store", "Shopping & Retail"),
    ("Uniqlo Casual Wear", "Shopping & Retail"),
    ("H&M Hennes & Mauritz", "Shopping & Retail"),
    ("Ajio Digital Reliance Retail", "Shopping & Retail"),
    ("Sephora Cosmetics & Fragrance", "Shopping & Retail"),
    ("IKEA Furniture Store Home", "Shopping & Retail"),
    ("Nykaa Beauty and Cosmetics", "Shopping & Retail"),
    ("Croma Electronics Tata Retail", "Shopping & Retail"),
    ("Decathlon Sports Gear", "Shopping & Retail"),
    ("Costco Wholesale Club", "Shopping & Retail"),
    ("Lululemon Athletica Pants", "Shopping & Retail"),

    # Transportation
    ("Uber Technologies Inc Ride", "Transportation"),
    ("Uber Trip Help.Uber.Com", "Transportation"),
    ("Ola Cabs Ride ANI Technologies", "Transportation"),
    ("Rapido Bike Taxi Booking", "Transportation"),
    ("Lyft Ride SF Downtown", "Transportation"),
    ("Shell Gas Station Fuel", "Transportation"),
    ("Chevron Fuel Dispenser", "Transportation"),
    ("Indian Oil Petrol Pump Fuel", "Transportation"),
    ("Bharat Petroleum Pump Refill", "Transportation"),
    ("MTA Subway Metro Card NY", "Transportation"),
    ("Delhi Metro Smart Card Recharge", "Transportation"),
    ("Bangalore Metro Namma Rail", "Transportation"),
    ("BART Transit Oakland Station", "Transportation"),
    ("FasTrak Bridge Toll CA", "Transportation"),
    ("FASTag Toll Plaza Highway Deduction", "Transportation"),
    ("Amtrak Train Rail Ticket", "Transportation"),
    ("IRCTC Train Ticket Booking Rail", "Transportation"),
    ("ParkMobile Street Parking Meter", "Transportation"),
    ("ExxonMobil Express Gas", "Transportation"),

    # Subscriptions & Digital
    ("Netflix.com Monthly Subscription", "Subscriptions & Digital"),
    ("Spotify Premium Family Plan", "Subscriptions & Digital"),
    ("Amazon Prime Annual Membership", "Subscriptions & Digital"),
    ("Apple iCloud 2TB Storage Plan", "Subscriptions & Digital"),
    ("Google One Storage Subscription", "Subscriptions & Digital"),
    ("YouTube Premium Family Plan", "Subscriptions & Digital"),
    ("OpenAI ChatGPT Plus Subscription", "Subscriptions & Digital"),
    ("GitHub Pro Subscription CoPilot", "Subscriptions & Digital"),
    ("Adobe Creative Cloud Monthly", "Subscriptions & Digital"),
    ("New York Times Digital Access", "Subscriptions & Digital"),
    ("Disney+ Hotstar Annual VIP", "Subscriptions & Digital"),
    ("Sony LIV Subscription Streaming", "Subscriptions & Digital"),
    ("Substack Newsletter Monthly", "Subscriptions & Digital"),
    ("Audible Books Membership", "Subscriptions & Digital"),
    ("Medium Member Yearly Subscription", "Subscriptions & Digital"),
    ("NordVPN 2 Year Protection Plan", "Subscriptions & Digital"),
    ("Dropbox Cloud Storage 1TB", "Subscriptions & Digital"),
    ("Slack Technologies Workspace Plan", "Subscriptions & Digital"),
    ("Notion Personal Plus Subscription", "Subscriptions & Digital"),

    # Bills & Utilities
    ("AT&T Mobility Wireless Monthly Bill", "Bills & Utilities"),
    ("Verizon Wireless Cell Phone Bill", "Bills & Utilities"),
    ("Airtel Postpaid Mobile Bill Payment", "Bills & Utilities"),
    ("Jio Infocomm Prepaid 84 Days Plan", "Bills & Utilities"),
    ("Vodafone Idea Vi Monthly Recharge", "Bills & Utilities"),
    ("ConEdison Electricity & Gas NYC", "Bills & Utilities"),
    ("PG&E Utility Bill California", "Bills & Utilities"),
    ("Tata Power Electricity Bill", "Bills & Utilities"),
    ("BESCOM Power Electric Utility Bangalore", "Bills & Utilities"),
    ("City Water and Sewage Utility Dept", "Bills & Utilities"),
    ("Comcast Xfinity Home Internet Bill", "Bills & Utilities"),
    ("Act Fibernet Broadband Monthly", "Bills & Utilities"),
    ("Spectra High Speed Fiber Internet", "Bills & Utilities"),
    ("Mahanagar Gas PNG Piped Supply", "Bills & Utilities"),
    ("Waste Management Residential Trash", "Bills & Utilities"),
    ("State Farm Home Insurance Premium", "Bills & Utilities"),

    # Health & Fitness
    ("CVS Pharmacy Prescription Pills", "Health & Fitness"),
    ("Walgreens Pharmacy Drugstore", "Health & Fitness"),
    ("Apollo Pharmacy Medicines Bangalore", "Health & Fitness"),
    ("1mg Tata Digital Healthcare Medicines", "Health & Fitness"),
    ("Equinox Fitness Club Membership Gym", "Health & Fitness"),
    ("Cult.fit Gym & Fitness Membership", "Health & Fitness"),
    ("Planet Fitness Monthly Dues", "Health & Fitness"),
    ("Gold's Gym Annual Workout Access", "Health & Fitness"),
    ("Quest Diagnostics Lab Blood Test", "Health & Fitness"),
    ("Dental Care Clinic Teeth Cleaning", "Health & Fitness"),
    ("Kaiser Permanente Medical Copay", "Health & Fitness"),
    ("Max Healthcare Specialist Consultation", "Health & Fitness"),
    ("Optometry Vision Eye Exam Contacts", "Health & Fitness"),

    # Investments & Savings
    ("Zerodha Broking Ltd Coin SIP Funds", "Investments & Savings"),
    ("Groww Investment Nextbillion Tech", "Investments & Savings"),
    ("Vanguard Index Funds Automatic Deposit", "Investments & Savings"),
    ("Fidelity Brokerage Individual Transfer", "Investments & Savings"),
    ("Charles Schwab Roth IRA Contribution", "Investments & Savings"),
    ("Robinhood Financial Instant Deposit", "Investments & Savings"),
    ("Coinbase Crypto Bitcoin Purchase", "Investments & Savings"),
    ("Kuvera Mutual Fund Direct SIP", "Investments & Savings"),
    ("Upstox Securities Trading Margin", "Investments & Savings"),
    ("TreasuryDirect US Govt T-Bills", "Investments & Savings"),
    ("National Pension System NPS Contribution", "Investments & Savings"),
    ("Public Provident Fund PPF Deposit Bank", "Investments & Savings"),
    ("INDmoney US Stocks Trading Account", "Investments & Savings"),
    ("Webull Financial Securities Deposit", "Investments & Savings"),

    # Entertainment & Leisure
    ("AMC Theatres Movie Cinema Popcorn", "Entertainment & Leisure"),
    ("PVR INOX Multiplex Cinemas Tickets", "Entertainment & Leisure"),
    ("BookMyShow Movie & Concert Tickets", "Entertainment & Leisure"),
    ("PlayStation Network PS Store Game", "Entertainment & Leisure"),
    ("Steam Valve Video Games Purchase", "Entertainment & Leisure"),
    ("Nintendo eShop Switch Game Download", "Entertainment & Leisure"),
    ("Ticketmaster Live Music Concert Tour", "Entertainment & Leisure"),
    ("Dave & Buster's Arcade Games & Drinks", "Entertainment & Leisure"),
    ("Topgolf Entertainment Driving Range", "Entertainment & Leisure"),
    ("Bowlero Bowling Lanes Fun", "Entertainment & Leisure"),

    # Income & Deposits
    ("Direct Deposit Payroll Tech Corp Salary", "Income & Deposits"),
    ("Infosys Limited Monthly Payroll Salary", "Income & Deposits"),
    ("Google LLC Monthly Compensation Salary", "Income & Deposits"),
    ("Stripe Payments Payout Seller Proceeds", "Income & Deposits"),
    ("PayPal Transfer Bank Account Payout", "Income & Deposits"),
    ("Upwork Global Freelance Earnings Payout", "Income & Deposits"),
    ("Dividend Credit Vanguard VOO Index", "Income & Deposits"),
    ("Interest Earned High Yield Savings Account", "Income & Deposits"),
    ("Client Wire Transfer Consulting Fee", "Income & Deposits"),
    ("State Tax Refund Direct Deposit", "Income & Deposits"),

    # Travel & Lodging
    ("Airbnb Booking Downtown Apartment Stay", "Travel & Lodging"),
    ("Marriott Hotels & Resorts Lodging", "Travel & Lodging"),
    ("Hilton Worldwide Reservation Hotel", "Travel & Lodging"),
    ("Delta Air Lines Flight Ticket NY-SFO", "Travel & Lodging"),
    ("United Airlines Flight Booking", "Travel & Lodging"),
    ("IndiGo Airlines Flight Domestic Travel", "Travel & Lodging"),
    ("MakeMyTrip Flight & Hotel Package", "Travel & Lodging"),
    ("Expedia Travel Flight Hotel Car", "Travel & Lodging"),
    ("Booking.com Worldwide Hotel Room", "Travel & Lodging"),
    ("Enterprise Rent-A-Car Rental Vehicle", "Travel & Lodging")
]

class SpendingCategorizer:
    """ML Model for transaction categorization using TF-IDF + Logistic Regression with confidence scoring."""
    def __init__(self):
        self.model = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
            ("clf", LogisticRegression(C=1.5, max_iter=500, class_weight="balanced"))
        ])
        self.is_trained = False
        self._train()

    def _train(self):
        texts, labels = zip(*TRAINING_DATA)
        self.model.fit(texts, labels)
        self.is_trained = True

    def predict(self, description: str) -> Dict[str, Any]:
        if not self.is_trained:
            self._train()

        # Handle empty/short description
        if not description or not description.strip():
            return {
                "category": "Shopping & Retail",
                "confidence": 0.5,
                "probabilities": {}
            }

        probs = self.model.predict_proba([description])[0]
        classes = self.model.classes_

        top_idx = np.argmax(probs)
        top_cat = str(classes[top_idx])
        confidence = float(probs[top_idx])

        # Return top 4 probabilities
        prob_dict = {str(classes[i]): round(float(probs[i]), 3) for i in np.argsort(probs)[::-1][:4]}

        return {
            "category": top_cat,
            "confidence": round(confidence, 3),
            "probabilities": prob_dict
        }

    def batch_categorize(self, descriptions: List[str]) -> List[Dict[str, Any]]:
        return [self.predict(desc) for desc in descriptions]


class SavingsForecaster:
    """
    ML-driven monthly savings forecaster.
    Analyzes historical monthly earnings, baseline living costs, discretionary spending,
    and projects savings for future months with confidence bounds and scenario simulations.
    """
    def __init__(self):
        pass

    def forecast(self, monthly_history: List[Dict[str, float]], horizon_months: int = 6) -> Dict[str, Any]:
        """
        Takes list of monthly dicts: [{'month': '2026-03', 'income': 6500, 'spending': 4200, 'savings': 2300}, ...]
        Returns projected savings for upcoming months, savings rate trends, and scenario analyses.
        """
        if not monthly_history or len(monthly_history) < 2:
            return self._default_forecast(horizon_months)

        df = pd.DataFrame(monthly_history)
        if "savings" not in df.columns:
            df["savings"] = df["income"] - df["spending"]

        # Feature matrix: time step
        n = len(df)
        X = np.arange(n).reshape(-1, 1)
        y_savings = df["savings"].values
        y_spending = df["spending"].values
        y_income = df["income"].values

        # Linear + Momentum trend fit
        from sklearn.linear_model import Ridge
        ridge_savings = Ridge(alpha=1.0)
        ridge_savings.fit(X, y_savings)

        ridge_spending = Ridge(alpha=1.0)
        ridge_spending.fit(X, y_spending)

        ridge_income = Ridge(alpha=1.0)
        ridge_income.fit(X, y_income)

        # Future time steps
        future_X = np.arange(n, n + horizon_months).reshape(-1, 1)
        pred_savings = ridge_savings.predict(future_X)
        pred_spending = ridge_spending.predict(future_X)
        pred_income = ridge_income.predict(future_X)

        # Standard deviation of residuals for confidence intervals
        residuals = y_savings - ridge_savings.predict(X)
        std_err = np.std(residuals) if len(residuals) > 1 else 250.0

        # Build month labels
        last_month_str = monthly_history[-1]["month"]
        try:
            last_date = datetime.strptime(last_month_str, "%Y-%m")
        except:
            last_date = datetime.now()

        projections = []
        cumulative_savings = 0.0

        for i in range(horizon_months):
            next_date = last_date + timedelta(days=32 * (i + 1))
            m_label = next_date.strftime("%b %Y")

            base_val = max(0.0, float(pred_savings[i]))
            p10 = max(0.0, float(base_val - 1.28 * std_err))  # 80% CI lower
            p90 = float(base_val + 1.28 * std_err)            # 80% CI upper
            inc = float(pred_income[i])
            sp = float(pred_spending[i])
            savings_rate = round((base_val / inc * 100.0) if inc > 0 else 0, 1)

            cumulative_savings += base_val

            projections.append({
                "month": m_label,
                "projected_savings": round(base_val, 2),
                "lower_bound": round(p10, 2),
                "upper_bound": round(p90, 2),
                "projected_income": round(inc, 2),
                "projected_spending": round(sp, 2),
                "savings_rate_pct": savings_rate,
                "cumulative_projected": round(cumulative_savings, 2)
            })

        avg_current_savings = float(np.mean(y_savings[-3:]))
        avg_current_spending = float(np.mean(y_spending[-3:]))
        avg_current_income = float(np.mean(y_income[-3:]))

        conservative_savings_6m = sum([p["projected_savings"] * 0.82 for p in projections])
        baseline_savings_6m = sum([p["projected_savings"] for p in projections])
        optimized_savings_6m = sum([p["projected_savings"] * 1.24 for p in projections])

        current_savings_rate = round((avg_current_savings / avg_current_income * 100.0) if avg_current_income > 0 else 0, 1)

        assumed_liquid_reserves = 28500.0
        runway_months = round(assumed_liquid_reserves / avg_current_spending, 1) if avg_current_spending > 0 else 12.0

        return {
            "current_monthly_avg_savings": round(avg_current_savings, 2),
            "current_monthly_avg_spending": round(avg_current_spending, 2),
            "current_savings_rate_pct": current_savings_rate,
            "emergency_runway_months": runway_months,
            "projections": projections,
            "scenarios_6_month": {
                "conservative": {
                    "total": round(conservative_savings_6m, 2),
                    "label": "Inflation / Unplanned Outflows (-18%)",
                    "monthly_avg": round(conservative_savings_6m / horizon_months, 2)
                },
                "baseline": {
                    "total": round(baseline_savings_6m, 2),
                    "label": "Current Velocity Trajectory",
                    "monthly_avg": round(baseline_savings_6m / horizon_months, 2)
                },
                "wyvern_optimized": {
                    "total": round(optimized_savings_6m, 2),
                    "label": "Wyvern AI Budget Rebalancing (+24%)",
                    "monthly_avg": round(optimized_savings_6m / horizon_months, 2),
                    "extra_accumulated": round(optimized_savings_6m - baseline_savings_6m, 2)
                }
            }
        }

    def _default_forecast(self, horizon: int) -> Dict[str, Any]:
        base_income = 5800.0
        base_spending = 3650.0
        base_savings = base_income - base_spending
        projections = []
        cum = 0.0
        now = datetime.now()
        for i in range(horizon):
            m_date = now + timedelta(days=30 * (i + 1))
            s_val = base_savings + (i * 45.0)
            cum += s_val
            projections.append({
                "month": m_date.strftime("%b %Y"),
                "projected_savings": round(s_val, 2),
                "lower_bound": round(s_val * 0.85, 2),
                "upper_bound": round(s_val * 1.15, 2),
                "projected_income": round(base_income + (i * 20), 2),
                "projected_spending": round(base_spending - (i * 25), 2),
                "savings_rate_pct": round((s_val / base_income) * 100, 1),
                "cumulative_projected": round(cum, 2)
            })

        return {
            "current_monthly_avg_savings": round(base_savings, 2),
            "current_monthly_avg_spending": round(base_spending, 2),
            "current_savings_rate_pct": round((base_savings / base_income) * 100, 1),
            "emergency_runway_months": 7.8,
            "projections": projections,
            "scenarios_6_month": {
                "conservative": {"total": round(cum * 0.82, 2), "label": "Conservative (-18%)", "monthly_avg": round(cum * 0.82 / horizon, 2)},
                "baseline": {"total": round(cum, 2), "label": "Baseline", "monthly_avg": round(cum / horizon, 2)},
                "wyvern_optimized": {"total": round(cum * 1.24, 2), "label": "Wyvern Optimized (+24%)", "monthly_avg": round(cum * 1.24 / horizon, 2), "extra_accumulated": round(cum * 0.24, 2)}
            }
        }


class AnomalyDetector:
    """
    ML Anomaly Detection combining:
    1. Isolation Forest on numeric feature vectors (Amount, Hour, Category index)
    2. Category-Specific Robust Statistics (MAD - Median Absolute Deviation & IQR)
    3. Heuristic Rules (rapid duplicate triggers, sudden subscription price surge)
    """
    def __init__(self):
        self.iso_forest = IsolationForest(n_estimators=100, contamination=0.08, random_state=42)
        self.category_baselines = {}
        self.is_fitted = False

    def fit(self, transactions: List[Dict[str, Any]]):
        if not transactions or len(transactions) < 10:
            return

        df = pd.DataFrame(transactions)
        for cat, group in df.groupby("category"):
            amounts = group["amount"].values
            median = float(np.median(amounts))
            mad = float(np.median(np.abs(amounts - median)))
            if mad == 0:
                mad = float(np.std(amounts)) if len(amounts) > 1 else 10.0
            p95 = float(np.percentile(amounts, 95)) if len(amounts) >= 5 else median * 2.5
            self.category_baselines[cat] = {
                "median": median,
                "mad": max(mad, 5.0),
                "p95": p95,
                "count": len(amounts)
            }

        feature_matrix = []
        for t in transactions:
            amt = float(t.get("amount", 0))
            hour = 12
            if "date" in t:
                try:
                    dt = datetime.fromisoformat(t["date"].replace("Z", ""))
                    hour = dt.hour
                except:
                    pass
            cat_idx = CATEGORIES.index(t.get("category", "Shopping & Retail")) if t.get("category") in CATEGORIES else 0
            feature_matrix.append([amt, hour, cat_idx])

        if len(feature_matrix) >= 10:
            self.iso_forest.fit(np.array(feature_matrix))
            self.is_fitted = True

    def analyze_transaction(self, tx: Dict[str, Any], recent_transactions: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        amount = float(tx.get("amount", 0))
        category = tx.get("category", "Shopping & Retail")
        merchant = tx.get("merchant", tx.get("name", "Unknown"))
        date_str = tx.get("date", "")

        is_anomaly = False
        reasons = []
        severity = "NORMAL"
        anomaly_score = 0.0

        baseline = self.category_baselines.get(category, {"median": 45.0, "mad": 25.0, "p95": 180.0})
        median = baseline["median"]
        mad = baseline["mad"]
        p95 = baseline["p95"]

        mod_z = 0.6745 * (amount - median) / (mad if mad > 0 else 1.0)

        if mod_z > 3.5:
            is_anomaly = True
            severity = "CRITICAL" if mod_z > 6.0 else "WARNING"
            diff_pct = int(((amount - median) / median) * 100) if median > 0 else 200
            reasons.append(f"Unusual spend spike: {amount:,.2f} is +{diff_pct}% above your typical {category} median of {median:,.2f}")
            anomaly_score = min(98.0, 45.0 + (mod_z * 8.0))
        elif amount > p95 and amount > 150:
            is_anomaly = True
            severity = "WARNING"
            reasons.append(f"Exceeds 95th percentile spend tier for {category}")
            anomaly_score = max(anomaly_score, 65.0)

        # Check for rapid duplicate charges (within 10 minutes)
        if recent_transactions and date_str:
            try:
                curr_dt = datetime.fromisoformat(date_str.replace("Z", ""))
                for past in recent_transactions[-10:]:
                    if past.get("id") == tx.get("id"):
                        continue
                    p_dt = datetime.fromisoformat(past.get("date", "").replace("Z", ""))
                    if abs((curr_dt - p_dt).total_seconds()) < 600 and abs(float(past.get("amount", 0)) - amount) < 0.01:
                        is_anomaly = True
                        severity = "CRITICAL"
                        reasons.append(f"Potential duplicate charge: identical amount {amount:,.2f} detected within 10 minutes of previous transaction")
                        anomaly_score = 95.0
                        break
            except Exception:
                pass

        if category == "Subscriptions & Digital" and amount > 60.0:
            is_anomaly = True
            if severity != "CRITICAL":
                severity = "WARNING"
            reasons.append(f"Subscription alert: High recurring charge ({amount:,.2f}) detected for digital services")
            anomaly_score = max(anomaly_score, 72.0)

        if self.is_fitted and not is_anomaly:
            cat_idx = CATEGORIES.index(category) if category in CATEGORIES else 0
            hour = 12
            try:
                if date_str:
                    hour = datetime.fromisoformat(date_str.replace("Z", "")).hour
            except:
                pass

            iso_pred = self.iso_forest.predict([[amount, hour, cat_idx]])[0]
            if iso_pred == -1:
                is_anomaly = True
                severity = "INFO"
                reasons.append("Unusual multidimensional feature pattern flagged by ML Isolation Forest")
                anomaly_score = max(anomaly_score, 58.0)

        action = "None required"
        if severity == "CRITICAL":
            action = "Review immediately with card issuer or merchant to verify transaction legitimacy."
        elif severity == "WARNING":
            action = "Reallocate discretionary budget ceiling or flag if unexpected charge."
        elif severity == "INFO":
            action = "Monitored automatically by Wyvern. No immediate action needed."

        return {
            "is_anomaly": is_anomaly,
            "severity": severity,
            "anomaly_score": round(anomaly_score, 1),
            "reasons": reasons if reasons else ["Spending aligned with baseline historical patterns."],
            "suggested_action": action
        }

    def detect_all(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.is_fitted:
            self.fit(transactions)

        results = []
        for i, tx in enumerate(transactions):
            recent = transactions[max(0, i-5):i]
            diag = self.analyze_transaction(tx, recent)
            results.append({
                **tx,
                "anomaly_analysis": diag
            })
        return results

# Singleton instances
categorizer = SpendingCategorizer()
forecaster = SavingsForecaster()
anomaly_detector = AnomalyDetector()
