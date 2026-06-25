# Evaluation Skill: Evaluates candidate answers for accuracy, depth, and vagueness
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.genai import types

class EvaluationResult(BaseModel):
    question: str = Field(description="The main technical question that was asked.")
    answer: str = Field(description="The candidate's answer to the main question.")
    followup_question: str = Field(description="The skeptical follow-up question that was asked.")
    followup_answer: str = Field(description="The candidate's answer to the follow-up question.")
    accuracy_feedback: str = Field(description="Detailed evaluation of technical accuracy across both answers.")
    depth_feedback: str = Field(description="Detailed evaluation of depth (did they explain the 'why' and 'how' across both answers?).")
    vagueness_feedback: str = Field(description="Detailed evaluation of vagueness (were their answers hand-wavy or too high-level across both answers?).")
    score: int = Field(description="Overall score for this Q&A turn from 1 (poor) to 10 (excellent).")
    is_weak_area: bool = Field(description="True if the answers revealed a significant weak area or gap in knowledge, False otherwise.")
    weak_area_topic: str = Field(description="The specific topic or technology of the weak area if applicable, otherwise empty.")

evaluator_agent = LlmAgent(
    name="evaluator_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are an expert technical interviewer. Evaluate the candidate's answers to the main question "
        "and the subsequent follow-up question together. "
        "Review their responses for:\n"
        "1. Accuracy: Are the answers technically correct? Are there any errors or fabrications?\n"
        "2. Depth: Do they demonstrate a deep, thorough understanding of the architecture, design choices, "
        "and trade-offs, or just surface-level knowledge? Did they successfully explain the 'how' and 'why'?\n"
        "3. Vagueness: Were their answers specific and concrete, or did they remain hand-wavy and avoid details "
        "even after being pressed in the follow-up?\n\n"
        "Provide detailed, objective feedback for each aspect, score the overall turn from 1 to 10, "
        "and determine if this represents a weak area. "
        "Identify the specific technical topic of the weak area if applicable."
    ),
    output_schema=EvaluationResult,
    generate_content_config=types.GenerateContentConfig(
        max_output_tokens=4096
    ),
)
