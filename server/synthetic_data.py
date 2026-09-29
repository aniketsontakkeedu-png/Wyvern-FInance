"""
Wyvern Synthetic Transaction Data Generator & Seed Profiles
Provides realistic, high-fidelity transactions for both US and India contexts,
including seeded anomalies for testing anomaly detection and historical data for savings forecasting.
"""
from datetime import datetime, timedelta
import random

ACCOUNTS = [
    {
        "id": "acc_chk_01",
        "name": "Apex Premier Checking",
        "institution": "JPMorgan Chase & Co.",
        "type": "depository",
        "subtype": "checking",
        "balance": 18450.75,
        "currency": "USD",
        "mask": "4819",
        "status": "active"
    },
    {
        "id": "acc_sav_02",
        "name": "High Yield Treasury Vault (4.85% APY)",
        "institution": "Marcus by Goldman Sachs",
        "type": "depository",
        "subtype": "savings",
        "balance": 45280.00,
        "currency": "USD",
        "mask": "9021",
        "status": "active"
    },
    {
        "id": "acc_cc_03",
        "name": "Sapphire Black Obsidian Card",
        "institution": "JPMorgan Chase & Co.",
        "type": "credit",
        "subtype": "credit card",
        "balance": -1642.30,
        "limit": 25000.00,
        "currency": "USD",
        "mask": "3104",
        "status": "active"
    },
    {
        "id": "acc_inv_04",
        "name": "Wealthfront / Vanguard Direct Index",
        "institution": "Vanguard Group",
        "type": "investment",
        "subtype": "brokerage",
        "balance": 88420.50,
        "currency": "USD",
        "mask": "7712",
        "status": "active"
    }
]

# Historical monthly aggregate balances & flows (for ML forecasting)
MONTHLY_HISTORY = [
    {"month": "2026-04", "income": 7200.00, "spending": 4350.00, "savings": 2850.00},
    {"month": "2026-05", "income": 7200.00, "spending": 4120.00, "savings": 3080.00},
    {"month": "2026-06", "income": 7800.00, "spending": 4680.00, "savings": 3120.00},
    {"month": "2026-07", "income": 7200.00, "spending": 3950.00, "savings": 3250.00},
    {"month": "2026-08", "income": 8400.00, "spending": 4410.00, "savings": 3990.00},
    {"month": "2026-09", "income": 7650.00, "spending": 4210.00, "savings": 3440.00}
]

