# =============================================================================
# AI Financial Advisor — Web Application Server (Vercel & Local Compatible)
# =============================================================================
"""
FastAPI Server powering the AI Financial Advisor web platform.
Serves the web UI and exposes REST & SSE endpoints for the AI Agent.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from google import genai
from google.genai import types

# ── Local modules ─────────────────────────────────────────────────────────────
from financial_tools import (
    analyze_budget,
    calculate_backdoor_roth_tax,
    calculate_debt_payoff,
    calculate_emergency_fund,
    calculate_fire_timeline,
    calculate_indian_capital_gains_tax,
    calculate_indian_income_tax,
    calculate_investment_growth,
    calculate_loan,
    calculate_net_worth,
    calculate_real_estate_roi,
    calculate_retirement_plan,
    calculate_sgb_vs_gold_etf,
    calculate_sip_returns,
    calculate_tax_efficient_asset_location,
)

load_dotenv()

# UTF-8 fix for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_NAME = "gemini-3.5-flash-lite"
API_KEY = os.environ.get("GEMINI_API_KEY", "")

app = FastAPI(title="ArthaVeda AI — Universal Financial & Tax Fiduciary", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_INSTRUCTION = """\
You are ArthaVeda AI — an expert, autonomous AI Financial Planning & Tax Fiduciary specialized in two primary countries: INDIA 🇮🇳 and the UNITED STATES 🇺🇸.
Your mission is to answer ANY financial, tax, or investment question with complete mathematical precision, smooth clarity, and data-driven frameworks.

======================================================================
CRITICAL CURRENCY & COUNTRY DIRECTIVE (MUST ALWAYS COMPLY)
======================================================================

1. PRIMARY DEFAULT CURRENCY — RUPEES (₹ INR):
   - Prioritize Indian Rupees (₹ INR) as the primary default currency for all general or unspecified financial calculations.
   - Format Indian figures using Lakhs (₹1,00,000) and Crores (₹1,00,00,000).
   - Support Dollars ($ USD) when requested by the user or when addressing US-specific financial scenarios.
   - Current USD/INR conversion baseline: ~$1 USD = ₹83.85 INR.

2. COUNTRY 1: INDIA 🇮🇳 DOMAIN INTELLIGENCE:
   - Income Tax: Expert on New Tax Regime (Budget 2024/2025/2026 - Standard Deduction ₹75k, 87A rebate up to ₹7L) vs Old Tax Regime (Section 80C ₹1.5L, 80D ₹25k/₹50k, 80CCD(1B) NPS ₹50k, HRA).
   - Capital Gains Tax: Equity STCG (20%) & LTCG (12.5% beyond ₹1.25L exemption); Debt Mutual Funds (taxed at slab rate); Real Estate (12.5% LTCG without indexation / Sec 54 & 54F exemptions).
   - Sovereign Gold Bonds (SGB) vs Gold ETFs: SGB offers 2.5% p.a. interest + 100% Tax-Free capital gains at 8-yr maturity vs Gold ETFs (12.5% tax) & Physical Gold (3% GST).
   - Mutual Funds & Equities: Step-up SIPs, Direct vs Regular MFs, ELSS 3-yr lock-in, SWP retirement strategy, Nifty 50/Sensex ETFs, STT, dividend taxes.
   - Government Schemes: PPF (EEE status), EPF/VPF, NPS, Senior Citizen Savings Scheme (SCSS), FDs, RBI Floating Rate Bonds.

3. COUNTRY 2: UNITED STATES 🇺🇸 & CROSS-BORDER DOMAIN INTELLIGENCE:
   - Retirement & Taxes: 401(k), Traditional vs Roth IRA, Backdoor & Mega-Backdoor Roth IRA pro-rata rules (IRS 8606), 4% Safe Withdrawal Rate (SWR), FIRE (Lean/Fat/Coast).
   - Real Estate: NOI, Cap Rate %, Cash-on-Cash ROI, 30-yr vs 15-yr Mortgage Amortization, 1031 exchanges.
   - Cross-Border India ⇄ US Finance: RBI LRS remittance ($250k limit, 20% TCS with tax credit), US Stock investing for Indian residents, NRI NRE/NRO banking, DTAA (Double Tax Avoidance Agreement) credit rules, FEMA repatriation rules.

