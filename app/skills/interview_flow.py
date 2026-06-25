# Interview Flow Skill: Conducts the interactive Q&A loop using Human-in-the-Loop
from google.adk.events.request_input import RequestInput
from google.adk.events.event import Event
from google.adk.agents.context import Context
from google.adk.workflow import node
from typing import Any

@node(rerun_on_resume=True)
async def conduct_interview(ctx: Context, node_input: Any):
    """Orchestrates the interview turns, asking questions and capturing answers."""
    # Retrieve current state
    questions = ctx.state.get("questions", [])
    current_index = ctx.state.get("current_index", 0)
    
    # Check if we have completed all questions in the queue
    if current_index >= len(questions):
        # We are finished! Route to report generation
        yield Event(output="interview_complete", route="complete")
        return
        
    # Check if the user has provided an answer to the current question
    interrupt_id = f"q_{current_index}"
    if ctx.resume_inputs and interrupt_id in ctx.resume_inputs:
        user_answer = ctx.resume_inputs[interrupt_id]
        current_question = questions[current_index]
        
        # Yield the question and answer to trigger the evaluation node
        yield Event(
            output={"question": current_question, "answer": user_answer},
            route="evaluate"
        )
        return
        
    # If the user has not answered yet, yield a RequestInput to pause and ask the question
    current_question = questions[current_index]
    yield RequestInput(
        interrupt_id=interrupt_id,
        message=f"\n[Question {current_index + 1}/{len(questions)}] {current_question}\n"
    )
