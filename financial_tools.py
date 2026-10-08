# =============================================================================
# Financial Advisor Agent — Core Financial Calculation Tools
# =============================================================================
"""
Pure-math financial utilities used by the agent's function-calling tools.
All calculations are deterministic and show intermediate steps.
Includes advanced calculators for FIRE, Backdoor Roth, Real Estate ROI, and Tax Location.
"""

from __future__ import annotations
import math
from typing import Any


# ─────────────────────────────────────────────────────────────────────────────
# BUDGET ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def analyze_budget(
    monthly_income: float,
    expenses: dict[str, float],
) -> dict[str, Any]:
    """
    50/30/20 budget framework analysis.
    Returns categorised breakdown, surplus/deficit, and recommendations.
    """
    total_expenses = sum(expenses.values())
    surplus = monthly_income - total_expenses
    savings_rate = (surplus / monthly_income * 100) if monthly_income else 0

    # 50/30/20 targets
    needs_target   = monthly_income * 0.50
    wants_target   = monthly_income * 0.30
    savings_target = monthly_income * 0.20

    steps = [
        f"Monthly Income           : ${monthly_income:,.2f}",
        f"Total Expenses           : ${total_expenses:,.2f}",
        f"Monthly Surplus/Deficit  : ${surplus:+,.2f}",
        f"Actual Savings Rate      : {savings_rate:.1f}%",
        "",
        "─── 50/30/20 Targets ───────────────────────────────────────",
        f"  Needs   (50%) target   : ${needs_target:,.2f}",
        f"  Wants   (30%) target   : ${wants_target:,.2f}",
        f"  Savings (20%) target   : ${savings_target:,.2f}",
    ]

    return {
        "monthly_income": monthly_income,
        "total_expenses": total_expenses,
        "surplus": surplus,
        "savings_rate_pct": round(savings_rate, 2),
        "needs_target": round(needs_target, 2),
        "wants_target": round(wants_target, 2),
        "savings_target": round(savings_target, 2),
        "expense_breakdown": expenses,
        "calculation_steps": "\n".join(steps),
    }


# ─────────────────────────────────────────────────────────────────────────────
# EMERGENCY FUND
# ─────────────────────────────────────────────────────────────────────────────

def calculate_emergency_fund(
    monthly_expenses: float,
    months_target: int = 6,
    current_savings: float = 0.0,
    monthly_contribution: float = 0.0,
) -> dict[str, Any]:
    """How long to reach an emergency fund target given a monthly contribution."""
    target = monthly_expenses * months_target
    gap = max(0.0, target - current_savings)
    months_to_goal = math.ceil(gap / monthly_contribution) if monthly_contribution > 0 else None

    steps = [
        f"Monthly Expenses         : ${monthly_expenses:,.2f}",
        f"Target ({months_target} months)        : ${target:,.2f}",
        f"Current Savings          : ${current_savings:,.2f}",
        f"Gap to Fill              : ${gap:,.2f}",
        f"Monthly Contribution     : ${monthly_contribution:,.2f}",
        f"Months to Goal           : {months_to_goal if months_to_goal else 'N/A (no contribution set)'}",
    ]

    return {
        "target_amount": round(target, 2),
        "current_savings": round(current_savings, 2),
        "gap": round(gap, 2),
        "monthly_contribution": round(monthly_contribution, 2),
        "months_to_goal": months_to_goal,
        "calculation_steps": "\n".join(steps),
    }


# ─────────────────────────────────────────────────────────────────────────────
# DEBT PAYOFF STRATEGIES
# ─────────────────────────────────────────────────────────────────────────────

