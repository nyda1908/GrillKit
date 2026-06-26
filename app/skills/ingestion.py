# Ingestion Skill: Parses user's CV (text or PDF) and project documentation
import io
from pydantic import BaseModel, Field
from pypdf import PdfReader
from google.adk.agents import LlmAgent
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.agents.context import Context
from google.adk.workflow import node
from google.genai import types

class ParsedInterviewInput(BaseModel):
    cv_text: str = Field(description="Extracted CV text of the candidate. If not found, return an empty string.", default="")
    doc_text: str = Field(description="Extracted project documentation text. If not found, return an empty string.", default="")
    role: str = Field(description="The target job role they are interviewing for. If not found, return an empty string.", default="")

# LLM Agent to parse plain conversational text or pastes into structured fields
ingestion_parser = LlmAgent(
    name="ingestion_parser",
    model="gemini-2.0-flash",
    instruction=(
        "You are an assistant that parses interview materials. "
        "Analyze the candidate's input text (which may be conversational or a direct paste). "
        "Extract their CV/resume text, any project documentation or project descriptions they provided, "
        "and the target job role. If any of these are not found, return an empty string for that field."
    ),
    output_schema=ParsedInterviewInput,
)

def extract_text_from_part(part: types.Part) -> str:
    """Helper to extract text from a PDF artifact part."""
    pdf_bytes = None
    if part.inline_data and part.inline_data.data:
        pdf_bytes = part.inline_data.data
    elif part.file_data and part.file_data.file_uri:
        uri = part.file_data.file_uri
        if uri.startswith("file://"):
            path = uri[7:]
            if path.startswith("/") and ":" in path[1:3]:
                path = path[1:]
            with open(path, "rb") as f:
                pdf_bytes = f.read()
                
    if not pdf_bytes:
        raise ValueError("Could not retrieve binary data from the uploaded CV PDF.")
        
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

@node(rerun_on_resume=True)
async def validate_ingestion(ctx: Context, node_input: ParsedInterviewInput):
    """Checks if we have CV (from text or PDF), project docs, and role. If not, prompts the user."""
    # Retrieve current state values
    cv_text = ctx.state.get("cv_text") or node_input.cv_text
    doc_text = ctx.state.get("doc_text") or node_input.doc_text
    role = ctx.state.get("role") or node_input.role
    parsed_pdf = ctx.state.get("parsed_pdf")
    
    # Print the cv_text length to logs at the start of each execution/resume
    state_cv_len = len(ctx.state.get("cv_text") or "")
    input_cv_len = len(node_input.cv_text or "")
    print(f"[validate_ingestion] cv_text length in state: {state_cv_len}, in node_input: {input_cv_len}")
    
    # 1. Check if there are any uploaded PDF artifacts in the session
    filenames = await ctx.list_artifacts()
    pdf_files = [f for f in filenames if f.lower().endswith(".pdf")]
    
    # If a new PDF CV has been uploaded and not parsed yet, parse it!
    if pdf_files and pdf_files[0] != parsed_pdf:
        try:
            print(f"Loading and parsing uploaded PDF CV: {pdf_files[0]}...")
            part = await ctx.load_artifact(pdf_files[0])
            if part:
                pdf_cv_text = extract_text_from_part(part)
                if pdf_cv_text.strip():
                    cv_text = pdf_cv_text
                    parsed_pdf = pdf_files[0]
                    print("Successfully extracted text from uploaded PDF CV.")
        except Exception as e:
            print(f"Error parsing PDF CV: {e}")
            
    interrupt_id = "request_materials"
    
    # 2. If the user has just provided conversational text via RequestInput
    if ctx.resume_inputs and interrupt_id in ctx.resume_inputs:
        user_text = ctx.resume_inputs[interrupt_id]
        yield Event(
            output=user_text,
            state={
                "cv_text": cv_text,
                "doc_text": doc_text,
                "parsed_pdf": parsed_pdf,
                "role": role
            },
            route="reparse"
        )
        return

    # 3. Check if we are missing CV or target job role (project docs are optional)
    if not cv_text.strip() or not role.strip():
        missing = []
        if not cv_text.strip():
            missing.append("CV/Resume")
        if not role.strip():
            missing.append("Target Job Role")
        
        # CRITICAL: persist state before pausing or this data will be lost
        yield Event(
            state={
                "cv_text": cv_text,
                "doc_text": doc_text,
                "role": role,
                "parsed_pdf": parsed_pdf
            }
        )
        
        prompt_msg = (
            f"Welcome to GrillKit! I noticed you are missing your {', '.join(missing)}. "
            "Please paste your CV/resume, project documentation as text, and/or state your target job role below, "
            "or upload a PDF file of your CV/Resume to begin."
        )
        yield RequestInput(
            interrupt_id=interrupt_id,
            message=prompt_msg
        )
        return
        
    # 4. If we have all three, we save them to state and route to the claims extractor
    yield Event(
        output={
            "cv_text": cv_text,
            "doc_text": doc_text,
            "role": role
        },
        state={
            "cv_text": cv_text,
            "doc_text": doc_text,
            "role": role,
            "parsed_pdf": parsed_pdf
        },
        route="valid"
    )
