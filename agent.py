# =============================================================================
# Financial Advisor Agent — Main Entry Point
# =============================================================================
"""
Agentic AI Financial Planning Assistant powered by Google Gemini.

Architecture
────────────
  • Stateful multi-turn conversation via google.genai Chat
  • Seven financial tools with automatic function calling
  • Streaming output for responsive UX
  • Rich terminal rendering (panels, markdown, rules)

Usage
─────
  py agent.py          (Windows)
  python3 agent.py     (Linux / macOS)

Environment
───────────
  GEMINI_API_KEY in .env file (or exported as env var).
"""

from __future__ import annotations

import json
import os
import sys
import warnings
from typing import Any

# Ensure UTF-8 output encoding across Windows legacy consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
from google import genai
from google.genai import types
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

# Ignore warnings
warnings.filterwarnings("ignore")

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

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

load_dotenv()

MODEL_NAME = "gemini-3.5-flash-lite"

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

# ─────────────────────────────────────────────────────────────────────────────
# TOOL WRAPPERS — Python functions with type hints and docstrings
# ─────────────────────────────────────────────────────────────────────────────

def analyze_budget_tool(monthly_income: float, expenses: dict) -> dict:
    """
    Analyze monthly budget using the 50/30/20 framework.
    Calculates surplus/deficit, savings rate, and 50/30/20 targets.

    Args:
        monthly_income: Take-home monthly income in dollars (e.g. 5500.0).
        expenses: Key-value dictionary of expense names to monthly dollar amounts,
                  e.g. {"rent": 1400.0, "groceries": 500.0, "car": 300.0, "utilities": 150.0, "subscriptions": 200.0, "dining_out": 400.0}.
    """
    return analyze_budget(monthly_income, expenses)


def calculate_emergency_fund_tool(
    monthly_expenses: float,
    months_target: int = 6,
    current_savings: float = 0.0,
    monthly_contribution: float = 0.0,
) -> dict:
    """
    Calculate emergency fund target, gap to goal, and months to reach it.

    Args:
        monthly_expenses: Total essential monthly expenses in dollars.
        months_target: Months of expenses to save as buffer (default 6).
        current_savings: Existing emergency fund balance (default 0).
        monthly_contribution: Monthly amount directed to the emergency fund.
    """
    return calculate_emergency_fund(
        monthly_expenses, months_target, current_savings, monthly_contribution
    )


def calculate_debt_payoff_tool(
    debts: list,
    extra_payment: float = 0.0,
    strategy: str = "avalanche",
) -> dict:
    """
    Simulate debt payoff using avalanche or snowball strategy.
    Returns months to payoff, total interest paid, and per-debt timeline.

    Args:
        debts: List of dicts, each with keys name (str), balance (float),
               apr (float, annual % rate), min_payment (float).
        extra_payment: Extra monthly dollars applied to the priority debt.
        strategy: "avalanche" (highest APR first) or "snowball" (lowest balance first).
    """
    return calculate_debt_payoff(debts, extra_payment, strategy)


def calculate_investment_growth_tool(
    initial_investment: float,
    monthly_contribution: float,
    annual_return_pct: float,
    years: int,
    inflation_pct: float = 2.5,
) -> dict:
    """
    Project portfolio growth with compound interest and monthly contributions.

    Args:
        initial_investment: Starting lump-sum balance in dollars.
        monthly_contribution: Amount invested each month.
        annual_return_pct: Expected annual return, e.g. 7 for 7%.
        years: Investment time horizon in years.
        inflation_pct: Annual inflation assumption for real value (default 2.5).
    """
    return calculate_investment_growth(
        initial_investment, monthly_contribution, annual_return_pct, years, inflation_pct
    )


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
    """
    Project retirement corpus and assess if it meets desired income using
    the safe withdrawal rate (default 4% rule). Calculates any shortfall.

    Args:
        current_age: User's current age in years.
        retirement_age: Target retirement age.
        current_savings: Current retirement account balance.
        monthly_contribution: Monthly retirement contribution.
        annual_return_pct: Expected annual portfolio return (%).
        desired_annual_income: Desired annual retirement income (today's dollars).
        inflation_pct: Annual inflation rate assumption (default 2.5).
        withdrawal_rate_pct: Safe withdrawal rate, default 4.0 (4% rule).
    """
    return calculate_retirement_plan(
        current_age, retirement_age, current_savings, monthly_contribution,
        annual_return_pct, desired_annual_income, inflation_pct, withdrawal_rate_pct,
    )