def calculate_debt_payoff(
    debts: list[dict],          # [{name, balance, apr, min_payment}]
    extra_payment: float = 0.0,
    strategy: str = "avalanche",  # "avalanche" | "snowball"
) -> dict[str, Any]:
    """
    Simulates month-by-month debt payoff using avalanche or snowball method.
    """
    strategy = strategy.lower()
    if strategy not in ("avalanche", "snowball"):
        strategy = "avalanche"

    debt_list = [
        {
            "name": d["name"],
            "balance": float(d["balance"]),
            "monthly_rate": float(d["apr"]) / 100 / 12,
            "min_payment": float(d["min_payment"]),
            "paid_off_month": None,
            "total_interest": 0.0,
        }
        for d in debts
    ]

    total_interest = 0.0
    month = 0
    max_months = 600

    while any(d["balance"] > 0 for d in debt_list) and month < max_months:
        month += 1

        for d in debt_list:
            if d["balance"] > 0:
                interest = d["balance"] * d["monthly_rate"]
                d["balance"] += interest
                d["total_interest"] += interest
                total_interest += interest

        active = [d for d in debt_list if d["balance"] > 0]
        if strategy == "avalanche":
            active.sort(key=lambda x: x["monthly_rate"], reverse=True)
        else:
            active.sort(key=lambda x: x["balance"])

        remaining_extra = extra_payment
        for d in active:
            payment = min(d["min_payment"], d["balance"])
            d["balance"] = max(0.0, d["balance"] - payment)
            if d["balance"] == 0 and d["paid_off_month"] is None:
                d["paid_off_month"] = month

        if active:
            target = next((d for d in active if d["balance"] > 0), None)
            if target:
                payment = min(remaining_extra, target["balance"])
                target["balance"] = max(0.0, target["balance"] - payment)
                if target["balance"] == 0 and target["paid_off_month"] is None:
                    target["paid_off_month"] = month

    years = month // 12
    months_remaining = month % 12

    per_debt = [
        {
            "name": d["name"],
            "paid_off_month": d["paid_off_month"] or month,
            "interest_paid": round(d["total_interest"], 2),
        }
        for d in debt_list
    ]

    steps = [
        f"Strategy                 : {strategy.capitalize()} Method",
        f"Extra Monthly Payment    : ${extra_payment:,.2f}",
        f"Total Months to Payoff   : {month} ({years}y {months_remaining}m)",
        f"Total Interest Paid      : ${total_interest:,.2f}",
    ]

    return {
        "strategy": strategy,
        "months_to_payoff": month,
        "years_to_payoff": round(month / 12, 1),
        "total_interest_paid": round(total_interest, 2),
        "per_debt_timeline": per_debt,
        "calculation_steps": "\n".join(steps),
    }


# ─────────────────────────────────────────────────────────────────────────────
# INVESTMENT GROWTH — COMPOUND INTEREST
# ─────────────────────────────────────────────────────────────────────────────

def calculate_investment_growth(
    initial_investment: float,
    monthly_contribution: float,
    annual_return_pct: float,
    years: int,
    inflation_pct: float = 2.5,
) -> dict[str, Any]:
    """Compound growth with monthly contributions and inflation adjustment."""
    monthly_rate = annual_return_pct / 100 / 12
    n = years * 12

    fv_lump = initial_investment * (1 + monthly_rate) ** n
    if monthly_rate > 0:
        fv_annuity = monthly_contribution * (((1 + monthly_rate) ** n - 1) / monthly_rate)
    else:
        fv_annuity = monthly_contribution * n

    nominal_fv = fv_lump + fv_annuity
    total_contributed = initial_investment + monthly_contribution * n
    total_gains = nominal_fv - total_contributed
    real_fv = nominal_fv / ((1 + inflation_pct / 100) ** years)

    yearly = []
    balance = initial_investment
    for y in range(1, years + 1):
        for _ in range(12):
            balance = balance * (1 + monthly_rate) + monthly_contribution
        yearly.append({"year": y, "balance": round(balance, 2)})

    steps = [
        f"Initial Investment       : ${initial_investment:,.2f}",
        f"Monthly Contribution     : ${monthly_contribution:,.2f}",
        f"Annual Return            : {annual_return_pct}%",
        f"Time Horizon             : {years} years",
        f"Nominal Future Value     : ${nominal_fv:,.2f}",
        f"Total Contributed        : ${total_contributed:,.2f}",
        f"Total Investment Gains   : ${total_gains:,.2f}",
        f"Real Value ({inflation_pct}% inflation): ${real_fv:,.2f}",
    ]

    return {
        "nominal_future_value": round(nominal_fv, 2),
        "real_future_value": round(real_fv, 2),
        "total_contributed": round(total_contributed, 2),
        "total_gains": round(total_gains, 2),
        "yearly_balances": yearly,
        "calculation_steps": "\n".join(steps),
    }


# ─────────────────────────────────────────────────────────────────────────────
# RETIREMENT PLANNING & SWR
# ─────────────────────────────────────────────────────────────────────────────

def calculate_retirement_plan(
    current_age: int,
    retirement_age: int,
    current_savings: float,
    monthly_contribution: float,
    annual_return_pct: float,
    desired_annual_income: float,
    inflation_pct: float = 2.5,
    withdrawal_rate_pct: float = 4.0,
) -> dict[str, Any]:
    """Project retirement corpus using 4% Safe Withdrawal Rate (SWR)."""
    years_to_retire = retirement_age - current_age
    monthly_rate = annual_return_pct / 100 / 12
    n = years_to_retire * 12

    fv_lump = current_savings * (1 + monthly_rate) ** n
    fv_annuity = (
        monthly_contribution * (((1 + monthly_rate) ** n - 1) / monthly_rate)
        if monthly_rate > 0
        else monthly_contribution * n
    )
    projected_corpus = fv_lump + fv_annuity

    real_annual_income = desired_annual_income * ((1 + inflation_pct / 100) ** years_to_retire)
    required_corpus = real_annual_income / (withdrawal_rate_pct / 100)
    gap = required_corpus - projected_corpus

    additional_monthly = 0.0
    if gap > 0 and monthly_rate > 0:
        additional_monthly = (gap * monthly_rate) / (((1 + monthly_rate) ** n) - 1)

    steps = [
        f"Years to Retirement      : {years_to_retire}",
        f"Current Savings          : ${current_savings:,.2f}",
        f"Projected Corpus         : ${projected_corpus:,.2f}",
        f"Required Corpus ({withdrawal_rate_pct}% SWR): ${required_corpus:,.2f}",
        f"Surplus / (Shortfall)    : ${-gap:+,.2f}",
    ]

    return {
        "years_to_retirement": years_to_retire,
        "projected_corpus": round(projected_corpus, 2),
        "required_corpus": round(required_corpus, 2),
        "surplus_or_shortfall": round(-gap, 2),
        "additional_monthly_contribution_needed": round(additional_monthly, 2),
        "is_on_track": gap <= 0,
        "calculation_steps": "\n".join(steps),
    }


