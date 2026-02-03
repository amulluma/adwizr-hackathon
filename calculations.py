"""
Retirement Planning Calculation Module
Excel-Wired | Deterministic | FV-based SIP
Based on the authoritative Excel model logic
"""

from dataclasses import dataclass
from typing import List
import math


@dataclass
class RetirementInputs:
    """Input data for retirement planning calculations"""
    current_age: int
    retirement_age: int
    life_expectancy: int = 85
    current_annual_expenses: float = 0  # Normalized to annual
    current_investments: float = 0
    current_annual_income: float = 0  # For context/plausibility only
    risk_profile: str = "moderate"  # conservative, moderate, aggressive
    dependents: str = "self_spouse"  # self_spouse, children, parents, combination, not_sure
    inflation_rate: float = 0.06  # Locked at 6%


@dataclass
class RetirementResult:
    """Output of retirement planning calculations"""
    # Timeline
    current_age: int
    retirement_age: int
    life_expectancy: int
    years_to_retirement: int
    retirement_duration: int

    # Core outputs
    current_annual_expenses: float
    future_annual_expenses: float  # Living expenses at retirement
    corpus_required: float
    future_investment_value: float
    corpus_gap: float
    monthly_savings_required: float
    monthly_savings_rounded: float  # Rounded to clean figure

    # Rates
    expected_return_rate: float
    inflation_rate: float
    risk_profile: str

    # Context
    current_annual_income: float
    dependents: str
    income_expense_flag: bool  # True if expenses > income

    # Assumptions list
    assumptions: List[str]


def get_return_rate(risk_profile: str) -> float:
    """
    Map risk profile to expected annual return rate
    As per system prompt:
    - Conservative → 0.08
    - Balanced / Moderate → 0.12
    - Aggressive → 0.15
    """
    rates = {
        "conservative": 0.08,
        "moderate": 0.12,
        "balanced": 0.12,
        "aggressive": 0.15
    }
    return rates.get(risk_profile.lower(), 0.12)


def calculate_future_value(present_value: float, rate: float, years: int) -> float:
    """
    Calculate future value using compound interest
    FV = PV * (1 + r)^n
    """
    if years <= 0:
        return present_value
    return present_value * ((1 + rate) ** years)


def calculate_corpus_for_retirement(annual_expense_at_retirement: float,
                                    return_rate: float,
                                    inflation_rate: float,
                                    retirement_duration: int) -> float:
    """
    Calculate corpus required at retirement to fund expenses for retirement duration.

    Uses the same return rate as the selected risk profile for discounting
    (as per system prompt R9: use the same return assumption pre- and post-retirement)

    This calculates present value of growing annuity where:
    - First payment = annual_expense_at_retirement
    - Growth rate = inflation_rate (expenses grow with inflation)
    - Discount rate = return_rate (investment returns during retirement)
    - Duration = retirement_duration years
    """
    if retirement_duration <= 0:
        return 0

    # Real rate = (1 + nominal) / (1 + inflation) - 1
    # But we use growing annuity formula directly

    # Present Value of Growing Annuity formula:
    # If return_rate != inflation_rate:
    #   PV = PMT * [1 - ((1+g)/(1+r))^n] / (r - g)
    # If return_rate == inflation_rate:
    #   PV = PMT * n / (1 + r)

    g = inflation_rate  # Growth rate of expenses
    r = return_rate     # Discount rate (investment return)
    n = retirement_duration
    pmt = annual_expense_at_retirement

    if abs(r - g) < 0.0001:  # Effectively equal
        corpus = pmt * n / (1 + r)
    else:
        corpus = pmt * (1 - ((1 + g) / (1 + r)) ** n) / (r - g)

    return max(0, corpus)


def calculate_monthly_sip(future_value: float, annual_rate: float, years: int) -> float:
    """
    Calculate monthly SIP (PMT) required to reach future value
    FV-based SIP formula (constant monthly, no step-ups)

    PMT = FV * [r / ((1+r)^n - 1)]
    where r = monthly rate, n = number of months
    """
    if years <= 0:
        return 0
    if future_value <= 0:
        return 0

    monthly_rate = annual_rate / 12
    months = years * 12

    if monthly_rate == 0:
        return future_value / months

    # PMT for future value annuity
    pmt = future_value * (monthly_rate / (((1 + monthly_rate) ** months) - 1))
    return pmt


