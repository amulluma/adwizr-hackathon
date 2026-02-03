"""
Goal Planning Assistant - Retirement Planning
Excel-Wired | Conversation-Driven | Deterministic
Streamlit UI with GPT-4o Integration
"""

import streamlit as st
from openai import OpenAI
import json
import re
import os
from dotenv import load_dotenv
from calculations import (
    RetirementInputs,
    RetirementResult,
    calculate_retirement_plan,
    calculate_whatif_scenario,
    format_result_summary,
    format_currency,
    generate_excel_plan
)

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Goal Planning Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Color palette from template
# Accent: #D1A36C (golden/tan)
# Gray: #8B8D98
# Background: #111111 (dark)
# Light backgrounds for cards: #1a1a1a, #222222
# Text on dark: #E8E8E8, #FFFFFF

# Custom CSS for dark theme UI
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #111111;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: #E8E8E8;
    }

    /* Logo container */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    .logo-container img {
        max-height: 80px;
        width: auto;
    }

    /* Headers */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #D1A36C;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #8B8D98;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #D1A36C;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #D1A36C;
        padding-bottom: 0.3rem;
    }

    /* Metric cards - golden accent */
    .metric-card {
        background: linear-gradient(135deg, #2a2520 0%, #1a1815 100%);
        border: 1px solid #D1A36C;
        padding: 1.5rem;
        border-radius: 12px;
        color: #FFFFFF;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #D1A36C;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #E8E8E8;
        opacity: 0.9;
    }

    /* Green highlight card for main result */
    .metric-card-highlight {
        background: linear-gradient(135deg, #1a2a1a 0%, #152015 100%);
        border: 1px solid #4a7c4a;
        padding: 1.5rem;
        border-radius: 12px;
        color: #FFFFFF;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-card-highlight .metric-value {
        color: #6abf6a;
    }

    /* Info box - dark with gold border */
    .info-box {
        background: #1a1a1a;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #D1A36C;
        margin: 0.5rem 0;
        color: #E8E8E8;
    }
    .info-box strong {
        color: #D1A36C;
    }

    /* Assumption box - dark with gray accent */
    .assumption-box {
        background: #1a1a1a;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #8B8D98;
        margin: 0.5rem 0;
        color: #E8E8E8;
    }

    /* Disclaimer box - dark with amber warning */
    .disclaimer-box {
        background: #2a2515;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #D1A36C;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #E8E8E8;
    }
    .disclaimer-box strong {
        color: #D1A36C;
    }

    /* Next steps box - dark with muted green */
    .next-steps-box {
        background: #1a2a1a;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #6abf6a;
        margin: 1rem 0;
        color: #E8E8E8;
    }
    .next-steps-box strong {
        color: #6abf6a;
    }

    /* Warning box - dark with red accent */
    .warning-box {
        background: #2a1a1a;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #bf6a6a;
        margin: 1rem 0;
        color: #E8E8E8;
    }
    .warning-box strong {
        color: #bf6a6a;
    }

    /* What-if cards */
    .whatif-card {
        background: #1a1a1a;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #8B8D98;
        margin: 0.5rem 0;
        color: #E8E8E8;
    }
    .whatif-card strong {
        color: #D1A36C;
    }
    .whatif-card-base {
        background: #1a2a1a;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #6abf6a;
        margin: 0.5rem 0;
        color: #E8E8E8;
    }
    .whatif-card-base strong {
        color: #6abf6a;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background-color: #1a1a1a;
        border: 1px solid #333333;
    }

    /* Chat input container */
    [data-testid="stChatInput"] {
        background-color: #1a1a1a !important;
    }

    /* Chat input text area */
    [data-testid="stChatInput"] textarea {
        background-color: #222222 !important;
        color: #E8E8E8 !important;
        border: 1px solid #8B8D98 !important;
        border-radius: 8px !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #D1A36C !important;
        box-shadow: 0 0 0 1px #D1A36C !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #8B8D98 !important;
    }

    /* Chat input submit button */
    [data-testid="stChatInput"] button {
        background-color: #D1A36C !important;
        color: #111111 !important;
    }
    [data-testid="stChatInput"] button:hover {
        background-color: #b8905d !important;
    }

    /* Bottom chat input container styling */
    .stChatInput {
        background-color: #111111 !important;
    }
    [data-testid="stBottom"] {
        background-color: #111111 !important;
    }
    [data-testid="stBottomBlockContainer"] {
        background-color: #111111 !important;
    }

    /* Input fields */
    .stTextInput input, .stNumberInput input {
        background-color: #222222;
        color: #E8E8E8;
        border: 1px solid #8B8D98;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #D1A36C;
    }

    /* Buttons */
    .stButton button {
        background-color: #D1A36C;
        color: #111111;
        border: none;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #b8905d;
        color: #111111;
    }

    /* Download button */
    .stDownloadButton button {
        background-color: #D1A36C;
        color: #111111;
        border: none;
        font-weight: bold;
    }

    /* Info/Warning/Success messages */
    .stAlert {
        background-color: #1a1a1a;
        color: #E8E8E8;
    }

    /* Markdown text */
    .stMarkdown {
        color: #E8E8E8;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #D1A36C;
    }
    [data-testid="stMetricLabel"] {
        color: #8B8D98;
    }

    /* Horizontal rule */
    hr {
        border-color: #333333;
    }

    /* Caption text */
    .stCaption {
        color: #8B8D98;
    }
</style>
""", unsafe_allow_html=True)

# System prompt based on the updated specification
SYSTEM_PROMPT = """
# SYSTEM PROMPT

**Goal Planning Assistant (Retirement Only)**
**Excel-Wired | Conversation-Driven | Deterministic**

---

## 1. ROLE & OBJECTIVE

You are a **goal-based financial planning assistant**.

Your purpose is to:

1. Conduct a **structured, multi-turn conversation** to collect *all materially relevant inputs*
2. Ensure **no hidden assumptions** are made
3. Use the **attached Excel model as the single source of calculation truth**
4. Produce:
   * future cost / corpus required
   * monthly savings (SIP-style) required
5. Clearly explain:
   * *why* this number exists
   * *which assumptions* were used
6. Include **explicit guardrails and disclaimers**

You are **not**:
* a product recommender
* a tax advisor
* a portfolio constructor

---

## 2. NON-NEGOTIABLE GLOBAL RULES

1. Handle **one goal per session**
2. **Conversation first, calculation last**
3. Ask **one question per turn**
4. Make **no silent assumptions**
5. Allow "I don't know" → apply safe default + disclose
6. Follow **Excel model as authoritative**
7. Use **FV-based SIP only** (constant monthly, no step-ups)
8. Keep outputs **planning-level**, not precise forecasts
9. **Normalize all monetary inputs to annual values** before calculation
10. If **current living expenses exceed current income**, explicitly flag this in the explanation and state that the plan assumes future normalization of income and/or expenses, **without recomputing numbers**
11. Round final monthly savings outputs to a **clean, human-readable figure** (e.g., nearest ₹500 or ₹1,000)

---

## 3. SUPPORTED GOAL

* Retirement Planning

---

## 4. TOP-LEVEL CONVERSATION FLOW

Start → Retirement Planning Flow

---

# 🧠 5. RETIREMENT PLANNING — FULL CONVERSATION LOGIC

### R1. Current Age
* Ask for current age or DOB
* If DOB is provided, compute age

### R2. Retirement Age
* Ask desired retirement age
* Suggest a **retirement age range of 55–65** (based on current trends or if the user would like to work longer)
* Validate: retirement age > current age

### R3. Time to Save (Derived)
retirement age − current age

### R4. Life Expectancy / Retirement Duration
* Ask till what age retirement savings should last
* If unknown, default to **85** and disclose
years to provide = life expectancy − retirement age

### R5. Dependents During Retirement
Ask who will be financially supported:
* Self / spouse only
* Children
* Parents
* Combination
* Not sure

### R6. Current Living Expenses (Mandatory)
* Ask current living expenses
* **Explicitly confirm whether the value is monthly or annual**
* Normalize internally to **annual**
* Do not ask for line items

### R7. Inflation for Living Expenses (Locked)
living expense inflation = 0.06

### R8. Living Expenses at Retirement (Authoritative Derived Output)
current annual living expenses × (1 + 0.06) ^ (time to retirement)

### R9. Retirement Corpus Required (Authoritative Output)
* Treat "corpus required" from Excel logic as final target
* Use living expenses at retirement + years to provide
* If retirement cashflows are discounted, **use the same return rate as the selected risk profile**
* Explicitly disclose that **the same return assumption is applied pre- and post-retirement**, unless the Excel model specifies otherwise

### R10. Existing Investment Portfolio (Mandatory)
* Ask for the **total current investment portfolio value**
* Treat this as **existing retirement savings**
* Zero allowed

### R11. Corpus Gap (Derived)
corpus required − existing investment portfolio

### R12. Risk Profile (Mandatory Selector)
* Conservative → 0.08
* Balanced / Moderate → 0.12
* Aggressive → 0.15

### R13. Monthly Savings Required (Authoritative Output)
* Use FV-based SIP
* Inputs: corpus gap, time to save (months), selected return
* Output must align with Excel "Monthly Savings required"
* Round output to a clean, human-readable figure

### R14. Current Income (Context Only)
* Ask approximate income (monthly or annual)
* Normalize internally to annual
* Use only for plausibility checks and explanation

---

## IMPORTANT: DATA COLLECTION COMPLETION

When you have collected ALL the following inputs, output CALCULATION_READY followed by a JSON block:
1. current_age (number)
2. retirement_age (number)
3. life_expectancy (number, default 85)
4. current_annual_expenses (number - normalized to annual)
5. current_investments (number)
6. current_annual_income (number - normalized to annual)
7. risk_profile (string: conservative, moderate, or aggressive)
8. dependents (string: self_spouse, children, parents, combination, not_sure)

Format when ALL data collected:
CALCULATION_READY
```json
{
    "current_age": <number>,
    "retirement_age": <number>,
    "life_expectancy": <number>,
    "current_annual_expenses": <number>,
    "current_investments": <number>,
    "current_annual_income": <number>,
    "risk_profile": "<conservative|moderate|aggressive>",
    "dependents": "<self_spouse|children|parents|combination|not_sure>"
}
```

---

## TONE & BEHAVIOR
- Warm, professional, and trustworthy
- No sales language or product recommendations
- Empathetic to financial concerns
- Clear and jargon-free explanations
- Patient with unclear answers

## IMPORTANT NOTES:
- Do NOT provide the final calculation - just collect the data
- When you have ALL required inputs, output CALCULATION_READY with the JSON
- If user provides ambiguous data, ask for clarification
- Convert any "lakhs" or "crores" mentioned to actual numbers (1 lakh = 100000, 1 crore = 10000000)
- Always confirm if expense/income values are monthly or annual before normalizing
- Each new conversation is a new user - do not assume any prior context
"""

# What-if system prompt addition
WHATIF_SYSTEM_PROMPT = """
You are helping with what-if scenario analysis for a retirement plan.

The base plan has been calculated. The user is asking about alternative scenarios.

WHAT-IF RULES:
1. Only change ONE variable per scenario (typically retirement age)
2. All other assumptions remain identical to the base plan
3. Clearly label results as "What-if comparison"
4. Maximum 3 what-if scenarios per response
5. No optimization language ("best", "ideal", "optimal")
6. No product recommendations

When user asks what-if questions like:
- "What if I retire at 58?"
- "What if I delay retirement?"

Respond with a comparison format and explain WHY the numbers changed.

Include this disclosure:
> These what-if scenarios are illustrative comparisons based on the same assumptions as your base plan.
> They are meant to show directional impact, not to replace the original plan.
"""


def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "calculation_done" not in st.session_state:
        st.session_state.calculation_done = False

    if "result" not in st.session_state:
        st.session_state.result = None

    if "inputs" not in st.session_state:
        st.session_state.inputs = None

    if "collected_data" not in st.session_state:
        st.session_state.collected_data = None

    if "openai_client" not in st.session_state:
        st.session_state.openai_client = None

    if "whatif_mode" not in st.session_state:
        st.session_state.whatif_mode = False

    if "followup_messages" not in st.session_state:
        st.session_state.followup_messages = []


def get_openai_client():
    """Get or create OpenAI client from environment variable"""
    if st.session_state.openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            st.session_state.openai_client = OpenAI(api_key=api_key)
    return st.session_state.openai_client


def chat_with_gpt(messages: list, system_prompt: str = SYSTEM_PROMPT) -> str:
    """Send messages to GPT-4o and get response"""
    client = get_openai_client()
    if not client:
        return "Error: OpenAI API key not found. Please add OPENAI_API_KEY to your .env file."

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}] + messages,
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error communicating with GPT-4o: {str(e)}"


def extract_calculation_data(response: str) -> dict:
    """Extract JSON data from CALCULATION_READY response"""
    if "CALCULATION_READY" not in response:
        return None

    # Find JSON in the response
    json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find JSON without code blocks
    json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def perform_calculation(data: dict):
    """Perform retirement calculation with collected data"""
    inputs = RetirementInputs(
        current_age=int(data.get("current_age", 30)),
        retirement_age=int(data.get("retirement_age", 60)),
        life_expectancy=int(data.get("life_expectancy", 85)),
        current_annual_expenses=float(data.get("current_annual_expenses", 600000)),
        current_investments=float(data.get("current_investments", 0)),
        current_annual_income=float(data.get("current_annual_income", 0)),
        risk_profile=data.get("risk_profile", "moderate").lower(),
        dependents=data.get("dependents", "self_spouse"),
        inflation_rate=0.06  # Locked at 6%
    )

    result = calculate_retirement_plan(inputs)
    return result, inputs


# Follow-up chat system prompt
FOLLOWUP_SYSTEM_PROMPT = """
You are a helpful retirement planning assistant. The user has already completed their retirement plan and now has follow-up questions.

## CONTEXT - USER'S RETIREMENT PLAN
{plan_context}

## YOUR ROLE
1. Answer questions about the retirement plan results
2. Explain calculations and assumptions in simple terms
3. Handle what-if scenario questions (e.g., "What if I retire at 58?")
4. Provide general retirement planning guidance
5. Be transparent about limitations

## WHAT-IF SCENARIO HANDLING
When users ask what-if questions about retirement age:
- Calculate the new scenario using the same assumptions
- Present comparison: Base Plan vs What-If
- Explain why the numbers changed
- Use this format:

**Base Plan (Retire at {base_age}):**
- Monthly SIP: {base_sip}

**What-if: Retire at {new_age}:**
- Monthly SIP: {new_sip}
- Difference: {difference}
- Reason: [Shorter/Longer] accumulation period

## RULES
1. Stay focused on the user's specific plan
2. Don't recommend specific products or funds
3. Always mention that these are estimates based on assumptions
4. If asked about complex tax/legal matters, suggest consulting a professional
5. Be helpful, clear, and concise

## AVAILABLE DATA
You have access to all the plan details shown in the context above. Use specific numbers when answering questions.
"""


def get_plan_context(result: RetirementResult, inputs: RetirementInputs) -> str:
    """Generate context string for follow-up chat"""
    return f"""
RETIREMENT PLAN DETAILS:
- Current Age: {result.current_age} years
- Retirement Age: {result.retirement_age} years
- Life Expectancy: {result.life_expectancy} years
- Years to Retirement: {result.years_to_retirement} years
- Retirement Duration: {result.retirement_duration} years
- Risk Profile: {result.risk_profile.capitalize()}

FINANCIAL DETAILS:
- Current Annual Expenses: {format_currency(result.current_annual_expenses)}
- Current Annual Income: {format_currency(result.current_annual_income) if result.current_annual_income > 0 else 'Not provided'}
- Current Investments: {format_currency(inputs.current_investments)}
- Living Expenses at Retirement: {format_currency(result.future_annual_expenses)}/year
- Corpus Required: {format_currency(result.corpus_required)}
- Future Value of Current Investments: {format_currency(result.future_investment_value)}
- Corpus Gap: {format_currency(result.corpus_gap)}
- Monthly SIP Required: {format_currency(result.monthly_savings_rounded)}

ASSUMPTIONS:
- Inflation Rate: {result.inflation_rate * 100:.0f}% per annum
- Expected Return Rate: {result.expected_return_rate * 100:.0f}% per annum
- Same return rate applied pre- and post-retirement
- Constant monthly SIP (no step-ups)
"""


def chat_followup(user_message: str, result: RetirementResult, inputs: RetirementInputs) -> str:
    """Handle follow-up chat questions about the retirement plan"""
    client = get_openai_client()
    if not client:
        return "Error: OpenAI API key not found."

    # Build context-aware system prompt
    plan_context = get_plan_context(result, inputs)
    system_prompt = FOLLOWUP_SYSTEM_PROMPT.format(
        plan_context=plan_context,
        base_age=result.retirement_age,
        base_sip=format_currency(result.monthly_savings_rounded),
        new_age="{user_specified_age}",
        new_sip="{calculated_sip}",
        difference="{calculated_difference}"
    )

    # Check if user is asking about a specific retirement age
    age_match = re.search(r'retire\s*(?:at|when|by)?\s*(\d{2})', user_message.lower())
    if age_match:
        new_age = int(age_match.group(1))
        if new_age > inputs.current_age and new_age != result.retirement_age:
            whatif_result = calculate_whatif_scenario(inputs, new_age)
            diff = whatif_result.monthly_savings_rounded - result.monthly_savings_rounded
            diff_sign = "+" if diff > 0 else ""
            reason = "shorter accumulation period and longer retirement" if new_age < result.retirement_age else "longer accumulation period and shorter retirement"

            whatif_info = f"""

WHAT-IF CALCULATION RESULT:
- New Retirement Age: {new_age}
- New Monthly SIP Required: {format_currency(whatif_result.monthly_savings_rounded)}
- Difference from Base Plan: {diff_sign}{format_currency(abs(diff))}
- New Corpus Required: {format_currency(whatif_result.corpus_required)}
- Reason: {reason}
"""
            system_prompt += whatif_info

    # Build messages for API call
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history
    for msg in st.session_state.followup_messages:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def display_goal_summary(result: RetirementResult, inputs: RetirementInputs):
    """Section A: Goal Summary"""
    st.markdown('<p class="section-header">A. Goal Summary</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="info-box">
            <strong>Goal Type:</strong> Retirement Planning<br>
            <strong>Current Age:</strong> {result.current_age} years<br>
            <strong>Retirement Age:</strong> {result.retirement_age} years
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="info-box">
            <strong>Years to Retirement:</strong> {result.years_to_retirement} years<br>
            <strong>Retirement Duration:</strong> {result.retirement_duration} years<br>
            <strong>Life Expectancy:</strong> {result.life_expectancy} years
        </div>
        """, unsafe_allow_html=True)

    with col3:
        dependents_display = {
            "self_spouse": "Self / Spouse",
            "children": "Children",
            "parents": "Parents",
            "combination": "Combination",
            "not_sure": "Not specified"
        }
        st.markdown(f"""
        <div class="info-box">
            <strong>Risk Profile:</strong> {result.risk_profile.capitalize()}<br>
            <strong>Dependents:</strong> {dependents_display.get(result.dependents, result.dependents)}<br>
            <strong>Expected Return:</strong> {result.expected_return_rate * 100:.0f}% p.a.
        </div>
        """, unsafe_allow_html=True)


def display_authoritative_numbers(result: RetirementResult):
    """Section B: Authoritative Numbers"""
    st.markdown('<p class="section-header">B. Authoritative Numbers</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Living Expenses at Retirement</div>
            <div class="metric-value">{format_currency(result.future_annual_expenses)}/year</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Corpus Gap</div>
            <div class="metric-value">{format_currency(result.corpus_gap)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Corpus Required</div>
            <div class="metric-value">{format_currency(result.corpus_required)}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card-highlight">
            <div class="metric-label">Monthly SIP Required</div>
            <div class="metric-value">{format_currency(result.monthly_savings_rounded)}</div>
        </div>
        """, unsafe_allow_html=True)


def display_explanation(result: RetirementResult, inputs: RetirementInputs):
    """Section C: Explanation"""
    st.markdown('<p class="section-header">C. Why This Monthly Amount?</p>', unsafe_allow_html=True)

    explanation_parts = [
        f"**Time Horizon:** You have {result.years_to_retirement} years until retirement at age {result.retirement_age}.",
        f"**Inflation Impact:** Your current annual expenses of {format_currency(result.current_annual_expenses)} will grow to {format_currency(result.future_annual_expenses)} at retirement (6% inflation).",
        f"**Expense Escalation:** During {result.retirement_duration} years of retirement, expenses continue to rise with inflation.",
        f"**Return Assumption:** Based on your {result.risk_profile} risk profile, we assume {result.expected_return_rate * 100:.0f}% annual returns both before and after retirement.",
        f"**FV-based SIP Logic:** To accumulate the corpus gap of {format_currency(result.corpus_gap)}, you need to invest {format_currency(result.monthly_savings_rounded)} monthly using a constant SIP approach."
    ]

    for part in explanation_parts:
        st.markdown(f"- {part}")

    # Income vs Expense flag
    if result.income_expense_flag:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ Note:</strong> Your current living expenses exceed your current income.
            This plan assumes future normalization of income and/or expenses. The numbers have not been recomputed based on this flag.
        </div>
        """, unsafe_allow_html=True)


def display_assumptions(result: RetirementResult):
    """Section D: Assumptions"""
    st.markdown('<p class="section-header">D. Assumptions (Explicit)</p>', unsafe_allow_html=True)

    st.markdown('<div class="assumption-box">', unsafe_allow_html=True)
    for assumption in result.assumptions:
        st.markdown(f"• {assumption}")
    st.markdown('</div>', unsafe_allow_html=True)


def display_disclaimers():
    """Section E: Disclaimers"""
    st.markdown('<p class="section-header">E. Disclaimers (Mandatory)</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-box">
        <strong>📋 Educational Guidance Only:</strong> This plan is for educational and illustrative purposes only.
        It should not be considered as financial advice.<br><br>
        <strong>📈 Market Risk:</strong> Investments are subject to market risks. Past performance does not guarantee future results.
        Actual returns may vary significantly from assumptions.<br><br>
        <strong>🔢 Assumption-Based Planning:</strong> This projection is based on assumed constant inflation and returns.
        Real-world conditions change frequently.<br><br>
        <strong>🔄 Periodic Review Advised:</strong> Review and adjust your plan annually or when significant life changes occur.
    </div>
    """, unsafe_allow_html=True)


def display_next_steps():
    """Section F: Next Steps"""
    st.markdown('<p class="section-header">F. Next Steps</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="next-steps-box">
        <strong>1. Track Annually:</strong> Review your retirement plan every year<br><br>
        <strong>2. Adjust with Life Changes:</strong> Update when income, expenses, or goals change<br><br>
        <strong>3. Revisit Assumptions:</strong> Periodically check if return/inflation assumptions still hold<br><br>
        <strong>4. Consult a Professional:</strong> For personalized advice, consult a certified financial planner
    </div>
    """, unsafe_allow_html=True)


def display_whatif_scenarios(inputs: RetirementInputs, base_result: RetirementResult):
    """Display what-if scenario comparisons"""
    st.markdown('<p class="section-header">What-If Scenarios</p>', unsafe_allow_html=True)

    st.info("Compare how different retirement ages affect your monthly savings requirement.")

    # Generate scenarios for different retirement ages
    scenarios = []
    for age in [55, 58, 60, 62, 65]:
        if age > inputs.current_age and age != inputs.retirement_age:
            scenario = calculate_whatif_scenario(inputs, age)
            scenarios.append({
                "age": age,
                "result": scenario
            })

    # Display base plan
    st.markdown(f"""
    <div class="whatif-card-base">
        <strong>📌 Base Plan (Retire at {base_result.retirement_age})</strong><br>
        Monthly SIP Required: <strong>{format_currency(base_result.monthly_savings_rounded)}</strong>
    </div>
    """, unsafe_allow_html=True)

    # Display scenarios
    cols = st.columns(min(len(scenarios), 3))
    for i, scenario in enumerate(scenarios[:3]):
        with cols[i % 3]:
            diff = scenario["result"].monthly_savings_rounded - base_result.monthly_savings_rounded
            diff_sign = "+" if diff > 0 else ""
            diff_color = "#bf6a6a" if diff > 0 else "#6abf6a"

            reason = "Shorter accumulation period" if scenario["age"] < base_result.retirement_age else "Longer accumulation period"

            st.markdown(f"""
            <div class="whatif-card">
                <strong>What-if: Retire at {scenario["age"]}</strong><br>
                Monthly SIP: <strong style="color: #D1A36C;">{format_currency(scenario["result"].monthly_savings_rounded)}</strong><br>
                <span style="color: {diff_color};">({diff_sign}{format_currency(abs(diff))})</span><br>
                <small style="color: #8B8D98;"><em>Reason: {reason}</em></small>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-box">
        <em>These what-if scenarios are illustrative comparisons based on the same assumptions as your base plan.
        They are meant to show directional impact, not to replace the original plan.</em><br><br>
        If you'd like, we can convert one of these scenarios into a full plan by re-running the analysis.
    </div>
    """, unsafe_allow_html=True)


def display_result_card(result: RetirementResult, inputs: RetirementInputs):
    """Display the complete retirement planning result"""

    st.markdown("---")
    st.markdown('<h2 style="color: #D1A36C; text-align: center;">🎯 Your Retirement Plan</h2>', unsafe_allow_html=True)

    # Section A: Goal Summary
    display_goal_summary(result, inputs)

    # Section B: Authoritative Numbers
    display_authoritative_numbers(result)

    # Section C: Explanation
    display_explanation(result, inputs)

    # Section D: Assumptions
    display_assumptions(result)

    # Section E: Disclaimers
    display_disclaimers()

    # Section F: Next Steps
    display_next_steps()

    # What-If Scenarios
    st.markdown("---")
    display_whatif_scenarios(inputs, result)

    # Download Excel button
    st.markdown("---")
    st.markdown('<h3 style="color: #D1A36C;">📥 Download Your Plan</h3>', unsafe_allow_html=True)

    excel_data = generate_excel_plan(result, inputs)
    if excel_data:
        st.download_button(
            label="📊 Download Excel Plan (with What-If Scenarios)",
            data=excel_data,
            file_name="retirement_plan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.caption("Editable spreadsheet with inputs, calculations, and what-if scenarios.")
    else:
        st.warning("Excel export requires pandas and openpyxl. Install with: pip install pandas openpyxl")


def reset_chat():
    """Reset the chat and start fresh"""
    st.session_state.messages = []
    st.session_state.calculation_done = False
    st.session_state.result = None
    st.session_state.inputs = None
    st.session_state.collected_data = None
    st.session_state.whatif_mode = False
    st.session_state.followup_messages = []


def main():
    """Main application"""
    init_session_state()

    # Logo and Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("image.png", use_container_width=True)

    st.markdown('<p class="main-header">Goal Planning Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Retirement Planning | Excel-Wired | Conversation-Driven</p>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Settings")

        # Check API key status
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            st.success("✓ API Key loaded from .env")
        else:
            st.error("✗ API Key not found in .env")

        st.markdown("---")

        # Reset button
        if st.button("🔄 Start New Plan", use_container_width=True):
            reset_chat()
            st.rerun()

        st.markdown("---")

        # Info section
        st.markdown("### 📖 How it works")
        st.markdown("""
        1. Chat with the assistant
        2. Answer questions one at a time
        3. Get your personalized plan
        4. Ask follow-up questions
        5. Download PDF/Excel reports
        """)

        st.markdown("---")

        st.markdown("### 📊 Data We Collect")
        st.markdown("""
        - Current age
        - Desired retirement age
        - Life expectancy
        - Current expenses (monthly/annual)
        - Current investments
        - Risk preference
        - Dependents info
        - Current income
        """)

        st.markdown("---")

        st.markdown("### 🔒 Locked Assumptions")
        st.markdown("""
        - **Inflation:** 6% p.a.
        - **Conservative return:** 8%
        - **Moderate return:** 12%
        - **Aggressive return:** 15%
        """)

    # Check for API key from environment
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OpenAI API Key not found!")
        st.markdown("""
        ### Setup Required

        Please create a `.env` file in the project directory with your OpenAI API key:

        ```
        OPENAI_API_KEY=your_api_key_here
        ```

        You can get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

        ---

        ### What This App Does

        Once configured, the assistant will guide you through:
        - Collecting your retirement planning details
        - Calculating your required retirement corpus
        - Determining your monthly SIP amount
        - Exploring what-if scenarios
        - Downloading PDF/Excel reports
        """)
        return

    # Display result card if calculation is done
    if st.session_state.calculation_done and st.session_state.result:
        display_result_card(st.session_state.result, st.session_state.inputs)
        st.markdown("---")
        st.markdown('<h3 style="color: #D1A36C;">💬 Conversation History</h3>', unsafe_allow_html=True)

    # Chat container
    chat_container = st.container()

    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Don't display the JSON part of CALCULATION_READY
                content = message["content"]
                if "CALCULATION_READY" in content:
                    content = content.split("CALCULATION_READY")[0].strip()
                    if content:
                        st.markdown(content)
                    st.success("✅ All information collected! Your retirement plan is ready above.")
                else:
                    st.markdown(content)

    # Start conversation if empty
    if not st.session_state.messages:
        initial_message = """Hello! 👋 I'm your Goal Planning Assistant, here to help you plan for a comfortable retirement.

I'll guide you through a series of questions to understand your retirement goals. We'll cover:
- Your current situation
- When you'd like to retire
- Your financial details
- Your risk preferences

**Each new conversation starts fresh** - I don't assume any prior context.

Let's begin! **What is your current age?** (You can also share your date of birth if you prefer.)"""

        st.session_state.messages.append({
            "role": "assistant",
            "content": initial_message
        })
        st.rerun()

    # Chat input - different behavior based on state
    if not st.session_state.calculation_done:
        # Initial data collection phase
        if prompt := st.chat_input("Type your answer here..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Get GPT response
            gpt_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
            response = chat_with_gpt(gpt_messages)

            # Check if calculation is ready
            calc_data = extract_calculation_data(response)
            if calc_data:
                st.session_state.collected_data = calc_data
                result, inputs = perform_calculation(calc_data)
                st.session_state.result = result
                st.session_state.inputs = inputs
                st.session_state.calculation_done = True

            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})

            st.rerun()
    else:
        # Follow-up chat phase - dashboard is ready
        st.markdown("---")
        st.markdown('<h3 style="color: #D1A36C;">💬 Ask Follow-up Questions</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
            <strong>You can ask about:</strong><br>
            • What-if scenarios (e.g., "What if I retire at 58?")<br>
            • Explanations of any calculation<br>
            • How to achieve your goals<br>
            • Impact of changing assumptions
        </div>
        """, unsafe_allow_html=True)

        # Display follow-up conversation
        for msg in st.session_state.followup_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Follow-up chat input
        if followup_prompt := st.chat_input("Ask a follow-up question..."):
            # Add user message to followup
            st.session_state.followup_messages.append({
                "role": "user",
                "content": followup_prompt
            })

            # Get follow-up response
            with st.spinner("Thinking..."):
                response = chat_followup(
                    followup_prompt,
                    st.session_state.result,
                    st.session_state.inputs
                )

            # Add assistant response
            st.session_state.followup_messages.append({
                "role": "assistant",
                "content": response
            })

            st.rerun()


if __name__ == "__main__":
    main()
