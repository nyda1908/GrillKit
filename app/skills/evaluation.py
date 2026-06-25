# Evaluation Skill: Evaluates candidate answers for accuracy, depth, and vagueness
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent

class EvaluationResult(BaseModel):
    question: str = Field(description="The question that was asked.")
    answer: str = Field(description="The candidate's answer.")
    accuracy_feedback: str = Field(description="Detailed evaluation of technical accuracy (is the answer correct?).")
    depth_feedback: str = Field(description="Detailed evaluation of depth (did they explain the 'why' and 'how'?).")
    vagueness_feedback: str = Field(description="Detailed evaluation of vagueness (were they hand-wavy or too high-level?).")
    score: int = Field(description="Overall score for this answer from 1 (poor) to 10 (excellent).")
    is_weak_area: bool = Field(description="True if the answer revealed a significant weak area or gap in knowledge, False otherwise.")
    weak_area_topic: str = Field(description="The specific topic or technology of the weak area if applicable, otherwise empty.")

evaluator_agent = LlmAgent(
    name="evaluator_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are an expert technical interviewer. Evaluate the candidate's answer to the given question. "
        "Review the answer for: "
        "1. Accuracy: Is the answer technically correct? "
        "2. Depth: Does the candidate demonstrate a deep, thorough understanding, or just surface-level knowledge? "
        "3. Vagueness: Is the answer specific and concrete, or is it hand-wavy and lacking detail? "
        "Provide detailed feedback for each aspect, score the answer from 1 to 10, and determine if this represents a weak area. "
        "Identify the specific technical topic of the weak area if they underperformed."
    ),
    output_schema=EvaluationResult,
)