def round_to_clean_figure(amount: float, to_nearest: int = 500) -> float:
    """
    Round to a clean, human-readable figure
    Default: nearest ₹500
    For larger amounts (>50000), round to nearest ₹1000
    """
    if amount <= 0:
        return 0

    if amount > 50000:
        to_nearest = 1000

    return round(amount / to_nearest) * to_nearest


def calculate_retirement_plan(inputs: RetirementInputs) -> RetirementResult:
    """
    Main calculation function for retirement planning
    Follows the Excel model as authoritative source

    Steps (as per system prompt):
    R3. Time to save = retirement age − current age
    R4. Years to provide = life expectancy − retirement age
    R8. Living expenses at retirement = annual expenses × (1 + 0.06)^years
    R9. Corpus required using growing annuity with risk-based return
    R10. Future value of existing investments
    R11. Corpus gap = corpus required − future investments
    R13. Monthly savings using FV-based SIP, rounded to clean figure
    """

    # R3: Years to retirement (time to save)
    years_to_retirement = inputs.retirement_age - inputs.current_age

    # R4: Retirement duration (years to provide)
    retirement_duration = inputs.life_expectancy - inputs.retirement_age

    # R12: Get expected return rate based on risk profile
    expected_return = get_return_rate(inputs.risk_profile)

    # R8: Living expenses at retirement (inflated)
    future_annual_expenses = calculate_future_value(
        inputs.current_annual_expenses,
        inputs.inflation_rate,
        years_to_retirement
    )

    # R9: Corpus required (using same return rate for discounting)
    corpus_required = calculate_corpus_for_retirement(
        future_annual_expenses,
        expected_return,
        inputs.inflation_rate,
        retirement_duration
    )

    # R10: Future value of existing investments at retirement
    future_investment_value = calculate_future_value(
        inputs.current_investments,
        expected_return,
        years_to_retirement
    )

    # R11: Corpus gap
    corpus_gap = max(0, corpus_required - future_investment_value)

    # R13: Monthly savings required (FV-based SIP)
    monthly_savings = calculate_monthly_sip(
        corpus_gap,
        expected_return,
        years_to_retirement
    )

    # Round to clean figure
    monthly_savings_rounded = round_to_clean_figure(monthly_savings)

    # Check income vs expenses flag
    income_expense_flag = inputs.current_annual_income > 0 and inputs.current_annual_expenses > inputs.current_annual_income

    # Prepare assumptions list
    assumptions = [
        f"Inflation rate: {inputs.inflation_rate * 100:.0f}% per annum (locked)",
        f"Expected investment return: {expected_return * 100:.0f}% per annum ({inputs.risk_profile} profile)",
        f"Life expectancy: {inputs.life_expectancy} years",
        f"Same return rate ({expected_return * 100:.0f}%) applied pre- and post-retirement",
        "Constant monthly SIP (no step-ups)",
        "No tax implications considered",
        "No product or fund recommendations included",
        "Figures are planning-level estimates, not precise forecasts"
    ]

    return RetirementResult(
        current_age=inputs.current_age,
        retirement_age=inputs.retirement_age,
        life_expectancy=inputs.life_expectancy,
        years_to_retirement=years_to_retirement,
        retirement_duration=retirement_duration,
        current_annual_expenses=inputs.current_annual_expenses,
        future_annual_expenses=future_annual_expenses,
        corpus_required=corpus_required,
        future_investment_value=future_investment_value,
        corpus_gap=corpus_gap,
        monthly_savings_required=monthly_savings,
        monthly_savings_rounded=monthly_savings_rounded,
        expected_return_rate=expected_return,
        inflation_rate=inputs.inflation_rate,
        risk_profile=inputs.risk_profile,
        current_annual_income=inputs.current_annual_income,
        dependents=inputs.dependents,
        income_expense_flag=income_expense_flag,
        assumptions=assumptions
    )


