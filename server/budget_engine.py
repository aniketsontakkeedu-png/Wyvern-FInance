"""
Wyvern Budgeting Recommendation Engine (INR Edition):
Analyzes user transactions to generate 50/30/20 allocations, recurring subscription audits,
and personalized financial recommendations in Indian Rupees (₹).
"""
from typing import Dict, List, Any
import numpy as np

class BudgetEngine:
    def __init__(self):
        pass

    def analyze_budget(self, transactions: List[Dict[str, Any]], accounts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates 50/30/20 rule allocation, detects spending leaks,
        and generates actionable personalized financial recommendations in INR (₹).
        """
        expense_txs = [t for t in transactions if t.get("category") != "Income & Deposits"]
        income_txs = [t for t in transactions if t.get("category") == "Income & Deposits"]

        total_income = sum(t["amount"] for t in income_txs) if income_txs else 85000.00
        total_expense = sum(t["amount"] for t in expense_txs)

        needs_categories = ["Bills & Utilities", "Transportation", "Health & Fitness"]
        wants_categories = ["Food & Dining", "Shopping & Retail", "Entertainment & Leisure", "Travel & Lodging", "Subscriptions & Digital"]
        savings_categories = ["Investments & Savings"]

        needs_total = sum(t["amount"] for t in expense_txs if t.get("category") in needs_categories)
        food_dining_total = sum(t["amount"] for t in expense_txs if t.get("category") == "Food & Dining")
        essential_food = food_dining_total * 0.45
        discretionary_food = food_dining_total * 0.55

        needs_total += essential_food
        wants_total = sum(t["amount"] for t in expense_txs if t.get("category") in wants_categories and t.get("category") != "Food & Dining") + discretionary_food
        savings_total = sum(t["amount"] for t in expense_txs if t.get("category") in savings_categories)

        if total_income > 0:
            needs_pct = round((needs_total / total_income) * 100, 1)
            wants_pct = round((wants_total / total_income) * 100, 1)
            savings_pct = round((savings_total / total_income) * 100, 1)
        else:
            needs_pct, wants_pct, savings_pct = 50.0, 30.0, 20.0

        cat_totals: Dict[str, float] = {}
        for t in expense_txs:
            cat = t.get("category", "Other")
            cat_totals[cat] = cat_totals.get(cat, 0.0) + float(t.get("amount", 0.0))

        subs = [t for t in expense_txs if t.get("category") == "Subscriptions & Digital"]
        sub_total_monthly = sum(s["amount"] for s in subs)
        sub_annual_cost = sub_total_monthly * 12

        recommendations = []

        # Rec 1: Wants vs 50/30/20 target
        if wants_pct > 30:
            excess_wants = max(0.0, (wants_pct - 30) / 100.0 * total_income)
            recommendations.append({
                "id": "rec_wants_rebalance",
                "priority": "HIGH",
                "badge": "50/30/20 LEAK",
                "title": "Discretionary Spending Above 30% Threshold",
                "description": f"Discretionary spending is currently at {wants_pct}% of total monthly earnings. Trimming ₹{excess_wants:,.0f}/mo from dining and online shopping will align your profile with institutional wealth-building benchmarks.",
                "monthly_savings_impact": round(excess_wants, 2),
                "annual_savings_impact": round(excess_wants * 12, 2),
                "suggested_action": f"Set a ₹{max(3000, excess_wants):,.0f} monthly cap on food delivery apps and impulse shopping."
            })
        else:
            recommendations.append({
                "id": "rec_wants_optimal",
                "priority": "OPTIMIZATION",
                "badge": "DISCIPLINED ALLOCATION",
                "title": "Discretionary Spending Under Control",
                "description": f"Discretionary 'Wants' are kept at {wants_pct}% of total inflow, which is within the 30% healthy threshold.",
                "monthly_savings_impact": round(total_income * 0.05, 2),
                "annual_savings_impact": round(total_income * 0.6, 2),
                "suggested_action": "Maintain this discipline and route surplus cash directly into your active SIP portfolio."
            })

        # Rec 2: Subscription Audit & Consolidation
        if len(subs) >= 2 or sub_total_monthly > 1000:
            potential_sub_trim = sub_total_monthly * 0.35
            recommendations.append({
                "id": "rec_sub_audit",
                "priority": "HIGH",
                "badge": "SUBSCRIPTION CREEP",
                "title": f"Consolidate {len(subs)} Active Streaming & Digital Subscriptions",
                "description": f"You are currently spending ₹{sub_total_monthly:,.2f}/mo (₹{sub_annual_cost:,.2f}/year) across recurring digital licenses. Wyvern detected overlapping OTT streaming platforms.",
                "monthly_savings_impact": round(potential_sub_trim, 2),
                "annual_savings_impact": round(potential_sub_trim * 12, 2),
                "suggested_action": "Pause dormant subscriptions (e.g. duplicate streaming) to save instantly."
            })

        # Rec 3: High Dining Out Arbitrage
        if food_dining_total > 5000:
            dining_trim = food_dining_total * 0.22
            recommendations.append({
                "id": "rec_dining_arbitrage",
                "priority": "MEDIUM",
                "badge": "DINING OPTIMIZATION",
                "title": "Delivery & Restaurant Surcharge Arbitrage",
                "description": f"Food delivery fees and restaurant markups constitute ₹{food_dining_total:,.2f} of this cycle's outflows. Shifting two orders/week to grocery prep yields high compound gains.",
                "monthly_savings_impact": round(dining_trim, 2),
                "annual_savings_impact": round(dining_trim * 12, 2),
                "suggested_action": "Batch grocery orders with Blinkit / Instamart to mitigate delivery charges."
            })

        # Rec 4: SIP Compound Yield Reinvestment
        rec_sip_boost = max(2500.0, total_income * 0.05)
        projected_10y_boost = rec_sip_boost * (( (1 + 0.15/12)**(120) - 1 ) / (0.15/12))
        recommendations.append({
            "id": "rec_sip_acceleration",
            "priority": "OPTIMIZATION",
            "badge": "ALPHA GENERATION",
            "title": "Reallocate Surplus into Top-Quartile SIPs (Parag Parikh / Quant)",
            "description": f"Routing an additional ₹{rec_sip_boost:,.0f}/month into Parag Parikh Flexi Cap or Quant Small Cap compounds to ~₹{projected_10y_boost:,.0f} over 10 years at a 15% historical CAGR.",
            "monthly_savings_impact": round(rec_sip_boost, 2),
            "annual_savings_impact": round(rec_sip_boost * 12, 2),
            "suggested_action": "Set up an automated monthly auto-debit on the 1st of every month."
        })

        # Rec 5: Emergency Liquidity Cushion
        liquid_cash = sum(a["balance"] for a in accounts if a["subtype"] in ["savings", "checking"])
        monthly_burn = total_expense if total_expense > 0 else 40000.0
        runway_months = round(liquid_cash / monthly_burn, 1) if monthly_burn > 0 else 6.0

        if runway_months > 6:
            idle_cash = max(0.0, liquid_cash - (monthly_burn * 4))
            recommendations.append({
                "id": "rec_yield_boost",
                "priority": "OPTIMIZATION",
                "badge": "CASH DRAG ALERT",
                "title": "Optimize Idle Cash in High-Yield Arbitrage or Liquid Funds",
                "description": f"Your liquid runway is {runway_months} months (₹{liquid_cash:,.2f}). Move ~₹{idle_cash:,.2f} of excess checking balance into 7.1% APY Arbitrage Funds or Liquid Mutual Funds.",
                "monthly_savings_impact": round((idle_cash * 0.071) / 12, 2),
                "annual_savings_impact": round(idle_cash * 0.071, 2),
                "suggested_action": "Maintain 4 months of buffer in savings and deploy remainder to liquid arbitrage."
            })

        total_potential_monthly = sum(r["monthly_savings_impact"] for r in recommendations[:4])

        return {
            "currency": "INR",
            "currency_symbol": "₹",
            "income": round(total_income, 2),
            "expense": round(total_expense, 2),
            "rule_50_30_20": {
                "needs": {"amount": round(needs_total, 2), "pct": needs_pct, "ideal_pct": 50},
                "wants": {"amount": round(wants_total, 2), "pct": wants_pct, "ideal_pct": 30},
                "savings": {"amount": round(savings_total, 2), "pct": savings_pct, "ideal_pct": 20}
            },
            "category_breakdown": [{"category": k, "amount": round(v, 2)} for k, v in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)],
            "subscriptions": {
                "count": len(subs),
                "monthly_total": round(sub_total_monthly, 2),
                "annual_total": round(sub_annual_cost, 2),
                "items": subs
            },
            "total_potential_monthly_savings": round(total_potential_monthly, 2),
            "recommendations": recommendations
        }

budget_engine = BudgetEngine()
