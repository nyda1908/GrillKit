# Extraction Skill: Extracts key claims, technical choices, metrics, and decisions
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent

class Claim(BaseModel):
    text: str = Field(description="A specific technical claim, framework choice, performance metric, or architectural decision.")
    category: str = Field(description="The category of the claim (e.g., 'Technical Choice', 'Metric', 'Project Decision').")
    source: str = Field(description="The source of the claim, e.g., 'CV' or 'Project Doc'.")

class ExtractedProfile(BaseModel):
    claims: list[Claim] = Field(description="List of extracted technical claims, choices, metrics, and decisions.")

extractor_agent = LlmAgent(
    name="extractor_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are an expert technical interviewer. Review the candidate's CV and project documentation "
        "provided below:\n\n"
        "--- CANDIDATE CV ---\n"
        "{cv_text}\n\n"
        "--- PROJECT DOCUMENTATION ---\n"
        "{doc_text}\n\n"
        "Extract all key technical claims, framework/architectural choices, performance metrics "
        "(e.g. latency, throughput, scale), and critical project decisions. "
        "Extract only factual, concrete details. Categorize and structure them according to the schema."
    ),
    output_schema=ExtractedProfile,
)
