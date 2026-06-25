# State Tracking Skill: Tracks evaluations and weak areas across the session
from google.adk.events.event import Event
from google.adk.agents.context import Context
from .evaluation import EvaluationResult

def process_evaluation(ctx: Context, node_input: EvaluationResult) -> Event:
    """Processes the evaluation result, updates state, and loops back to the interview."""
    # Retrieve current state lists (default to empty lists if not set)
    evaluations = ctx.state.get("evaluations", [])
    weak_areas = ctx.state.get("weak_areas", [])
    
    # Append the latest evaluation (convert Pydantic model to dict)
    evaluations.append(node_input.model_dump())
    
    # Track weak areas if identified, avoiding duplicates
    if node_input.is_weak_area and node_input.weak_area_topic:
        topic = node_input.weak_area_topic.strip()
        if topic and topic not in weak_areas:
            weak_areas.append(topic)
            
    # Increment the question index to move to the next question
    current_index = ctx.state.get("current_index", 0)
    current_index += 1
    
    # Return Event with the updated state and the "loop" route to trigger the next question
    return Event(
        state={
            "evaluations": evaluations,
            "weak_areas": weak_areas,
            "current_index": current_index
        },
        route="loop"
    )