# ─────────────────────────────────────────────────────────────────────────────
# LOAN / MORTGAGE AMORTISATION
# ─────────────────────────────────────────────────────────────────────────────

def calculate_loan(
    principal: float,
    annual_rate_pct: float,
    term_years: int,
    extra_monthly_payment: float = 0.0,
) -> dict[str, Any]:
    """Calculate loan amortisation and extra payment savings."""
    monthly_rate = annual_rate_pct / 100 / 12
    n = term_years * 12

    if monthly_rate == 0:
        base_payment = principal / n
    else:
        base_payment = principal * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)

    balance = principal
    total_interest = 0.0
    for _ in range(n):
        interest = balance * monthly_rate
        total_interest += interest
        balance -= (base_payment - interest)

    balance_extra = principal
    total_interest_extra = 0.0
    months_extra = 0
    while balance_extra > 0.01 and months_extra < n:
        interest = balance_extra * monthly_rate
        total_interest_extra += interest
        payment = min(base_payment + extra_monthly_payment, balance_extra + interest)
        balance_extra -= (payment - interest)
        months_extra += 1

    interest_saved = total_interest - total_interest_extra
    months_saved = n - months_extra

    steps = [
        f"Base Monthly Payment     : ${base_payment:,.2f}",
        f"Total Interest (base)    : ${total_interest:,.2f}",
        f"Extra Monthly Payment    : ${extra_monthly_payment:,.2f}",
        f"New Payoff Term          : {months_extra} months ({months_extra//12}y {months_extra%12}m)",
        f"Interest Saved           : ${interest_saved:,.2f}",
        f"Months Saved             : {months_saved}",
    ]

    return {
        "monthly_payment": round(base_payment, 2),
        "total_interest_no_extra": round(total_interest, 2),
        "months_with_extra_payment": months_extra,
        "interest_saved": round(interest_saved, 2),
        "months_saved": months_saved,
        "calculation_steps": "\n".join(steps),
    }


# ─────────────────────────────────────────────────────────────────────────────
# NET WORTH
# ─────────────────────────────────────────────────────────────────────────────

def calculate_net_worth(
    assets: dict[str, float],
    liabilities: dict[str, float],
) -> dict[str, Any]:
    """Calculate total assets, liabilities, and net worth."""
    total_assets = sum(assets.values())
    total_liabilities = sum(liabilities.values())
    net_worth = total_assets - total_liabilities
    ratio = (total_liabilities / total_assets * 100) if total_assets else 0

    steps = [
        f"Total Assets             : ${total_assets:,.2f}",
        f"Total Liabilities        : ${total_liabilities:,.2f}",
        f"Net Worth                : ${net_worth:+,.2f}",
        f"Debt-to-Asset Ratio      : {ratio:.1f}%",
    ]

    return {
        "total_assets": round(total_assets, 2),
        "total_liabilities": round(total_liabilities, 2),
        "net_worth": round(net_worth, 2),
        "debt_to_asset_ratio_pct": round(ratio, 2),
        "calculation_steps": "\n".join(steps),
    }


