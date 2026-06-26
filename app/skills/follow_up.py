# Follow-up Skill: Generates and saves skeptical follow-up questions
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.events.event import Event
from google.adk.agents.context import Context

class FollowUpQuestion(BaseModel):
    question: str = Field(description="A single, sharp, skeptical follow-up question probing the candidate's answer.")

follow_up_generator = LlmAgent(
    name="follow_up_generator",
    model="gemini-2.0-flash",
    instruction=(
        "You are a highly skeptical, senior software architect conducting a technical interview. "
        "The candidate was asked a main question and gave an answer. "
        "Analyze their answer. Generate exactly one sharp, skeptical, and direct follow-up question. "
        "Your follow-up question must: "
        "1. Probe vague, hand-wavy, or high-level parts of their answer, forcing them to explain the actual details. "
        "2. Challenge their assumptions, design choices, or frameworks (e.g., asking why they chose a specific tool or "
        "why they didn't consider an alternative). "
        "3. Ask for concrete specifics, metrics, operational trade-offs, or scaling implications. "
        "4. Ask about failure cases, what didn't work in their design, or how they handled edge cases. "
        "Keep the tone professional, direct, and highly critical but fair. Do not introduce new topics; stay focused "
        "on digging deeper into their actual response. "
        "Context from state:\n"
        "Main Question: {current_main_question}\n"
        "Candidate's Answer: {current_main_answer}"
    ),
    output_schema=FollowUpQuestion,
)

def save_followup(ctx: Context, node_input: FollowUpQuestion) -> Event:
    """Saves the generated follow-up question to the state and routes back to the interview flow."""
    return Event(
        state={
            "current_follow_up_question": node_input.question
        },
        route="ask_followup"
    )
