"""
Wyvern Budgeting Recommendation Engine (Goal-Curated Edition):
Dynamically curates recommendations, 50/30/20 benchmarks, and financial strategy based on user's goal:
- GROW_WEALTH: Long-term wealth compounding, step-up SIPs, and index hedges
- INCREASE_MONEY: High-alpha momentum equities, secondary income velocity, and aggressive capital growth
- SAVE_MONEY: Aggressive expense trimming, subscription elimination, and 12-month emergency runway
"""
from typing import Dict, List, Any
import numpy as np

class BudgetEngine:
    def __init__(self):
        pass

    def analyze_budget(self, transactions: List[Dict[str, Any]], accounts: List[Dict[str, Any]], goal: str = "GROW_WEALTH") -> Dict[str, Any]:
        """
        Calculates 50/30/20 allocation and curates recommendations tailored specifically to the user's money goal.
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

        # Ideal benchmark targets based on user's mission
        if goal == "SAVE_MONEY":
            ideal_needs, ideal_wants, ideal_savings = 50, 20, 30
        elif goal == "INCREASE_MONEY":
            ideal_needs, ideal_wants, ideal_savings = 45, 25, 30
        else: # GROW_WEALTH
            ideal_needs, ideal_wants, ideal_savings = 50, 30, 20

        # Curated recommendations based on money goal
        recommendations = []

        if goal == "SAVE_MONEY":
            # Mission: Save Money
            trim_amt = max(3500.0, wants_total * 0.3)
            recommendations.append({
                "id": "rec_save_discretionary",
                "priority": "HIGH",
                "badge": "GOAL: SAVE MONEY",
                "title": "Aggressive Discretionary Spending Lockdown",
                "description": f"To optimize capital preservation, trim discretionary outflows from {wants_pct}% down to {ideal_wants}%. Trimming ₹{trim_amt:,.0f}/month across dining and impulse shopping accelerates liquid reserves.",
                "monthly_savings_impact": round(trim_amt, 2),
                "annual_savings_impact": round(trim_amt * 12, 2),
                "suggested_action": f"Impose a strict weekly discretionary debit ceiling of ₹{round(trim_amt / 4, 0):,}."
            })

            sub_cut = sub_total_monthly * 0.6
            recommendations.append({
                "id": "rec_save_subscriptions",
                "priority": "HIGH",
                "badge": "SUBSCRIPTION PURGE",
                "title": "Purge Underutilized Digital Subscriptions",
                "description": f"You are carrying ₹{sub_total_monthly:,.2f}/mo (₹{sub_annual_cost:,.2f}/year) across recurring streaming and SaaS plans. Pausing non-essential OTT services saves ₹{sub_cut:,.0f}/mo immediately.",
                "monthly_savings_impact": round(sub_cut, 2),
                "annual_savings_impact": round(sub_cut * 12, 2),
                "suggested_action": "Cancel overlapping OTT video and music streaming plans."
            })

            liquid_cash = sum(a["balance"] for a in accounts if a["subtype"] in ["savings", "checking"])
            recommendations.append({
                "id": "rec_save_runway",
                "priority": "OPTIMIZATION",
                "badge": "12-MO RUNWAY",
                "title": "Park Liquid Reserves into 7.1% Arbitrage / Liquid Funds",
                "description": f"Move idle bank balance (₹{liquid_cash:,.0f}) from low-yield 3% savings into 7.1% tax-efficient Arbitrage funds while securing a 12-month emergency cushion.",
                "monthly_savings_impact": round((liquid_cash * 0.041) / 12, 2),
                "annual_savings_impact": round(liquid_cash * 0.041, 2),
                "suggested_action": "Retain 3 months in checking; sweep surplus to ICICI/Kotak Arbitrage Fund."
            })

        elif goal == "INCREASE_MONEY":
            # Mission: Increase Money
            alpha_alloc = max(5000.0, total_income * 0.08)
            recommendations.append({
                "id": "rec_inc_momentum",
                "priority": "HIGH",
                "badge": "GOAL: INCREASE MONEY",
                "title": "Deploy Capital into High-Growth Momentum Equities",
                "description": f"Route ₹{alpha_alloc:,.0f}/month into market leaders showing dominant relative strength (Trent, Tata Motors, NVIDIA, Broadcom) to maximize capital appreciation.",
                "monthly_savings_impact": round(alpha_alloc * 0.35, 2),
                "annual_savings_impact": round(alpha_alloc * 0.35 * 12, 2),
                "suggested_action": "Set up automated monthly basket buys in top 3 high-beta leaders."
            })

            inflow_target = total_income * 0.2
            recommendations.append({
                "id": "rec_inc_cashflow",
                "priority": "HIGH",
                "badge": "INCOME VELOCITY",
                "title": "Target 20% Velocity Inflow Expansion (₹" + f"{inflow_target:,.0f}" + "/mo)",
                "description": f"Your current monthly inflow is ₹{total_income:,.0f}. Scaling secondary consulting, freelance, or dividend yield by ₹{inflow_target:,.0f}/mo supercharges your compounding engine.",
                "monthly_savings_impact": round(inflow_target, 2),
                "annual_savings_impact": round(inflow_target * 12, 2),
                "suggested_action": "Deploy specialized skills into high-ticket freelance or performance advisory."
            })

            recommendations.append({
                "id": "rec_inc_sectoral",
                "priority": "OPTIMIZATION",
                "badge": "THEMATIC ALPHA",
                "title": "Thematic Allocation: AI Infrastructure & Semiconductor Index",
                "description": "Channel surplus investment into iShares Semiconductor (SOXX) and ICICI Tech Fund to capture global accelerated computing tailwinds.",
                "monthly_savings_impact": round(alpha_alloc * 0.25, 2),
                "annual_savings_impact": round(alpha_alloc * 0.25 * 12, 2),
                "suggested_action": "Allocate 20% of monthly investment pool to sectoral tech leaders."
            })

        else:
            # Mission: Grow Wealth
            sip_boost = max(4000.0, total_income * 0.06)
            proj_10y = sip_boost * (( (1 + 0.15/12)**(120) - 1 ) / (0.15/12))
            recommendations.append({
                "id": "rec_wealth_compounding",
                "priority": "HIGH",
                "badge": "GOAL: GROW WEALTH",
                "title": "Systematic 15% CAGR Wealth Engine Acceleration",
                "description": f"Boosting monthly SIP into Parag Parikh Flexi Cap and Quant Small Cap by ₹{sip_boost:,.0f}/mo compounds to ~₹{proj_10y:,.0f} over 10 years at a 15% historical CAGR.",
                "monthly_savings_impact": round(sip_boost, 2),
                "annual_savings_impact": round(sip_boost * 12, 2),
                "suggested_action": "Activate automatic step-up SIP with 10% annual escalation."
            })

            recommendations.append({
                "id": "rec_wealth_503020",
                "priority": "HIGH",
                "badge": "INSTITUTIONAL BENCHMARK",
                "title": "Institutional 50/30/20 Asset Alignment",
                "description": f"Rebalance discretionary spending to anchor 20%+ of your income (₹{total_income * 0.2:,.0f}/mo) directly into wealth-compounding assets.",
                "monthly_savings_impact": round(total_income * 0.05, 2),
                "annual_savings_impact": round(total_income * 0.6, 2),
                "suggested_action": "Automate mutual fund transfers on salary credit day."
            })

            recommendations.append({
                "id": "rec_wealth_global_hedge",
                "priority": "OPTIMIZATION",
                "badge": "GLOBAL CURRENCY HEDGE",
                "title": "Global Equity Hedge via Vanguard S&P 500 (VOO)",
                "description": "Diversify 15% of your portfolio into USD-denominated index funds to benefit from currency depreciation and global tech dominance.",
                "monthly_savings_impact": round(sip_boost * 0.5, 2),
                "annual_savings_impact": round(sip_boost * 0.5 * 12, 2),
                "suggested_action": "Set up a recurring monthly Dollar-Cost Average (DCA) into VOO/QQQ."
            })

        total_potential_monthly = sum(r["monthly_savings_impact"] for r in recommendations)

        return {
            "currency": "INR",
            "currency_symbol": "₹",
            "goal": goal,
            "income": round(total_income, 2),
            "expense": round(total_expense, 2),
            "rule_50_30_20": {
                "needs": {"amount": round(needs_total, 2), "pct": needs_pct, "ideal_pct": ideal_needs},
                "wants": {"amount": round(wants_total, 2), "pct": wants_pct, "ideal_pct": ideal_wants},
                "savings": {"amount": round(savings_total, 2), "pct": savings_pct, "ideal_pct": ideal_savings}
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