# ─────────────────────────────────────────────────────────────────────────────
# NEW ADVANCED COMPLEX FINANCIAL CALCULATORS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_fire_timeline(
    current_age: int,
    current_savings: float,
    monthly_income: float,
    monthly_expenses: float,
    expected_annual_return_pct: float = 7.0,
    swr_pct: float = 4.0,
    fire_multiplier: float = 1.0, # 0.75 for LeanFIRE, 1.0 for Standard, 1.5 for FatFIRE
) -> dict[str, Any]:
    """
    Calculate Financial Independence, Retire Early (FIRE) Timeline, CoastFIRE status, and FIRE target corpus.
    """
    annual_expenses = monthly_expenses * 12 * fire_multiplier
    fire_target_corpus = annual_expenses / (swr_pct / 100)
    monthly_savings = max(0.0, monthly_income - monthly_expenses)
    savings_rate_pct = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0.0

    monthly_rate = expected_annual_return_pct / 100 / 12
    
    # Simulate months to FIRE target
    balance = current_savings
    months = 0
    max_months = 720 # 60 years max

    while balance < fire_target_corpus and months < max_months:
        months += 1
        balance = balance * (1 + monthly_rate) + monthly_savings

    fire_age = current_age + (months // 12)
    fire_years = round(months / 12, 1)

    # CoastFIRE Calculation: Corpus needed today so that without adding another dollar, it reaches FIRE target at age 65
    years_to_65 = max(1, 65 - current_age)
    coast_fire_target_today = fire_target_corpus / ((1 + expected_annual_return_pct / 100) ** years_to_65)
    is_coast_fire = current_savings >= coast_fire_target_today

    steps = [
        f"Annual Expenses (Target)  : ${annual_expenses:,.2f}/yr",
        f"FIRE Target Corpus ({swr_pct}% SWR): ${fire_target_corpus:,.2f}",
        f"Monthly Savings           : ${monthly_savings:,.2f} ({savings_rate_pct:.1f}% savings rate)",
        f"Years to FIRE             : {fire_years} years",
        f"Projected FIRE Age        : Age {fire_age}",
        f"CoastFIRE Required Today  : ${coast_fire_target_today:,.2f}",
        f"CoastFIRE Status          : {'REACHED ✓' if is_coast_fire else 'In Progress'}",
    ]

    return {
        "fire_target_corpus": round(fire_target_corpus, 2),
        "savings_rate_pct": round(savings_rate_pct, 2),
        "years_to_fire": fire_years,
        "fire_age": fire_age,
        "coast_fire_target_today": round(coast_fire_target_today, 2),
        "is_coast_fire": is_coast_fire,
        "calculation_steps": "\n".join(steps),
    }


def calculate_backdoor_roth_tax(
    conversion_amount: float,
    pretax_traditional_ira_balance: float,
    nondeductible_basis: float,
    marginal_tax_rate_pct: float = 32.0,
) -> dict[str, Any]:
    """
    Calculate IRS Pro-Rata Rule tax liability for Backdoor or Mega-Backdoor Roth IRA conversions.
    """
    total_traditional_ira_value = pretax_traditional_ira_balance + nondeductible_basis
    if total_traditional_ira_value == 0:
        nondeductible_ratio = 1.0
    else:
        nondeductible_ratio = nondeductible_basis / total_traditional_ira_value

    taxable_ratio = 1.0 - nondeductible_ratio
    tax_free_converted_portion = conversion_amount * nondeductible_ratio
    taxable_converted_portion = conversion_amount * taxable_ratio
    estimated_tax_bill = taxable_converted_portion * (marginal_tax_rate_pct / 100)

    steps = [
        f"Total Traditional IRA Value: ${total_traditional_ira_value:,.2f}",
        f"Nondeductible Basis       : ${nondeductible_basis:,.2f}",
        f"Pro-Rata Non-Taxable Ratio: {nondeductible_ratio * 100:.2f}%",
        f"Pro-Rata Taxable Ratio    : {taxable_ratio * 100:.2f}%",
        f"Conversion Amount         : ${conversion_amount:,.2f}",
        f"Tax-Free Converted Amount : ${tax_free_converted_portion:,.2f}",
        f"Taxable Converted Amount  : ${taxable_converted_portion:,.2f}",
        f"Estimated Tax Liability ({marginal_tax_rate_pct}% bracket): ${estimated_tax_bill:,.2f}",
    ]

    return {
        "total_traditional_ira_value": round(total_traditional_ira_value, 2),
        "tax_free_converted_amount": round(tax_free_converted_portion, 2),
        "taxable_converted_amount": round(taxable_converted_portion, 2),
        "estimated_tax_bill": round(estimated_tax_bill, 2),
        "calculation_steps": "\n".join(steps),
    }


def calculate_real_estate_roi(
    property_price: float,
    down_payment: float,
    monthly_rent: float,
    annual_property_tax: float,
    annual_insurance: float,
    monthly_hoa_maintenance: float,
    vacancy_rate_pct: float = 5.0,
    mortgage_interest_rate_pct: float = 6.5,
    mortgage_term_years: int = 30,
) -> dict[str, Any]:
    """
    Calculate Real Estate Investment metrics: Cap Rate, Net Operating Income (NOI), Cash-on-Cash Return (CoC %), and Net Cash Flow.
    """
    gross_annual_rent = monthly_rent * 12
    effective_gross_income = gross_annual_rent * (1 - vacancy_rate_pct / 100)

    annual_operating_expenses = annual_property_tax + annual_insurance + (monthly_hoa_maintenance * 12)
    noi = effective_gross_income - annual_operating_expenses
    cap_rate_pct = (noi / property_price * 100) if property_price > 0 else 0.0

    # Mortgage calculation
    loan_principal = max(0.0, property_price - down_payment)
    if loan_principal > 0:
        r = mortgage_interest_rate_pct / 100 / 12
        n = mortgage_term_years * 12
        annual_debt_service = (loan_principal * (r * (1 + r)**n) / ((1 + r)**n - 1)) * 12
    else:
        annual_debt_service = 0.0

    annual_cash_flow = noi - annual_debt_service
    monthly_cash_flow = annual_cash_flow / 12

    # Total Cash Invested (down payment + estimated 3% closing costs)
    total_cash_invested = down_payment + (property_price * 0.03)
    cash_on_cash_return_pct = (annual_cash_flow / total_cash_invested * 100) if total_cash_invested > 0 else 0.0

    steps = [
        f"Property Price            : ${property_price:,.2f}",
        f"Down Payment              : ${down_payment:,.2f}",
        f"Gross Annual Rent         : ${gross_annual_rent:,.2f}",
        f"Net Operating Income (NOI): ${noi:,.2f}/yr",
        f"Cap Rate                  : {cap_rate_pct:.2f}%",
        f"Annual Debt Service       : ${annual_debt_service:,.2f}/yr",
        f"Net Annual Cash Flow      : ${annual_cash_flow:,.2f}/yr (${monthly_cash_flow:,.2f}/mo)",
        f"Total Cash Out of Pocket  : ${total_cash_invested:,.2f}",
        f"Cash-on-Cash Return (CoC) : {cash_on_cash_return_pct:.2f}%",
    ]

    return {
        "net_operating_income": round(noi, 2),
        "cap_rate_pct": round(cap_rate_pct, 2),
        "annual_cash_flow": round(annual_cash_flow, 2),
        "monthly_cash_flow": round(monthly_cash_flow, 2),
        "cash_on_cash_return_pct": round(cash_on_cash_return_pct, 2),
        "total_cash_invested": round(total_cash_invested, 2),
        "calculation_steps": "\n".join(steps),
    }


def calculate_tax_efficient_asset_location(
    taxable_account_balance: float,
    tax_deferred_balance: float, # Traditional 401k / IRA
    tax_exempt_balance: float,   # Roth 401k / Roth IRA / HSA
    stock_allocation_pct: float = 80.0,
    bond_allocation_pct: float = 20.0,
) -> dict[str, Any]:
    """
    Recommends optimal asset placement across Taxable, Tax-Deferred, and Tax-Exempt accounts for optimal after-tax wealth accumulation.
    """
    total_portfolio = taxable_account_balance + tax_deferred_balance + tax_exempt_balance
    target_stocks = total_portfolio * (stock_allocation_pct / 100)
    target_bonds = total_portfolio * (bond_allocation_pct / 100)

    # Strategy:
    # 1. High Growth Stocks -> Tax-Exempt (Roth) first, then Taxable (for long-term capital gains rate).
    # 2. Income/Bonds -> Tax-Deferred (Traditional IRA/401k) to avoid annual ordinary income tax on yields.

    steps = [
        f"Total Portfolio Value     : ${total_portfolio:,.2f}",
        f"Target Stocks ({stock_allocation_pct}%) : ${target_stocks:,.2f}",
        f"Target Bonds ({bond_allocation_pct}%)  : ${target_bonds:,.2f}",
        "",
        "─── OPTIMAL ASSET LOCATION STRATEGY ─────────────────────────",
        f"1. Tax-Exempt (Roth/HSA - ${tax_exempt_balance:,.2f}): Put 100% highest growth equities (Index Funds/Tech Stocks). Tax-free growth & withdrawals.",
        f"2. Tax-Deferred (Traditional - ${tax_deferred_balance:,.2f}): Place Bonds (${target_bonds:,.2f}) here to shield interest from ordinary income tax.",
        f"3. Taxable Account (${taxable_account_balance:,.2f}): Place broad-market ETFs (VOO/VTI) for favorable 0%/15%/20% long-term capital gains tax rates & step-up in basis.",
    ]

    return {
        "total_portfolio": round(total_portfolio, 2),
        "target_stocks_dollars": round(target_stocks, 2),
        "target_bonds_dollars": round(target_bonds, 2),
        "calculation_steps": "\n".join(steps),
    }


# ─────────────────────────────────────────────────────────────────────────────
# INDIAN TAX & INVESTMENT CALCULATORS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_indian_income_tax(
    gross_annual_income: float,
    section_80c: float = 150000.0,
    section_80d: float = 25000.0,
    nps_80ccd1b: float = 50000.0,
    hra_exemption: float = 0.0,
) -> dict[str, Any]:
    """
    Compares Indian Income Tax liability under New Tax Regime (FY 2024-25/2025-26) vs Old Tax Regime.
    Recommends the tax-optimal regime and shows explicit step-by-step savings.
    """
    # ── NEW TAX REGIME ──
    std_deduction_new = 75000.0
    taxable_new = max(0.0, gross_annual_income - std_deduction_new)
    
    tax_new = 0.0
    if taxable_new <= 700000:
        # Full Section 87A rebate applies if taxable income <= 7 Lakhs in New Regime
        tax_new = 0.0
    else:
        # Slab breakdown
        rem = taxable_new
        # 0 to 3L -> 0%
        # 3L to 7L (4L@5% = 20,000)
        if rem > 300000:
            tier = min(rem - 300000, 400000)
            tax_new += tier * 0.05
        # 7L to 10L (3L@10% = 30,000)
        if rem > 700000:
            tier = min(rem - 700000, 300000)
            tax_new += tier * 0.10
        # 10L to 12L (2L@15% = 30,000)
        if rem > 1000000:
            tier = min(rem - 1000000, 200000)
            tax_new += tier * 0.15
        # 12L to 15L (3L@20% = 60,000)
        if rem > 1200000:
            tier = min(rem - 1200000, 300000)
            tax_new += tier * 0.20
        # Above 15L @ 30%
        if rem > 1500000:
            tax_new += (rem - 1500000) * 0.30

    cess_new = tax_new * 0.04
    total_tax_new = tax_new + cess_new

    # ── OLD TAX REGIME ──
    std_deduction_old = 50000.0
    total_deductions_old = std_deduction_old + min(150000.0, section_80c) + min(50000.0, section_80d) + min(50000.0, nps_80ccd1b) + hra_exemption
    taxable_old = max(0.0, gross_annual_income - total_deductions_old)

    tax_old = 0.0
    if taxable_old <= 500000:
        tax_old = 0.0
    else:
        rem_old = taxable_old
        if rem_old > 250000:
            tier = min(rem_old - 250000, 250000)
            tax_old += tier * 0.05
        if rem_old > 500000:
            tier = min(rem_old - 500000, 500000)
            tax_old += tier * 0.20
        if rem_old > 1000000:
            tax_old += (rem_old - 1000000) * 0.30

    cess_old = tax_old * 0.04
    total_tax_old = tax_old + cess_old

    recommended_regime = "New Tax Regime" if total_tax_new <= total_tax_old else "Old Tax Regime"
    tax_savings = abs(total_tax_old - total_tax_new)

    steps = [
        f"Gross Annual Income       : ₹{gross_annual_income:,.2f}",
        "",
        "─── NEW TAX REGIME (Budget 2024/2025) ───────────────────────",
        f"Standard Deduction        : ₹{std_deduction_new:,.2f}",
        f"Taxable Income (New)      : ₹{taxable_new:,.2f}",
        f"Base Income Tax           : ₹{tax_new:,.2f}",
        f"Health & Edu Cess (4%)    : ₹{cess_new:,.2f}",
        f"Total Tax (New Regime)    : ₹{total_tax_new:,.2f}",
        "",
        "─── OLD TAX REGIME ──────────────────────────────────────────",
        f"Total Claimed Deductions  : ₹{total_deductions_old:,.2f} (80C, 80D, NPS, HRA, Std Ded)",
        f"Taxable Income (Old)      : ₹{taxable_old:,.2f}",
        f"Base Income Tax           : ₹{tax_old:,.2f}",
        f"Health & Edu Cess (4%)    : ₹{cess_old:,.2f}",
        f"Total Tax (Old Regime)    : ₹{total_tax_old:,.2f}",
        "",
        f"★ RECOMMENDED REGIME       : {recommended_regime.upper()} (Saves ₹{tax_savings:,.2f}/year)",
    ]

    return {
        "gross_annual_income": gross_annual_income,
        "tax_new_regime": round(total_tax_new, 2),
        "tax_old_regime": round(total_tax_old, 2),
        "recommended_regime": recommended_regime,
        "annual_tax_savings": round(tax_savings, 2),
        "calculation_steps": "\n".join(steps),
    }