SEED_TRANSACTIONS = [
    # Recent Anomaly 1: Sudden massive dinner charge spike
    {
        "id": "tx_2026_001",
        "account_id": "acc_cc_03",
        "amount": 842.50,
        "date": "2026-09-28T21:40:00Z",
        "merchant": "L'Espalier Private Dining Room",
        "category": "Food & Dining",
        "pending": False,
        "channel": "in_store",
        "currency": "USD"
    },
    # Recent Anomaly 2: Rapid duplicate flight booking charge within 5 minutes
    {
        "id": "tx_2026_002",
        "account_id": "acc_cc_03",
        "amount": 624.00,
        "date": "2026-09-27T14:10:00Z",
        "merchant": "United Airlines Booking Desk",
        "category": "Travel & Lodging",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_003",
        "account_id": "acc_cc_03",
        "amount": 624.00,
        "date": "2026-09-27T14:14:00Z",
        "merchant": "United Airlines Booking Desk",
        "category": "Travel & Lodging",
        "pending": True,
        "channel": "online",
        "currency": "USD"
    },
    # Recent Anomaly 3: Expensive recurring SaaS plan spike
    {
        "id": "tx_2026_004",
        "account_id": "acc_cc_03",
        "amount": 149.99,
        "date": "2026-09-26T08:00:00Z",
        "merchant": "Adobe Creative Cloud Pro Tier",
        "category": "Subscriptions & Digital",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    # Regular daily transactions
    {
        "id": "tx_2026_005",
        "account_id": "acc_cc_03",
        "amount": 6.85,
        "date": "2026-09-28T08:24:00Z",
        "merchant": "Blue Tokai Coffee Roasters",
        "category": "Food & Dining",
        "pending": False,
        "channel": "in_store",
        "currency": "USD"
    },
    {
        "id": "tx_2026_006",
        "account_id": "acc_cc_03",
        "amount": 42.10,
        "date": "2026-09-27T19:30:00Z",
        "merchant": "Uber Trip Help.Uber.Com",
        "category": "Transportation",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_007",
        "account_id": "acc_chk_01",
        "amount": 1250.00,
        "date": "2026-09-25T10:00:00Z",
        "merchant": "Vanguard Index Funds Automatic Deposit",
        "category": "Investments & Savings",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_008",
        "account_id": "acc_chk_01",
        "amount": 3825.00,
        "date": "2026-09-25T09:00:00Z",
        "merchant": "Direct Deposit Payroll Tech Corp Salary",
        "category": "Income & Deposits",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_009",
        "account_id": "acc_cc_03",
        "amount": 78.40,
        "date": "2026-09-24T18:15:00Z",
        "merchant": "Whole Foods Market Grocery",
        "category": "Food & Dining",
        "pending": False,
        "channel": "in_store",
        "currency": "USD"
    },
    {
        "id": "tx_2026_010",
        "account_id": "acc_cc_03",
        "amount": 18.99,
        "date": "2026-09-23T11:00:00Z",
        "merchant": "Spotify Premium Family Plan",
        "category": "Subscriptions & Digital",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_011",
        "account_id": "acc_cc_03",
        "amount": 22.99,
        "date": "2026-09-22T04:12:00Z",
        "merchant": "Netflix.com Monthly Subscription",
        "category": "Subscriptions & Digital",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_012",
        "account_id": "acc_cc_03",
        "amount": 89.50,
        "date": "2026-09-21T13:45:00Z",
        "merchant": "Target Store Minneapolis",
        "category": "Shopping & Retail",
        "pending": False,
        "channel": "in_store",
        "currency": "USD"
    },
    {
        "id": "tx_2026_013",
        "account_id": "acc_chk_01",
        "amount": 145.00,
        "date": "2026-09-20T16:20:00Z",
        "merchant": "ConEdison Electricity & Gas NYC",
        "category": "Bills & Utilities",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_014",
        "account_id": "acc_chk_01",
        "amount": 85.00,
        "date": "2026-09-19T10:00:00Z",
        "merchant": "Comcast Xfinity Home Internet Bill",
        "category": "Bills & Utilities",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_015",
        "account_id": "acc_cc_03",
        "amount": 34.20,
        "date": "2026-09-18T19:50:00Z",
        "merchant": "Zomato Online Ordering Gurgaon",
        "category": "Food & Dining",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_016",
        "account_id": "acc_cc_03",
        "amount": 142.30,
        "date": "2026-09-17T15:30:00Z",
        "merchant": "Nike Store Flagship",
        "category": "Shopping & Retail",
        "pending": False,
        "channel": "in_store",
        "currency": "USD"
    },
    {
        "id": "tx_2026_017",
        "account_id": "acc_cc_03",
        "amount": 55.00,
        "date": "2026-09-16T12:00:00Z",
        "merchant": "Chevron Fuel Dispenser",
        "category": "Transportation",
        "pending": False,
        "channel": "in_store",
        "currency": "USD"
    },
    {
        "id": "tx_2026_018",
        "account_id": "acc_cc_03",
        "amount": 20.00,
        "date": "2026-09-15T09:10:00Z",
        "merchant": "OpenAI ChatGPT Plus Subscription",
        "category": "Subscriptions & Digital",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_019",
        "account_id": "acc_chk_01",
        "amount": 500.00,
        "date": "2026-09-15T08:00:00Z",
        "merchant": "Zerodha Broking Ltd Coin SIP Funds",
        "category": "Investments & Savings",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_020",
        "account_id": "acc_cc_03",
        "amount": 65.00,
        "date": "2026-09-14T20:30:00Z",
        "merchant": "PVR INOX Multiplex Cinemas Tickets",
        "category": "Entertainment & Leisure",
        "pending": False,
        "channel": "in_store",
        "currency": "USD"
    },
    {
        "id": "tx_2026_021",
        "account_id": "acc_cc_03",
        "amount": 35.80,
        "date": "2026-09-13T13:10:00Z",
        "merchant": "Chipotle Mexican Grill NYC",
        "category": "Food & Dining",
        "pending": False,
        "channel": "in_store",
        "currency": "USD"
    },
    {
        "id": "tx_2026_022",
        "account_id": "acc_cc_03",
        "amount": 115.00,
        "date": "2026-09-12T17:40:00Z",
        "merchant": "Equinox Fitness Club Membership Gym",
        "category": "Health & Fitness",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_023",
        "account_id": "acc_cc_03",
        "amount": 29.50,
        "date": "2026-09-11T12:15:00Z",
        "merchant": "Swiggy Delivery Koramangala Bangalore",
        "category": "Food & Dining",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_024",
        "account_id": "acc_chk_01",
        "amount": 3825.00,
        "date": "2026-09-10T09:00:00Z",
        "merchant": "Direct Deposit Payroll Tech Corp Salary",
        "category": "Income & Deposits",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    },
    {
        "id": "tx_2026_025",
        "account_id": "acc_cc_03",
        "amount": 48.20,
        "date": "2026-09-09T16:00:00Z",
        "merchant": "Amazon.com Marketplace Purchase",
        "category": "Shopping & Retail",
        "pending": False,
        "channel": "online",
        "currency": "USD"
    }
]