def calculate_loan_tool(
    principal: float,
    annual_rate_pct: float,
    term_years: int,
    extra_monthly_payment: float = 0.0,
) -> dict:
    """
    Calculate loan/mortgage monthly payment, total interest, and impact of
    extra monthly payments (interest saved, months shaved off the term).

    Args:
        principal: Loan amount in dollars.
        annual_rate_pct: Annual interest rate, e.g. 6.5 for 6.5%.
        term_years: Loan term in years (e.g. 30 for a 30-year mortgage).
        extra_monthly_payment: Additional payment above the required minimum.
    """
    return calculate_loan(principal, annual_rate_pct, term_years, extra_monthly_payment)


def calculate_net_worth_tool(assets: dict, liabilities: dict) -> dict:
    """
    Calculate net worth: total assets minus total liabilities. Also returns
    the debt-to-asset ratio.

    Args:
        assets: Dict of asset names to dollar values,
                e.g. {"savings": 10000, "home": 320000, "car": 18000}.
        liabilities: Dict of liability names to dollar values,
                     e.g. {"mortgage": 260000, "car_loan": 9000}.
    """
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


# All tools in one list
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

# ─────────────────────────────────────────────────────────────────────────────
# RICH CONSOLE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

console = Console(force_terminal=True, legacy_windows=False)


def print_banner() -> None:
    t = Text()
    t.append("AI Financial Advisor Agent\n", style="bold green")
    t.append(f"Powered by {MODEL_NAME} | 7 Financial Tools | Streaming\n", style="dim")
    console.print(Panel(t, border_style="green", padding=(0, 2)))
    console.print(
        "[dim]Commands: [bold]quit[/bold] / [bold]exit[/bold] to leave | "
        "[bold]new[/bold] to reset conversation[/dim]\n"
    )


def print_agent(text: str) -> None:
    console.print(Rule("[green]Financial Advisor[/green]", style="green"))
    console.print(Markdown(text))
    console.print()


def run_turn(chat: Any, user_message: str) -> str:
    """
    Send user message to chat with streaming output.
    Automatic tool execution is handled by google-genai SDK.
    """
    console.print()
    console.print("  [dim]* Thinking & Calculating...[/dim]", end="\r")

    response = chat.send_message_stream(
        user_message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=TOOLS,
            temperature=0.1,
        ),
    )

    collected: list[str] = []
    first_chunk = True

    for chunk in response:
        if chunk.candidates:
            for part in chunk.candidates[0].content.parts:
                if part.text:
                    if first_chunk:
                        console.print(" " * 35, end="\r")
                        first_chunk = False
                    print(part.text, end="", flush=True)
                    collected.append(part.text)

    print()
    return "".join(collected)


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        rprint(
            "[red bold]Error:[/red bold] GEMINI_API_KEY not set. "
            "Add it to .env or export it."
        )
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    chat = client.chats.create(model=MODEL_NAME)

    print_banner()
    console.print("[bold green]Hello! I'm your AI Financial Advisor.[/bold green]")
    console.print(
        "Tell me about your financial situation — income, debts, savings goals, "
        "retirement plans — and I'll build a personalised action plan.\n"
    )

    while True:
        try:
            user_input = console.input("[bold cyan]You > [/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Session ended. Goodbye![/dim]")
            break

        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in ("quit", "exit", "q"):
            console.print("[dim]Session ended. Goodbye![/dim]")
            break
        if cmd == "new":
            chat = client.chats.create(model=MODEL_NAME)
            console.print("[dim]Conversation reset. Starting fresh.[/dim]\n")
            continue

        try:
            response_text = run_turn(chat, user_input)
            if response_text:
                print_agent(response_text)
        except Exception as exc:
            console.print(f"\n[red]Agent error:[/red] {exc}")
            console.print("[dim]Type 'new' to reset or try again.[/dim]\n")


if __name__ == "__main__":
    main()
