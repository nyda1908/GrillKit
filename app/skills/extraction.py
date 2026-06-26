# Extraction Skill: Extracts key claims, technical choices, metrics, and decisions with rankings
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from typing import Literal

class Claim(BaseModel):
    text: str = Field(description="A specific technical claim, framework choice, performance metric, or architectural decision.")
    category: str = Field(description="The category of the claim (e.g., 'Technical Choice', 'Metric', 'Project Decision').")
    source: str = Field(description="The source of the claim, e.g., 'CV' or 'Project Doc'.")
    rank: Literal["critical", "major", "minor"] = Field(
        description=(
            "The importance or impact rank of this claim. "
            "'critical' for core architecture, major high-impact metrics, and central project decisions. "
            "'major' for significant features, complex integrations, and secondary design choices. "
            "'minor' for standard tools, basic skills, auxiliary tasks, and standard frameworks."
        )
    )

class ExtractedProfile(BaseModel):
    claims: list[Claim] = Field(description="List of extracted technical claims, choices, metrics, and decisions ranked by importance.")

extractor_agent = LlmAgent(
    name="extractor_agent",
    model="gemini-2.0-flash",
    instruction=(
        "You are an expert technical interviewer. Review the candidate's CV and project documentation "
        "provided below:\n\n"
        "--- CANDIDATE CV ---\n"
        "{cv_text}\n\n"
        "--- PROJECT DOCUMENTATION ---\n"
        "{doc_text}\n\n"
        "Extract all key technical claims, framework/architectural choices, performance metrics "
        "(e.g. latency, throughput, scale), and critical project decisions. "
        "Extract only factual, concrete details. "
        "Rank each claim according to the schema rules: "
        "- 'critical' for the most important core architectures, major metrics, and central decisions. "
        "- 'major' for significant features, complex integrations, and secondary choices. "
        "- 'minor' for standard tools, basic technologies, or auxiliary tasks. "
        "Categorize, rank, and structure them according to the schema."
    ),
    output_schema=ExtractedProfile,
)