def calculate_whatif_scenario(base_inputs: RetirementInputs,
                               new_retirement_age: int) -> RetirementResult:
    """
    Calculate what-if scenario with different retirement age
    Only changes retirement age, all other assumptions remain identical
    """
    whatif_inputs = RetirementInputs(
        current_age=base_inputs.current_age,
        retirement_age=new_retirement_age,
        life_expectancy=base_inputs.life_expectancy,
        current_annual_expenses=base_inputs.current_annual_expenses,
        current_investments=base_inputs.current_investments,
        current_annual_income=base_inputs.current_annual_income,
        risk_profile=base_inputs.risk_profile,
        dependents=base_inputs.dependents,
        inflation_rate=base_inputs.inflation_rate
    )
    return calculate_retirement_plan(whatif_inputs)


def format_currency(amount: float, currency_symbol: str = "₹") -> str:
    """Format amount as Indian currency with lakhs/crores notation"""
    if amount >= 10000000:  # 1 crore
        return f"{currency_symbol}{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 lakh
        return f"{currency_symbol}{amount/100000:.2f} L"
    else:
        return f"{currency_symbol}{amount:,.0f}"


def format_result_summary(result: RetirementResult) -> dict:
    """Format the result for display"""
    return {
        "current_age": result.current_age,
        "retirement_age": result.retirement_age,
        "life_expectancy": result.life_expectancy,
        "years_to_retirement": result.years_to_retirement,
        "retirement_duration": result.retirement_duration,
        "current_annual_expenses": format_currency(result.current_annual_expenses),
        "future_annual_expenses": format_currency(result.future_annual_expenses),
        "corpus_required": format_currency(result.corpus_required),
        "corpus_required_raw": result.corpus_required,
        "current_investments_at_retirement": format_currency(result.future_investment_value),
        "corpus_gap": format_currency(result.corpus_gap),
        "corpus_gap_raw": result.corpus_gap,
        "monthly_sip_required": format_currency(result.monthly_savings_rounded),
        "monthly_sip_raw": result.monthly_savings_rounded,
        "monthly_sip_exact": result.monthly_savings_required,
        "expected_return": f"{result.expected_return_rate * 100:.0f}%",
        "inflation_rate": f"{result.inflation_rate * 100:.0f}%",
        "risk_profile": result.risk_profile.capitalize(),
        "dependents": result.dependents,
        "income_expense_flag": result.income_expense_flag,
        "current_annual_income": format_currency(result.current_annual_income) if result.current_annual_income > 0 else "Not provided",
        "assumptions": result.assumptions
    }