def calculate_sip_returns(
    monthly_investment: float,
    expected_annual_return_pct: float = 12.0,
    years: int = 15,
    step_up_annual_pct: float = 10.0,
) -> dict[str, Any]:
    """
    Calculates returns for Systematic Investment Plans (SIP) in Mutual Funds/Index Funds with optional annual step-up %.
    Includes LTCG tax estimate under Indian equity tax rules (12.5% on gains exceeding ₹1.25 Lakh).
    """
    total_months = years * 12
    monthly_rate = (expected_annual_return_pct / 100) / 12

    current_monthly_sip = monthly_investment
    total_invested = 0.0
    corpus = 0.0

    yearly_breakdown = []

    for month in range(1, total_months + 1):
        if month > 1 and (month - 1) % 12 == 0 and step_up_annual_pct > 0:
            current_monthly_sip *= (1 + step_up_annual_pct / 100)

        total_invested += current_monthly_sip
        corpus = (corpus + current_monthly_sip) * (1 + monthly_rate)

        if month % 12 == 0:
            year_num = month // 12
            yearly_breakdown.append({
                "year": year_num,
                "monthly_sip": round(current_monthly_sip, 2),
                "total_invested": round(total_invested, 2),
                "future_value": round(corpus, 2),
            })

    total_gains = max(0.0, corpus - total_invested)

    # Indian Equity LTCG Tax: 12.5% on gains over ₹1.25 Lakh
    taxable_ltcg = max(0.0, total_gains - 125000.0)
    estimated_ltcg_tax = taxable_ltcg * 0.125
    post_tax_corpus = corpus - estimated_ltcg_tax

    steps = [
        f"Initial Monthly SIP       : ₹{monthly_investment:,.2f}",
        f"Annual Step-Up            : {step_up_annual_pct}%",
        f"Time Horizon              : {years} years",
        f"Expected Return (CAGR)    : {expected_annual_return_pct}%",
        f"Total Amount Invested     : ₹{total_invested:,.2f}",
        f"Total Capital Gains       : ₹{total_gains:,.2f}",
        f"Estimated Gross Corpus    : ₹{corpus:,.2f}",
        f"Indian LTCG Tax (12.5% >₹1.25L): ₹{estimated_ltcg_tax:,.2f}",
        f"Estimated Post-Tax Value  : ₹{post_tax_corpus:,.2f}",
    ]

    return {
        "total_invested": round(total_invested, 2),
        "total_gains": round(total_gains, 2),
        "gross_corpus": round(corpus, 2),
        "estimated_ltcg_tax": round(estimated_ltcg_tax, 2),
        "post_tax_corpus": round(post_tax_corpus, 2),
        "yearly_breakdown": yearly_breakdown,
        "calculation_steps": "\n".join(steps),
    }


