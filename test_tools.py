from financial_tools import analyze_budget, calculate_debt_payoff, calculate_retirement_plan

# Test 1: Budget
r = analyze_budget(5500, {"rent":1400,"food":500,"car":300,"utilities":150,"dining":400})
print("Budget surplus:", r["surplus"], "| Savings rate:", r["savings_rate_pct"], "%")

# Test 2: Debt payoff
debts = [{"name":"Visa","balance":12000,"apr":22,"min_payment":240},
         {"name":"CarLoan","balance":6000,"apr":8,"min_payment":180}]
av = calculate_debt_payoff(debts, extra_payment=500, strategy="avalanche")
sn = calculate_debt_payoff(debts, extra_payment=500, strategy="snowball")
print(f"Avalanche: {av['months_to_payoff']}mo, interest={av['total_interest_paid']}")
print(f"Snowball : {sn['months_to_payoff']}mo, interest={sn['total_interest_paid']}")

# Test 3: Retirement
r = calculate_retirement_plan(32, 60, 45000, 600, 7, 70000)
print("On track:", r["is_on_track"], "| Corpus:", r["projected_corpus"], "| Needed:", r["required_corpus"])

print("\nAll tests PASSED!")