def generate_excel_plan(result: RetirementResult, inputs: RetirementInputs) -> bytes:
    """
    Generate downloadable Excel file with editable numbers for what-if scenarios
    """
    try:
        import pandas as pd
        from io import BytesIO

        # Create Excel writer
        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Inputs (Editable)
            inputs_data = {
                'Parameter': [
                    'Current Age',
                    'Retirement Age',
                    'Life Expectancy',
                    'Current Annual Expenses (₹)',
                    'Current Investments (₹)',
                    'Current Annual Income (₹)',
                    'Risk Profile',
                    'Inflation Rate (%)',
                    'Expected Return Rate (%)'
                ],
                'Value': [
                    inputs.current_age,
                    inputs.retirement_age,
                    inputs.life_expectancy,
                    inputs.current_annual_expenses,
                    inputs.current_investments,
                    inputs.current_annual_income,
                    inputs.risk_profile.capitalize(),
                    inputs.inflation_rate * 100,
                    result.expected_return_rate * 100
                ],
                'Notes': [
                    'Your current age',
                    'Target retirement age (55-65 recommended)',
                    'How long savings should last (default: 85)',
                    'Your current yearly expenses',
                    'Total retirement savings you have now',
                    'Your current yearly income (for reference)',
                    'Conservative (8%), Moderate (12%), Aggressive (15%)',
                    'Locked at 6% per annum',
                    'Based on risk profile selected'
                ]
            }
            df_inputs = pd.DataFrame(inputs_data)
            df_inputs.to_excel(writer, sheet_name='Inputs', index=False)

            # Sheet 2: Calculations
            calc_data = {
                'Calculation Step': [
                    'Years to Retirement',
                    'Retirement Duration (Years)',
                    'Living Expenses at Retirement (₹)',
                    'Corpus Required (₹)',
                    'Future Value of Current Investments (₹)',
                    'Corpus Gap (₹)',
                    'Monthly SIP Required (₹)',
                    'Monthly SIP Rounded (₹)'
                ],
                'Value': [
                    result.years_to_retirement,
                    result.retirement_duration,
                    round(result.future_annual_expenses, 0),
                    round(result.corpus_required, 0),
                    round(result.future_investment_value, 0),
                    round(result.corpus_gap, 0),
                    round(result.monthly_savings_required, 0),
                    result.monthly_savings_rounded
                ],
                'Formula': [
                    'Retirement Age - Current Age',
                    'Life Expectancy - Retirement Age',
                    'Annual Expenses × (1 + Inflation)^Years',
                    'PV of Growing Annuity',
                    'Current Investments × (1 + Return)^Years',
                    'Corpus Required - Future Investments',
                    'FV-based SIP formula',
                    'Rounded to nearest ₹500/₹1000'
                ]
            }
            df_calc = pd.DataFrame(calc_data)
            df_calc.to_excel(writer, sheet_name='Calculations', index=False)

            # Sheet 3: What-If Scenarios
            whatif_ages = [55, 58, 60, 62, 65]
            whatif_data = []

            for age in whatif_ages:
                if age > inputs.current_age:
                    scenario = calculate_whatif_scenario(inputs, age)
                    whatif_data.append({
                        'Retirement Age': age,
                        'Years to Retirement': scenario.years_to_retirement,
                        'Retirement Duration': scenario.retirement_duration,
                        'Corpus Required (₹)': round(scenario.corpus_required, 0),
                        'Monthly SIP Required (₹)': scenario.monthly_savings_rounded
                    })

            if whatif_data:
                df_whatif = pd.DataFrame(whatif_data)
                df_whatif.to_excel(writer, sheet_name='What-If Scenarios', index=False)

            # Sheet 4: Assumptions & Disclaimers
            assumptions_data = {
                'Category': ['Assumption'] * len(result.assumptions) + ['Disclaimer'] * 4,
                'Description': result.assumptions + [
                    'This plan is for educational guidance only',
                    'Investments are subject to market risk',
                    'Projections are assumption-based estimates',
                    'Periodic review and adjustment is advised'
                ]
            }
            df_assumptions = pd.DataFrame(assumptions_data)
            df_assumptions.to_excel(writer, sheet_name='Assumptions & Disclaimers', index=False)

        return output.getvalue()

    except ImportError:
        # If pandas/openpyxl not available, return None
        return None


# Test the calculations
if __name__ == "__main__":
    # Example: 35 year old wants to retire at 60
    test_inputs = RetirementInputs(
        current_age=35,
        retirement_age=60,
        life_expectancy=85,
        current_annual_expenses=600000,  # Rs. 50,000/month = 6L/year
        current_investments=500000,       # Rs. 5 lakhs
        current_annual_income=1200000,    # Rs. 12L/year
        risk_profile="moderate",
        dependents="self_spouse",
        inflation_rate=0.06
    )

    result = calculate_retirement_plan(test_inputs)
    summary = format_result_summary(result)

    # Use Rs. instead of rupee symbol for terminal compatibility
    print("\n=== RETIREMENT PLAN SUMMARY ===")
    print(f"Current Age: {summary['current_age']} years")
    print(f"Retirement Age: {summary['retirement_age']} years")
    print(f"Years to Retirement: {summary['years_to_retirement']} years")
    print(f"Retirement Duration: {summary['retirement_duration']} years")
    print(f"\n--- Authoritative Numbers ---")
    print(f"Current Annual Expenses: Rs. {result.current_annual_expenses:,.0f}")
    print(f"Living Expenses at Retirement: Rs. {result.future_annual_expenses:,.0f}")
    print(f"Corpus Required: Rs. {result.corpus_required:,.0f}")
    print(f"Current Investments at Retirement: Rs. {result.future_investment_value:,.0f}")
    print(f"Corpus Gap: Rs. {result.corpus_gap:,.0f}")
    print(f"Monthly SIP Required (exact): Rs. {result.monthly_savings_required:,.0f}")
    print(f"Monthly SIP Required (rounded): Rs. {result.monthly_savings_rounded:,.0f}")
    print(f"\nAssumptions:")
    for assumption in summary['assumptions']:
        print(f"  - {assumption}")

    # Test what-if
    print("\n=== WHAT-IF: Retire at 58 ===")
    whatif = calculate_whatif_scenario(test_inputs, 58)
    print(f"Monthly SIP Required: Rs. {whatif.monthly_savings_rounded:,.0f}")
