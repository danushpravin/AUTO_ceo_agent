# 'agent.py' Documentation

## File Purpose
'agent.py' is the **LLM orchestration layer**.

This file is responsible for:
- Initializing the OpenAI client and model.
- Defining all tool schemas exposed to the LLM
- Enforcing strict system-level rules and behaviour via the system prompt.
- Managing the tool-calling execution loop.
- Returning the final assistant response.

This is the **file that directly interacts with the OpenAI API**.

---

## Responsibilities

- Register all internal tools in OpenAI-compatible schema format.
- Control how the LLM is allowed to reason and act.
- Route tool calls from the LLM to actual Python functions.
- Feed tool outputs back into the conversation.
- Support multi-step, multi-tool reasoning in a single run.

---

## Model and Client Initialization

```python
MODEL = "gpt-4.1-mini"
client = OpenAI()
```
- The OpenAI client is initialized once.
- Model selection is centralized here.
- No other file is aware of the model or OpenAI SDK.

---

## Tool Schema Definition (OPENAI_TOOLS)

**OPENAI_TOOLS** defines the complete interface between the LLM and the internal system.

### Purpose
- Restrict the LLM to explicityly allowed operations.
- Provide structured names, descriptions and parameters.
- Prevent arbitrary function execution.

### Structure
Each entry follows OpenAI's function tool schema:
- **name** -> maps directly to a function in 'tools.py'.
- **description** -> guides tool selection.
- **parameters** -> strictly typed arguments (or empty object).

### Categories (Logical Grouping)
- Executive metrics
- Analytics
- Inventory and marketing
- Interpretation
- Recommendation
These groupings are organizational only and have no runtime effect.

---

## Tool Execution (execute_tool)

```python
def execute_tool(name: str, arguments: Dict[str, Any]):
```
### Responsibility
- Dynamically resolve the requested tool from tools.py.
- Execute it with provided arguments.
- Return raw results back to the agent loop.

### Notes
- Tools are called by name, not imported individually.
- Errors are caught and returned as structured dicts.
- This function does not validate business logic - only execution.

---

## System Prompt (SYSTEM_PROMPT)

The system prompt defines hard operational constraints, not style.

### Enforced Guarantees
- Only tool-returned data may be used.
- No hallucination, estimation, or guessing.
- No external knowledge.
- No currency mixing.
- Missing data must halt analysis.

### Behavioural Constraints
- Risk-first reporting.
- No permission seeking.
- No softening of negative findings.
- Interpretation must precede recommendations.
- Recommendations may only be produced via the recommendation tool.

The prompt converts the LLM from a chatbot into a rule-bound executive agent.

---

## Agent Loop (run_ceo_agent)

```python
def run_ceo_agent(conversation: List[Dict[str, str]])
```

### Resposnibilities
- Initialize the conversation with the system prompt.
- Send messages, tools, and tool choice policy to the LLM.
- Handle iterative tool calls.
- Support multiple tool calls in a single turn.
- Return the final assistant response when no tools are requested.

### Loop Flow
1. Send messages + tool schemas to the model
2. If tool calls are returned:
   - Execute each tool
   - Append results as tool messages
   - Continue the loop
3. If no tool calls:
   - Return the final assistant message
   - Exit

### Key Property 
This agent can:
- Call multiple tools
- Chain tools across turns
- Decide autonomously when analysis is complete

## What this file does NOT do
- Does not compute metrics
- Does not read CSVs
- Does not contain business logic
- Does not interpret numeric data itself
- Does not generate recommendations directly
- Does not persist state

## Summary

'agent.py' is a pure orchestration file.

It:
- Defines what the LLM is allowed to do.
- Enforces how it must behave.
- Executes tool calls safely.
- Manages the reasoning loop.

All intelligence lives elsewhere.
This file ensures it is used correctly and deterministically.