4. TOOL INVOCATION MAPPINGS:
   - Indian Income Tax (New vs Old Regime): `calculate_indian_income_tax_tool`
   - SIP & Step-Up Mutual Fund Returns: `calculate_sip_returns_tool`
   - Indian Capital Gains Tax (Stocks/Real Estate/Gold/Debt): `calculate_indian_capital_gains_tax_tool`
   - Sovereign Gold Bonds (SGB) vs Gold ETF: `calculate_sgb_vs_gold_etf_tool`
   - Budgeting (50/30/20): `analyze_budget_tool`
   - Debt Payoff (Avalanche vs Snowball): `calculate_debt_payoff_tool`
   - Loans & Mortgages: `calculate_loan_tool`
   - Retirement Planning: `calculate_retirement_plan_tool`
   - FIRE / CoastFIRE: `calculate_fire_timeline_tool`
   - Backdoor Roth IRA Pro-Rata Tax: `calculate_backdoor_roth_tax_tool`
   - Real Estate Investment & Cap Rate: `calculate_real_estate_roi_tool`
   - Asset Location Optimization: `calculate_tax_efficient_asset_location_tool`
   - Compound Growth: `calculate_investment_growth_tool`
   - Net Worth: `calculate_net_worth_tool`
   - Emergency Fund: `calculate_emergency_fund_tool`

5. ALWAYS CALCULATE & ANSWER DIRECTLY:
   When numbers are present, IMMEDIATELY call the relevant tool(s) and present explicit calculations, side-by-side tables, and structured action plans.

