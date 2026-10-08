# =============================================================================
# Financial Advisor Agent — Tool Schema Definitions
# =============================================================================
"""
JSON-schema tool declarations passed to the Gemini Interactions API.
Each entry maps 1-to-1 with a function in financial_tools.py.
"""

FINANCIAL_TOOLS: list[dict] = [
    # ── 1. Budget Analysis ────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "analyze_budget",
        "description": (
            "Analyze the user's monthly budget using the 50/30/20 framework. "
            "Calculates surplus/deficit, savings rate, and compares actuals to targets. "
            "Call this whenever the user mentions income and spending."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "monthly_income": {
                    "type": "number",
                    "description": "Net (take-home) monthly income in dollars.",
                },
                "expenses": {
                    "type": "object",
                    "description": (
                        "Map of expense category names to their monthly dollar amounts. "
                        "E.g. {\"rent\": 1200, \"groceries\": 400, \"utilities\": 150}."
                    ),
                    "additionalProperties": {"type": "number"},
                },
            },
            "required": ["monthly_income", "expenses"],
        },
    },

    # ── 2. Emergency Fund ─────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "calculate_emergency_fund",
        "description": (
            "Calculate emergency fund target, gap, and time-to-goal given a monthly contribution."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "monthly_expenses": {
                    "type": "number",
                    "description": "Total essential monthly expenses.",
                },
                "months_target": {
                    "type": "integer",
                    "description": "Number of months of expenses to save (default 6).",
                    "default": 6,
                },
                "current_savings": {
                    "type": "number",
                    "description": "Current emergency fund balance (default 0).",
                    "default": 0,
                },
                "monthly_contribution": {
                    "type": "number",
                    "description": "Amount allocated to emergency fund each month.",
                    "default": 0,
                },
            },
            "required": ["monthly_expenses"],
        },
    },

    # ── 3. Debt Payoff ────────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "calculate_debt_payoff",
        "description": (
            "Simulate debt payoff using avalanche (highest APR first) or snowball "
            "(lowest balance first) strategy. Returns months to payoff, total interest "
            "paid, and per-debt timeline. Use this to compare strategies or model extra payments."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "debts": {
                    "type": "array",
                    "description": "List of debt objects.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name":        {"type": "string",  "description": "Debt label (e.g. 'Visa Card')."},
                            "balance":     {"type": "number",  "description": "Current outstanding balance."},
                            "apr":         {"type": "number",  "description": "Annual Percentage Rate (e.g. 22.5 for 22.5%)."},
                            "min_payment": {"type": "number",  "description": "Required minimum monthly payment."},
                        },
                        "required": ["name", "balance", "apr", "min_payment"],
                    },
                },
                "extra_payment": {
                    "type": "number",
                    "description": "Extra monthly dollar amount applied to priority debt (default 0).",
                    "default": 0,
                },
                "strategy": {
                    "type": "string",
                    "enum": ["avalanche", "snowball"],
                    "description": "Payoff strategy: 'avalanche' minimises interest; 'snowball' for motivation.",
                    "default": "avalanche",
                },
            },
            "required": ["debts"],
        },
    },

    # ── 4. Investment Growth ──────────────────────────────────────────────────
    {
        "type": "function",
        "name": "calculate_investment_growth",
        "description": (
            "Project portfolio growth using compound interest with monthly contributions. "
            "Returns nominal and inflation-adjusted future value, total gains, "
            "and a year-by-year balance table."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "initial_investment": {
                    "type": "number",
                    "description": "Lump-sum starting balance.",
                },
                "monthly_contribution": {
                    "type": "number",
                    "description": "Amount invested each month.",
                },
                "annual_return_pct": {
                    "type": "number",
                    "description": "Expected annual return percentage (e.g. 7 for 7%).",
                },
                "years": {
                    "type": "integer",
                    "description": "Investment time horizon in years.",
                },
                "inflation_pct": {
                    "type": "number",
                    "description": "Assumed annual inflation rate for real-value calculation (default 2.5).",
                    "default": 2.5,
                },
            },
            "required": ["initial_investment", "monthly_contribution", "annual_return_pct", "years"],
        },
    },

    # ── 5. Retirement Planning ────────────────────────────────────────────────
    {
        "type": "function",
        "name": "calculate_retirement_plan",
        "description": (
            "Project retirement corpus at target retirement age, assess whether it meets "
            "the desired inflation-adjusted income via the safe withdrawal rule, "
            "and calculate any additional monthly savings needed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "current_age":             {"type": "integer", "description": "User's current age."},
                "retirement_age":          {"type": "integer", "description": "Target retirement age."},
                "current_savings":         {"type": "number",  "description": "Current retirement savings balance."},
                "monthly_contribution":    {"type": "number",  "description": "Monthly retirement contribution."},
                "annual_return_pct":       {"type": "number",  "description": "Expected annual portfolio return (%)."},
                "desired_annual_income":   {"type": "number",  "description": "Desired annual income in today's dollars."},
                "inflation_pct":           {"type": "number",  "description": "Annual inflation rate assumption (default 2.5).", "default": 2.5},
                "withdrawal_rate_pct":     {"type": "number",  "description": "Safe withdrawal rate (default 4.0 = 4% rule).", "default": 4.0},
            },
            "required": [
                "current_age", "retirement_age", "current_savings",
                "monthly_contribution", "annual_return_pct", "desired_annual_income",
            ],
        },
    },

    # ── 6. Loan / Mortgage ────────────────────────────────────────────────────
    {
        "type": "function",
        "name": "calculate_loan",
        "description": (
            "Compute loan/mortgage monthly payment, total interest, and the effect of "
            "extra monthly payments (interest saved, months saved). Good for mortgage "
            "comparisons (15 vs 30 year) or modelling any instalment loan."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "principal":              {"type": "number",  "description": "Loan amount."},
                "annual_rate_pct":        {"type": "number",  "description": "Annual interest rate (%)."},
                "term_years":             {"type": "integer", "description": "Loan term in years."},
                "extra_monthly_payment":  {"type": "number",  "description": "Additional monthly payment above minimum (default 0).", "default": 0},
            },
            "required": ["principal", "annual_rate_pct", "term_years"],
        },
    },

    # ── 7. Net Worth Snapshot ─────────────────────────────────────────────────
    {
        "type": "function",
        "name": "calculate_net_worth",
        "description": "Calculate total assets, total liabilities, net worth, and debt-to-asset ratio.",
        "parameters": {
            "type": "object",
            "properties": {
                "assets": {
                    "type": "object",
                    "description": "Map of asset names to dollar values. E.g. {\"savings\": 10000, \"car\": 15000}.",
                    "additionalProperties": {"type": "number"},
                },
                "liabilities": {
                    "type": "object",
                    "description": "Map of liability names to dollar values. E.g. {\"car_loan\": 8000, \"credit_card\": 3000}.",
                    "additionalProperties": {"type": "number"},
                },
            },
            "required": ["assets", "liabilities"],
        },
    },
]