def calculate_indian_capital_gains_tax(
    asset_type: str, # "equity_stocks_mf" | "debt_mf" | "real_estate" | "sgb_gold"
    purchase_price: float,
    sale_price: float,
    holding_period_months: int,
    investor_marginal_tax_rate_pct: float = 30.0,
) -> dict[str, Any]:
    """
    Calculates Capital Gains Tax liability in India across Equity, Debt MFs, Real Estate, and Sovereign Gold Bonds (SGB).
    """
    capital_gains = max(0.0, sale_price - purchase_price)
    asset_type = asset_type.lower()

    tax_rate_pct = 0.0
    tax_amount = 0.0
    is_ltcg = False
    notes = ""

    if "equity" in asset_type:
        is_ltcg = holding_period_months > 12
        if is_ltcg:
            taxable_gain = max(0.0, capital_gains - 125000.0)
            tax_rate_pct = 12.5
            tax_amount = taxable_gain * 0.125
            notes = "Equity LTCG: 12.5% on gains exceeding ₹1.25 Lakh annual exemption."
        else:
            tax_rate_pct = 20.0
            tax_amount = capital_gains * 0.20
            notes = "Equity STCG: Flat 20% on short-term gains (held <= 12 months)."

    elif "debt" in asset_type:
        is_ltcg = holding_period_months > 36
        tax_rate_pct = investor_marginal_tax_rate_pct
        tax_amount = capital_gains * (investor_marginal_tax_rate_pct / 100)
        notes = "Debt Mutual Funds: Taxed at investor's slab rate regardless of holding period (Finance Act 2023 amendment)."

    elif "real_estate" in asset_type:
        is_ltcg = holding_period_months > 24
        if is_ltcg:
            tax_rate_pct = 12.5
            tax_amount = capital_gains * 0.125
            notes = "Real Estate LTCG: Flat 12.5% without indexation (Budget 2024 rule), or Section 54/54F reinvestment exemption."
        else:
            tax_rate_pct = investor_marginal_tax_rate_pct
            tax_amount = capital_gains * (investor_marginal_tax_rate_pct / 100)
            notes = "Real Estate STCG: Added to income and taxed at marginal slab rate."

    elif "sgb" in asset_type or "gold" in asset_type:
        is_ltcg = holding_period_months > 24
        if is_ltcg and holding_period_months >= 96: # 8 years maturity
            tax_rate_pct = 0.0
            tax_amount = 0.0
            notes = "Sovereign Gold Bonds (SGB): 100% TAX-FREE CAPITAL GAINS upon 8-year maturity redemption!"
        elif is_ltcg:
            tax_rate_pct = 12.5
            tax_amount = capital_gains * 0.125
            notes = "Gold LTCG: 12.5% flat tax on gains held > 24 months."
        else:
            tax_rate_pct = investor_marginal_tax_rate_pct
            tax_amount = capital_gains * (investor_marginal_tax_rate_pct / 100)
            notes = "Gold STCG: Taxed at slab rate for holding <= 24 months."

    steps = [
        f"Asset Class               : {asset_type.upper()}",
        f"Holding Period            : {holding_period_months} months ({'LTCG' if is_ltcg else 'STCG'})",
        f"Purchase Price            : ₹{purchase_price:,.2f}",
        f"Sale Price                : ₹{sale_price:,.2f}",
        f"Gross Capital Gains       : ₹{capital_gains:,.2f}",
        f"Effective Tax Rate        : {tax_rate_pct}%",
        f"Estimated Capital Gains Tax: ₹{tax_amount:,.2f}",
        f"Rule Explanation          : {notes}",
    ]

    return {
        "capital_gains": round(capital_gains, 2),
        "is_ltcg": is_ltcg,
        "tax_rate_pct": tax_rate_pct,
        "estimated_tax": round(tax_amount, 2),
        "post_tax_gains": round(capital_gains - tax_amount, 2),
        "rule_notes": notes,
        "calculation_steps": "\n".join(steps),
    }