MANDATORY DISCLAIMER (include once on first full assessment):
> Disclaimer: I am an AI financial assistant providing educational models and frameworks.
> I am not a certified financial planner or tax advisor. Please verify specific
> tax or legal implications with a licensed professional.
"""

# ── Tool Definitions ──────────────────────────────────────────────────────────

def analyze_budget_tool(
    income: float,
    rent: float = 0.0,
    food: float = 0.0,
    car: float = 0.0,
    utilities: float = 0.0,
    subscriptions: float = 0.0,
    dining_out: float = 0.0,
) -> dict:
    """Calculate 50/30/20 budget breakdown."""
    expenses = {}
    if rent > 0: expenses['rent'] = rent
    if food > 0: expenses['food'] = food
    if car > 0: expenses['car'] = car
    if utilities > 0: expenses['utilities'] = utilities
    if subscriptions > 0: expenses['subscriptions'] = subscriptions
    if dining_out > 0: expenses['dining_out'] = dining_out
    return analyze_budget(income, expenses)

def calculate_emergency_fund_tool(
    monthly_expenses: float,
    months_target: int = 6,
    current_savings: float = 0.0,
    monthly_contribution: float = 0.0,
) -> dict:
    """Calculate emergency fund target, gap, and months to goal."""
    return calculate_emergency_fund(monthly_expenses, months_target, current_savings, monthly_contribution)

def calculate_debt_payoff_tool(
    debts: list,
    extra_payment: float = 0.0,
    strategy: str = "avalanche",
) -> dict:
    """Simulate debt payoff using avalanche or snowball strategy."""
    return calculate_debt_payoff(debts, extra_payment, strategy)

def calculate_investment_growth_tool(
    initial_investment: float,
    monthly_contribution: float,
    annual_return_pct: float,
    years: int,
    inflation_pct: float = 2.5,
) -> dict:
    """Project portfolio growth with compound interest."""
    return calculate_investment_growth(initial_investment, monthly_contribution, annual_return_pct, years, inflation_pct)

def calculate_retirement_plan_tool(
    current_age: int,
    retirement_age: int,
    current_savings: float,
    monthly_contribution: float,
    annual_return_pct: float,
    desired_annual_income: float,
    inflation_pct: float = 2.5,
    withdrawal_rate_pct: float = 4.0,
) -> dict:
    """Project retirement corpus and safe withdrawal rate."""
    return calculate_retirement_plan(
        current_age, retirement_age, current_savings, monthly_contribution,
        annual_return_pct, desired_annual_income, inflation_pct, withdrawal_rate_pct
    )

def calculate_loan_tool(
    principal: float,
    annual_rate_pct: float,
    term_years: int,
    extra_monthly_payment: float = 0.0,
) -> dict:
    """Calculate mortgage or loan amortisation and extra payment savings."""
    return calculate_loan(principal, annual_rate_pct, term_years, extra_monthly_payment)

def calculate_net_worth_tool(assets: dict, liabilities: dict) -> dict:
    """Calculate total assets, liabilities, and net worth."""
    return calculate_net_worth(assets, liabilities)

def calculate_fire_timeline_tool(
    current_age: int,
    current_savings: float,
    monthly_income: float,
    monthly_expenses: float,
    expected_annual_return_pct: float = 7.0,
    swr_pct: float = 4.0,
    fire_multiplier: float = 1.0,
) -> dict:
    """Calculate Financial Independence Retire Early (FIRE) timeline, target corpus, CoastFIRE status, and savings rate."""
    return calculate_fire_timeline(
        current_age, current_savings, monthly_income, monthly_expenses,
        expected_annual_return_pct, swr_pct, fire_multiplier
    )

def calculate_backdoor_roth_tax_tool(
    conversion_amount: float,
    pretax_traditional_ira_balance: float,
    nondeductible_basis: float,
    marginal_tax_rate_pct: float = 32.0,
) -> dict:
    """Calculate IRS Pro-Rata Rule tax liability for Backdoor or Mega-Backdoor Roth IRA conversions."""
    return calculate_backdoor_roth_tax(
        conversion_amount, pretax_traditional_ira_balance, nondeductible_basis, marginal_tax_rate_pct
    )

def calculate_real_estate_roi_tool(
    property_price: float,
    down_payment: float,
    monthly_rent: float,
    annual_property_tax: float,
    annual_insurance: float,
    monthly_hoa_maintenance: float,
    vacancy_rate_pct: float = 5.0,
    mortgage_interest_rate_pct: float = 6.5,
    mortgage_term_years: int = 30,
) -> dict:
    """Calculate Real Estate Investment metrics: Cap Rate, Net Operating Income (NOI), Cash-on-Cash Return (CoC %), and Net Cash Flow."""
    return calculate_real_estate_roi(
        property_price, down_payment, monthly_rent, annual_property_tax,
        annual_insurance, monthly_hoa_maintenance, vacancy_rate_pct,
        mortgage_interest_rate_pct, mortgage_term_years
    )

def calculate_tax_efficient_asset_location_tool(
    taxable_account_balance: float,
    tax_deferred_balance: float,
    tax_exempt_balance: float,
    stock_allocation_pct: float = 80.0,
    bond_allocation_pct: float = 20.0,
) -> dict:
    """Recommends optimal asset placement across Taxable, Tax-Deferred (Traditional 401k/IRA), and Tax-Exempt (Roth/HSA) accounts."""
    return calculate_tax_efficient_asset_location(
        taxable_account_balance, tax_deferred_balance, tax_exempt_balance,
        stock_allocation_pct, bond_allocation_pct
    )

def calculate_indian_income_tax_tool(
    gross_annual_income: float,
    section_80c: float = 150000.0,
    section_80d: float = 25000.0,
    nps_80ccd1b: float = 50000.0,
    hra_exemption: float = 0.0,
) -> dict:
    """Compares Indian Income Tax under New Tax Regime vs Old Tax Regime, recommending the tax-optimal regime."""
    return calculate_indian_income_tax(
        gross_annual_income, section_80c, section_80d, nps_80ccd1b, hra_exemption
    )

def calculate_sip_returns_tool(
    monthly_investment: float,
    expected_annual_return_pct: float = 12.0,
    years: int = 15,
    step_up_annual_pct: float = 10.0,
) -> dict:
    """Calculates returns for Systematic Investment Plans (SIP) in Mutual Funds/Index Funds with optional annual step-up % and LTCG tax."""
    return calculate_sip_returns(
        monthly_investment, expected_annual_return_pct, years, step_up_annual_pct
    )

def calculate_indian_capital_gains_tax_tool(
    asset_type: str,
    purchase_price: float,
    sale_price: float,
    holding_period_months: int,
    investor_marginal_tax_rate_pct: float = 30.0,
) -> dict:
    """Calculates Capital Gains Tax liability in India across Equity (STCG 20%, LTCG 12.5%), Debt MFs, Real Estate, and Sovereign Gold Bonds (SGB)."""
    return calculate_indian_capital_gains_tax(
        asset_type, purchase_price, sale_price, holding_period_months, investor_marginal_tax_rate_pct
    )

def calculate_sgb_vs_gold_etf_tool(
    initial_investment: float,
    tenure_years: int = 8,
    expected_gold_cagr_pct: float = 9.0,
) -> dict:
    """Compares Sovereign Gold Bonds (SGB - 2.5% interest & 0% tax) vs Gold ETFs vs Physical Gold."""
    return calculate_sgb_vs_gold_etf(
        initial_investment, tenure_years, expected_gold_cagr_pct
    )

TOOLS = [
    analyze_budget_tool,
    calculate_emergency_fund_tool,
    calculate_debt_payoff_tool,
    calculate_investment_growth_tool,
    calculate_retirement_plan_tool,
    calculate_loan_tool,
    calculate_net_worth_tool,
    calculate_fire_timeline_tool,
    calculate_backdoor_roth_tax_tool,
    calculate_real_estate_roi_tool,
    calculate_tax_efficient_asset_location_tool,
    calculate_indian_income_tax_tool,
    calculate_sip_returns_tool,
    calculate_indian_capital_gains_tax_tool,
    calculate_sgb_vs_gold_etf_tool,
]

# ── API Models ────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class DirectCalcRequest(BaseModel):
    tool: str
    args: Dict[str, Any]

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    key = os.environ.get("GEMINI_API_KEY", API_KEY)
    if not key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")

    session_id = req.session_id or str(uuid.uuid4())

    async def generate_stream():
        try:
            with genai.Client(api_key=key) as client_instance:
                chat = client_instance.chats.create(model=MODEL_NAME)
                response = chat.send_message_stream(
                    req.message,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        tools=TOOLS,
                        temperature=0.1,
                    ),
                )
                for chunk in response:
                    if chunk.candidates:
                        for part in chunk.candidates[0].content.parts:
                            if part.text:
                                data = json.dumps({"text": part.text, "session_id": session_id})
                                yield f"data: {data}\n\n"
                
                yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"
        except Exception as e:
            err_data = json.dumps({"error": str(e), "session_id": session_id})
            yield f"data: {err_data}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@app.post("/api/calc")
async def direct_calc(req: DirectCalcRequest):
    """Direct execution of tools for UI calculator widgets."""
    tool_name = req.tool
    args = req.args

    tool_map = {
        "analyze_budget": analyze_budget,
        "calculate_emergency_fund": calculate_emergency_fund,
        "calculate_debt_payoff": calculate_debt_payoff,
        "calculate_investment_growth": calculate_investment_growth,
        "calculate_retirement_plan": calculate_retirement_plan,
        "calculate_loan": calculate_loan,
        "calculate_net_worth": calculate_net_worth,
        "calculate_fire_timeline": calculate_fire_timeline,
        "calculate_backdoor_roth_tax": calculate_backdoor_roth_tax,
        "calculate_real_estate_roi": calculate_real_estate_roi,
        "calculate_tax_efficient_asset_location": calculate_tax_efficient_asset_location,
        "calculate_indian_income_tax": calculate_indian_income_tax,
        "calculate_sip_returns": calculate_sip_returns,
        "calculate_indian_capital_gains_tax": calculate_indian_capital_gains_tax,
        "calculate_sgb_vs_gold_etf": calculate_sgb_vs_gold_etf,
    }

    if tool_name not in tool_map:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")

    try:
        res = tool_map[tool_name](**args)
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/reset")
async def reset_session(req: Dict[str, str]):
    new_sid = str(uuid.uuid4())
    return {"status": "reset", "session_id": new_sid}

@app.get("/api/forex")
async def get_forex_rate():
    """Fetches live USD/INR exchange rate from public exchange rate API."""
    import urllib.request
    try:
        req = urllib.request.Request("https://open.er-api.com/v6/latest/USD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            rate = data.get("rates", {}).get("INR", 83.85)
            last_updated = data.get("time_last_update_utc", "")
            return {"status": "success", "pair": "USD/INR", "rate": rate, "last_updated": last_updated}
    except Exception as e:
        return {"status": "fallback", "pair": "USD/INR", "rate": 83.85, "error": str(e)}

@app.get("/")
async def serve_index():
    html_file = os.path.join(BASE_DIR, "index.html")
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
