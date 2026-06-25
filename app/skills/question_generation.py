# Question Generation Skill: Generates role-specific questions grounded in claims
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent

class QuestionList(BaseModel):
    questions: list[str] = Field(
        description="A list of exactly 10 challenging, comprehensive technical interview questions grounded in the candidate's claims and tailored to their target role."
    )

question_generator_agent = LlmAgent(
    name="question_generator_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are an expert technical interviewer. Review the target job role and the extracted claims, "
        "technical choices, metrics, and decisions of the candidate. "
        "Generate exactly 10 challenging, role-specific technical interview questions. "
        "The questions must comprehensively cover everything mentioned in the candidate's CV and project "
        "documentation — every project, every technical choice, every metric, and every tool or framework "
        "mentioned in their materials is fair game and should be covered. "
        "Do not repeat the same focus; span the entire breadth of their experience, asking them to justify "
        "architectural trade-offs, explain operational choices, details of specific achievements, or how they "
        "engineered particular solutions."
    ),
    output_schema=QuestionList,
)