def calculate_sgb_vs_gold_etf(
    initial_investment: float,
    tenure_years: int = 8,
    expected_gold_cagr_pct: float = 9.0,
) -> dict[str, Any]:
    """
    Compares Sovereign Gold Bonds (SGB) vs Gold ETFs vs Physical Gold over an 8-year horizon.
    Includes 2.5% p.a. SGB simple interest and 100% tax exemption on SGB maturity.
    """
    # 1. Sovereign Gold Bond (SGB)
    sgb_gold_value = initial_investment * ((1 + expected_gold_cagr_pct / 100) ** tenure_years)
    sgb_annual_interest = initial_investment * 0.025
    sgb_total_interest = sgb_annual_interest * tenure_years
    sgb_total_corpus = sgb_gold_value + sgb_total_interest
    sgb_tax = 0.0 # 100% tax-free capital gains at maturity

    # 2. Gold ETF (0.5% annual expense ratio + 12.5% LTCG tax)
    net_etf_return = expected_gold_cagr_pct - 0.5
    etf_gross_value = initial_investment * ((1 + net_etf_return / 100) ** tenure_years)
    etf_gains = max(0.0, etf_gross_value - initial_investment)
    etf_tax = etf_gains * 0.125
    etf_net_corpus = etf_gross_value - etf_tax

    # 3. Physical Gold (3% GST upfront + 12.5% LTCG tax)
    physical_invested = initial_investment * 0.97 # 3% GST lost
    physical_gross = physical_invested * ((1 + expected_gold_cagr_pct / 100) ** tenure_years)
    physical_gains = max(0.0, physical_gross - initial_investment)
    physical_tax = physical_gains * 0.125
    physical_net_corpus = physical_gross - physical_tax

    sgb_outperformance = sgb_total_corpus - etf_net_corpus

    steps = [
        f"Initial Investment        : ₹{initial_investment:,.2f}",
        f"Investment Tenure         : {tenure_years} Years (SGB Maturity)",
        f"Gold CAGR Assumption      : {expected_gold_cagr_pct}% p.a.",
        "",
        "─── 1. SOVEREIGN GOLD BONDS (SGB) ──────────────────────────",
        f"  Gold Asset Appreciation : ₹{sgb_gold_value:,.2f}",
        f"  + 2.5% Annual Interest  : ₹{sgb_total_interest:,.2f} (credited semi-annually)",
        f"  Capital Gains Tax       : ₹0.00 (100% EXEMPT at 8-yr maturity)",
        f"  Total Net SGB Corpus    : ₹{sgb_total_corpus:,.2f}",
        "",
        "─── 2. GOLD ETF / MUTUAL FUND ──────────────────────────────",
        f"  Gross Portfolio (0.5% TER): ₹{etf_gross_value:,.2f}",
        f"  LTCG Tax (12.5%)        : ₹{etf_tax:,.2f}",
        f"  Total Net ETF Corpus    : ₹{etf_net_corpus:,.2f}",
        "",
        "─── 3. PHYSICAL GOLD ───────────────────────────────────────",
        f"  Net Gold (after 3% GST) : ₹{physical_gross:,.2f}",
        f"  LTCG Tax (12.5%)        : ₹{physical_tax:,.2f}",
        f"  Total Net Physical Corpus: ₹{physical_net_corpus:,.2f}",
        "",
        f"★ SGB OUTPERFORMANCE OVER GOLD ETF: +₹{sgb_outperformance:,.2f} due to 2.5% extra yield & 0% tax!",
    ]

    return {
        "sgb_total_corpus": round(sgb_total_corpus, 2),
        "sgb_total_interest_earned": round(sgb_total_interest, 2),
        "etf_net_corpus": round(etf_net_corpus, 2),
        "physical_net_corpus": round(physical_net_corpus, 2),
        "sgb_extra_gain_over_etf": round(sgb_outperformance, 2),
        "calculation_steps": "\n".join(steps),
    }

