# AI Financial Advisor Agent

An agentic AI financial planning assistant powered by **Google Gemini** (`gemini-3.8-flash`) with streaming responses, stateful multi-turn conversation, and seven built-in financial calculation tools via function-calling.

---

## Features

| Capability | Details |
|---|---|
| **Stateful conversation** | Remembers your financial context across the full session |
| **Streaming responses** | Words appear as they're generated — no waiting |
| **7 financial tools** | Budget, emergency fund, debt payoff, investments, retirement, loans, net worth |
| **Agentic workflow** | Proactively asks for missing data before computing |
| **Scenario simulation** | Automatically compares avalanche vs snowball, 15yr vs 30yr mortgage, etc. |
| **Transparent math** | Shows every calculation step so you can verify the logic |

---

## Project Structure

```
financial advisor agent/
├── agent.py            # Main entry point — REPL + Gemini Interactions API loop
├── financial_tools.py  # Pure-math financial calculators (no AI)
├── tool_schemas.py     # JSON-schema tool declarations for Gemini function-calling
├── requirements.txt    # Python dependencies
├── .env.example        # Template — copy to .env and add your API key
└── README.md
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your Gemini API key

```bash
copy .env.example .env
# Then edit .env and replace 'your_api_key_here' with your actual key
```

Get a free API key at [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).

### 3. Run the agent

```bash
python agent.py
```

---

## Example Interactions

### Budget Analysis
```
You ▶ I earn $5,500/month net. I spend $1,400 rent, $500 food, $300 car,
       $150 utilities, $200 subscriptions, $400 dining out.
```
The agent calls `analyze_budget` → shows 50/30/20 breakdown, savings rate, and surplus.

### Debt Payoff Comparison
```
You ▶ I have a $12,000 Visa at 22% APR ($240 min) and a $6,000 car loan
       at 8% APR ($180 min). I can pay $500 extra. Which strategy is faster?
```
The agent calls `calculate_debt_payoff` twice (avalanche + snowball) and presents a comparison table.

### Retirement Check
```
You ▶ I'm 32, want to retire at 60. I have $45,000 saved, contribute $600/month.
       I want $70,000/year in retirement. Am I on track?
```
The agent calls `calculate_retirement_plan` → shows corpus, shortfall, and exact monthly increase needed.

---

## Available Financial Tools

| Tool | What It Calculates |
|---|---|
| `analyze_budget` | 50/30/20 breakdown, surplus/deficit, savings rate |
| `calculate_emergency_fund` | Target, gap, and months-to-goal |
| `calculate_debt_payoff` | Avalanche or snowball payoff timeline + total interest |
| `calculate_investment_growth` | Compound growth with contributions, real vs nominal FV |
| `calculate_retirement_plan` | Corpus projection, shortfall, 4% SWR analysis |
| `calculate_loan` | Monthly payment, amortisation, extra-payment impact |
| `calculate_net_worth` | Total assets, liabilities, net worth, debt-to-asset ratio |

---

## Session Commands

| Command | Action |
|---|---|
| `new` | Reset conversation (start fresh) |
| `quit` / `exit` | End session |

---

## Disclaimer

> This agent provides **educational financial models and frameworks**. It is not a certified financial planner or tax advisor. Always verify specific tax or legal implications with a licensed professional.
