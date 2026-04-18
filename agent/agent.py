import json
from typing import Dict, Any, List
from openai import OpenAI
from agent.rag.retriever import KnowledgeRetriever
retriever = KnowledgeRetriever()
from . import tools
from .tools import CTX
# ---------------- CONFIG ----------------

MODEL = "gpt-4.1-mini"
client = OpenAI()

# ---------------- TOOL SCHEMAS ----------------

OPENAI_TOOLS = [

    # -------- EXECUTIVE --------
    {
        "type": "function",
        "function": {
            "name": "tool_daily_delta",
            "description": "Today vs yesterday revenue delta.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_revenue_recent_performance",
            "description": "Recent revenue trend vs baseline.",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "default": 7}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_top_products",
            "description": "Top products by revenue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "default": 3}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_top_regions",
            "description": "Top regions by revenue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "default": 3}
                },
            },
        },
    },

    # -------- ANALYTICS --------
    {
        "type": "function",
        "function": {
            "name": "tool_sales_by_product",
            "description": "Revenue grouped by product.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_sales_by_region",
            "description": "Revenue grouped by region.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_sales_by_channel",
            "description": "Revenue grouped by channel.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_revenue_by_month",
            "description": "Monthly revenue trend.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_revenue_by_month_by_product",
            "description": "Monthly revenue broken down by product. Use this to identify seasonal patterns, growth trends, and peak months per product.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_profit_by_product",
            "description": "Profit and margin per product.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_true_profit_by_channel",
            "description": "True net profit by channel.",
            "parameters": {"type": "object", "properties": {}},
        },
    },



    # -------- INTERPRETATION --------
    {
        "type": "function",
        "function": {
            "name": "tool_interpret_growth_quality",
            "description": "Detect whether growth is real or fake.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_marketing_efficiency",
            "description": "Interpret marketing spend efficiency.",
            "parameters": {"type": "object", "properties": {
                "lookback_days": {"type": "integer",
                                  "description": "Number of days to analyze (e.g. 30, 60, 90, 180)",
                                  "default": 30}
            }},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_product_portfolio_health",
            "description": "Assess product portfolio health.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_inventory_health_vs_revenue",
            "description": "Inventory risk vs revenue performance.",
            "parameters": {"type": "object", "properties": {
                "lookback_days": {"type": "integer",
                                  "description": "Number of days to analyze (e.g. 30, 60, 90, 180)",
                                  "default": 30}
            }},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_channel_dependency_risk",
            "description": "Channel concentration and dependency risk.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    # -------- RECOMMENDATION --------
        {
        "type": "function",
        "function": {
            "name": "tool_generate_recommendations",
            "description": (
                "Generate executive recommendations based on interpretation flags "
                "and growth quality signals. Deterministic, data-driven."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

# ---------------- TOOL EXECUTOR ----------------

def execute_tool(name: str, arguments: Dict[str, Any]):
    try:
        func = getattr(tools, name)
        return func(**arguments) if arguments else func()
    except Exception as e:
        return {"error": str(e)}

# ---------------- SYSTEM PROMPT ----------------

SYSTEM_PROMPT = """
You are the AI CEO + Chief Analyst of the company — the operating system of the business.

ABSOLUTE RULES (NON-NEGOTIABLE):
- You ONLY use data returned by internal tools.
- You NEVER invent, estimate, guess, or hallucinate numbers.
- If required data is missing, you explicitly say so and stop.
- You NEVER use external knowledge or assumptions.
- You NEVER mix currencies.

CURRENCY RULES (STRICT):
- ALL monetary values are in Indian Rupees (₹).
- You MUST prefix all monetary values with ₹.
- You MUST NOT use $, USD, or any other currency symbol.
- Currency fields include:
  revenue, profit, net_profit, spend, CAC, total_cost,
  selling_price, cogs, packaging_cost, logistics_cost.
- Counts (units, days, stock, customers, percentages) are NOT currency.

BEHAVIOR:
- You think like a ruthless operator, not a chatbot.
- You interpret facts, surface risks, and expose fragility.
- You prioritize truth over optimism.
- You highlight concentration risk, fake growth, inefficiencies, and breakpoints.
- You do NOT soften bad news.

AUTONOMY:
- You automatically select and call the correct tools.
- You NEVER ask the user for permission to run analysis.
- You NEVER ask “Would you like me to…”.
- You ALWAYS take the next logical analytical step.
- You MUST complete interpretation before making any recommendation.
- Recommendations must always be traceable to explicit flags or signals.


- You report facts first.
- You explain implications clearly and concisely.
- You DO NOT give recommendations unless explicitly asked.
- When recommendations are requested, you MUST generate them exclusively via the recommendation tool.
- You MUST NOT generate recommendations directly in text.
- Material risks (inventory fragility, stockouts, critical concentration) must always be highlighted **before** reporting positive trends. Never bury them.
- If the user limits the focus, you must explicitly: 
   1) state which data or risks are excluded, 
   2) explain the impact of those exclusions on conclusions, 
   3) incorporate this context into your summary and recommendations.
- Always summarize first the critical risks, then report positive signals. Positive trends **cannot override or hide** ignored material risks.

- The business world you observe has demand patterns shaped by seasonality, 
  product lifecycle trends, and calendar events (festivals, gifting seasons, 
  promotional periods). When interpreting revenue variance across months or 
  weeks, always consider whether the pattern is consistent with expected 
  seasonal behaviour before drawing operational conclusions.
- A revenue spike does not confirm marketing improvement if it coincides with 
  a known high-demand period. A revenue decline does not confirm a crisis if 
  it follows a major demand event or occurs in a seasonally low month.
- Use tool_revenue_by_month to identify seasonal patterns in the data before 
  interpreting short-term performance. Never attribute seasonal fluctuation 
  to operational causes without evidence from tool outputs.
- Operational failures (stockouts, channel losses) during peak demand periods 
  must be reported as MORE severe, not less — the business lost revenue it 
  had market conditions to capture.

- When asked for status, performance, or health, you report:
  • What changed
  • Why it changed (if data supports it)
  • What risk it creates

- When asked to explain WHY a metric performed a certain way in a specific historical period, 
  only cite signals that are directly available from tool outputs.
  Never infer causes from calendar patterns, assumed seasonality, or external knowledge.
  If the causal data is not available from tools, explicitly state that and stop.

You are not an assistant.
You are the company’s executive brain.

"""

# ---------------- AGENT LOOP ----------------

def run_ceo_agent(conversation: List[Dict[str, str]], company_id: str):
    from agent.tools import init_company
    init_company(company_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation

    # -------- RAG KNOWLEDGE CONTEXT --------

    user_query = conversation[-1]["content"] if conversation else ""
    knowledge_context = retriever.retrieve(user_query)

    messages.insert(
        1,
        {
            "role": "system",
            "content": f"""
    Relevant Business Knowledge (reference only):

    {knowledge_context}

    Use this knowledge ONLY to interpret signals from internal tools.
    Never treat it as factual company data.
    All numbers must still come from tools.
    """
        }
    )
    tool_trace = []
    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=OPENAI_TOOLS,
            tool_choice="auto",
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append({
                "role": "assistant",
                "tool_calls": msg.tool_calls,
            })

            for call in msg.tool_calls:
                name = call.function.name
                args = json.loads(call.function.arguments or "{}")

                tool_trace.append({
                    "tool": name,
                    "arguments": args
                })

                print(f"\n TOOL CALLED: {name}")
                if args:
                    print(f"args: {args}")
                else:
                    print("args: {}")

                result = execute_tool(name, args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": name,
                    "content": json.dumps(result, default=str),
                })

            continue

        messages.append({"role": "assistant", "content": msg.content})
        return msg.content
