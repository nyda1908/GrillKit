# Interview Flow Skill: Conducts the interactive Q&A loop using Human-in-the-Loop
from google.adk.events.request_input import RequestInput
from google.adk.events.event import Event
from google.adk.agents.context import Context
from google.adk.workflow import node
from typing import Any

@node(rerun_on_resume=True)
async def conduct_interview(ctx: Context, node_input: Any):
    """Orchestrates the interview turns, handling main questions and follow-ups."""
    # Retrieve current state
    questions = ctx.state.get("questions", [])
    current_index = ctx.state.get("current_index", 0)
    current_phase = ctx.state.get("current_phase", "main")
    
    # 1. Check if we have completed all questions in the queue
    if current_index >= len(questions):
        yield Event(output="interview_complete", route="complete")
        return
        
    # Extract question text and expected concepts for the current turn
    current_question = questions[current_index]
    if isinstance(current_question, dict):
        q_text = current_question.get("text", "")
        expected_concepts = current_question.get("expected_concepts", [])
    else:
        q_text = getattr(current_question, "text", str(current_question))
        expected_concepts = getattr(current_question, "expected_concepts", [])
        
    interrupt_id_main = f"q_{current_index}"
    interrupt_id_followup = f"f_{current_index}"
    
    # 2. Check if we are in the "main" phase and the user has just answered
    if current_phase == "main" and ctx.resume_inputs and interrupt_id_main in ctx.resume_inputs:
        user_answer = ctx.resume_inputs[interrupt_id_main]
        
        # Save their main answer to state, transition to "follow_up" phase, and route to follow-up generator
        yield Event(
            output={
                "main_question": q_text,
                "main_answer": user_answer
            },
            state={
                "current_main_question": q_text,
                "current_main_answer": user_answer,
                "current_phase": "follow_up"
            },
            route="generate_followup"
        )
        return
        
    # 3. Check if we are in the "follow_up" phase and the user has just answered
    if current_phase == "follow_up" and ctx.resume_inputs and interrupt_id_followup in ctx.resume_inputs:
        followup_answer = ctx.resume_inputs[interrupt_id_followup]
        main_question = ctx.state.get("current_main_question")
        main_answer = ctx.state.get("current_main_answer")
        followup_question = ctx.state.get("current_follow_up_question")
        
        # We now have both answers! Yield them together with the expected concepts to trigger the evaluator agent
        yield Event(
            output={
                "question": main_question,
                "answer": main_answer,
                "expected_concepts": ", ".join(expected_concepts),
                "followup_question": followup_question,
                "followup_answer": followup_answer
            },
            route="evaluate"
        )
        return
        
    # 4. If the user hasn't answered yet, ask the appropriate question based on the current phase
    if current_phase == "main":
        yield RequestInput(
            interrupt_id=interrupt_id_main,
            message=f"\n[Question {current_index + 1}/{len(questions)}] {q_text}\n"
        )
        return
    elif current_phase == "follow_up":
        followup_question = ctx.state.get("current_follow_up_question")
        yield RequestInput(
            interrupt_id=interrupt_id_followup,
            message=f"\n[Follow-up] {followup_question}\n"
        )
        return
