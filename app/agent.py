# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import google.auth

from google.adk.workflow import Workflow, START
from google.adk.events.event import Event
from google.adk.apps import App

# Import modular skills
from .skills.ingestion import ingestion_parser, validate_ingestion
from .skills.extraction import extractor_agent
from .skills.question_generation import QuestionList, question_generator_agent
from .skills.interview_flow import conduct_interview
from .skills.follow_up import follow_up_generator, save_followup
from .skills.evaluation import evaluator_agent
from .skills.state_tracking import process_evaluation
from .skills.reporting import report_generator_agent

# Ensure GCP environment variables are set if credentials are available
try:
    _, project_id = google.auth.default()
    if project_id:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
except Exception:
    # Fallback to Gemini API (requires GEMINI_API_KEY or GOOGLE_API_KEY)
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")


def initialize_interview(node_input: QuestionList) -> Event:
    """Initializes the workflow state with the generated questions and tracking lists."""
    return Event(
        state={
            "questions": node_input.questions,
            "current_index": 0,
            "current_phase": "main",
            "evaluations": [],
            "weak_areas": []
        },
        route="ready"
    )


# Workflow Graph Definition
root_agent = Workflow(
    name="grillkit_interview_workflow",
    description="AI-powered technical interview coach that conducts interactive, grounded interviews.",
    edges=[
        # Ingestion & Parsing Flow
        (START, ingestion_parser),
        (ingestion_parser, validate_ingestion),
        
        # Route depending on whether materials are complete or need to be reparsed
        (validate_ingestion, {
            "reparse": ingestion_parser,
            "valid": extractor_agent
        }),
        
        # Claims Extraction & Question Generation Chain
        (extractor_agent, question_generator_agent),
        (question_generator_agent, initialize_interview),
        
        # Start/Resume Q&A loop
        (initialize_interview, conduct_interview),
        
        # Route from conduct_interview depending on the phase and completion
        (conduct_interview, {
            "generate_followup": follow_up_generator,
            "evaluate": evaluator_agent,
            "complete": report_generator_agent
        }),
        
        # Generate follow-up question and save to state, then loop back to ask it
        (follow_up_generator, save_followup),
        (save_followup, {
            "ask_followup": conduct_interview
        }),
        
        # Evaluate candidate answer and update state
        (evaluator_agent, process_evaluation),
        
        # Loop back to conduct the next main question
        (process_evaluation, {
            "loop": conduct_interview
        }),
    ],
)

# App Container (app name matches the directory name "app" to prevent session errors)
app = App(
    root_agent=root_agent,
    name="app",
)
