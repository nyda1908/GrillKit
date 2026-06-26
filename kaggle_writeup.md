# GrillKit: An AI-Powered Technical Interview Coach That Grills You On Your Own CV

**Track:** Concierge Agents  
**GitHub:** https://github.com/nyda1908/GrillKit  
**Author:** Nidhi Maheshwari, Mathematics and Computing, IIT Kharagpur

---

## The Problem

Placement season is brutal. You have a CV full of projects, metrics, and technical decisions- and somewhere in that document is every question a senior engineer at a quant firm or ML lab is going to ask you. The problem is you don't know which ones, and there's no good way to practice.

Mock interviews with friends don't work because they don't know your work deeply enough to probe it. Generic interview prep tools ask generic questions- "explain gradient descent," "what is a transformer"- questions that have nothing to do with *your specific choices*. And asking a chatbot to interview you produces the same surface-level questions every time, because it's guessing rather than reading.

The gap is real and personal. I'm preparing for CDC placements at IIT Kharagpur targeting ML Engineer and Quant Research roles. I needed something that could read my actual projects and ask me exactly what a skeptical senior engineer would: *Why did you choose this architecture? What failed before you landed on this approach? Justify that metric.*

GrillKit is that thing.

---

## Why Agents?

A plain LLM can interview you if you paste your CV into a chat. GrillKit is different in ways that matter.

The Day 5 SDD whitepaper puts it cleanly: "if a brain is given a vibe instead of a blueprint, it will guess." A chatbot guesses what questions to ask. GrillKit extracts your technical claims first, ranks them by importance, then generates questions grounded in what you actually said. It has a blueprint, not a vibe.

Beyond that: GrillKit tracks your answers across all questions, accumulates a weakness map, and synthesizes everything into a final report. A chatbot forgets question 3 by question 7. The interview loop uses ADK's `RequestInput` mechanism, a formal checkpoint that separates the agent's reasoning from the human's response, not just another chat turn. And unlike a prompt, GrillKit is a deployable system: anyone can upload their CV and get grilled on their own work.

---

## Architecture

GrillKit is an ADK 2.0 graph workflow agent with 8 modular skills, implementing a stateful cyclic interview loop with Human-in-the-Loop.

```
START
  └─► ingest_cv_docs        
        └─► extractor_agent      
              └─► question_generator_agent  
                    └─► initialize_interview
                          └─► conduct_interview  ◄─────────────────┐
                                ├─► follow_up_generator             │
                                │     └─► save_followup             │
                                │           └─► evaluator_agent     │
                                │                 └─► process_evaluation ┘ (loop)
                                └─► report_generator_agent  (on complete)
                                      └─► END
```

### The 8 Skills

**Ingestion (`ingestion.py`):** Parses the candidate's CV as plain text or PDF via pypdf. Validates that cv_text and role are present before proceeding. Persists state before every `RequestInput` pause to prevent context loss across turns- a direct response to the "context fragmentation" problem the Day 5 SDD whitepaper describes.

**Extraction (`extraction.py`):** Uses an `LlmAgent` with a structured Pydantic output schema to extract every technical claim, architectural decision, metric, and tool from the CV. Each claim is ranked as `critical`, `major`, or `minor` based on how central it is to the candidate's profile.

**Question Generation (`question_generation.py`):** Generates 8–12 questions dynamically based on CV density, allocating ~50% to critical claims, ~30% to major, ~20% to minor. The system prompt adopts a skeptical senior engineer persona. Questions ask *why* decisions were made, what alternatives were considered, what failed, and what production deployment would look like.

**Interview Flow (`interview_flow.py`):** Implements a two-phase stateful loop. For each main question, the agent pauses for the candidate's answer, generates a targeted follow-up probing the weakest part of the response, pauses again, then routes to evaluation.

**Follow-up Generation (`follow_up.py`):** A dedicated `LlmAgent` that reads the main question and the candidate's answer and generates one adversarial follow-up targeting vagueness or unsubstantiated claims.

**Evaluation (`evaluation.py`):** Evaluates both the main and follow-up answers together, scoring across accuracy, depth, communication, tradeoff reasoning, and handling of uncertainty- dimensions that map to what technical interviewers actually assess.

**State Tracking (`state_tracking.py`):** Accumulates evaluations across the session and maintains a structured weakness map with topic, reason, evidence, and suggested follow-up reading for each identified gap.

**Reporting (`reporting.py`):** Generates a final Markdown report using dynamic state injection, strong areas with specific evidence, weak areas with concrete reasons, and 3 targeted follow-up questions to practice before the real interview.

---

## Course Concepts Demonstrated

| Concept | Where | How |
|---|---|---|
| Agent / Multi-agent system (ADK 2.0) | `app/agent.py` | 12-node, 14-edge graph workflow with cyclic interview loop |
| Agent Skills (Agents CLI) | `app/skills/` | 8 modular skills with progressive disclosure- each skill has one job |
| Security features | `ingestion.py`, `.env.example` | Input sanitization; API key never in code; context boundary; no PII stored between sessions |
| Human-in-the-Loop | `interview_flow.py` | `RequestInput` / `ctx.resume_inputs` pause-resume pattern for each question and follow-up |
| Deployability | `agents-cli playground` | Runs locally via ADK web server; Dockerfile included for containerised deployment |

---

## Architectural Decisions

**Why ADK graph workflow instead of a single LLM agent?** The graph forces separation of concerns: extraction before question generation, question generation before the interview loop, evaluation before reporting. Each node has a specific input schema and output contract. This is the blueprint-not-vibe principle applied structurally.

**Why modular skills?** Progressive disclosure from Day 3, the description field of each skill is the routing algorithm. Nothing is loaded until needed, keeping the context window clean across a long interview session.

**Why Human-in-the-Loop instead of simulated answers?** Because the point is to make the candidate do the work. `RequestInput` is an architectural decision, not a convenience. It makes the loop genuinely interactive rather than a self-contained LLM dialogue.

---

## The Build Journey

GrillKit was scaffolded using `agents-cli scaffold`, which generated the project skeleton including `pyproject.toml`, virtual environment setup, and evaluation dataset structure. Antigravity IDE was used throughout as the coding agent for implementing and iterating on skill files.

Three real engineering failures surfaced during the build:

**Context persistence regression.** The `validate_ingestion` node kept losing `cv_text` between turns after Antigravity rewrote `ingestion.py` during feature additions — exactly the "context fragmentation" the Day 5 SDD whitepaper warns about. Fix: explicitly yielding a state-updating `Event` before every `RequestInput` pause, marked with a `# CRITICAL` comment to survive future rewrites.

**JSON truncation in evaluation.** The `evaluator_agent` was producing `ValidationError: EOF while parsing` on detailed answers- the JSON output was being cut off mid-string. Fix: `generate_content_config` with `max_output_tokens=4096`.

**Routing failure in the cyclic loop.** The `conduct_interview` node was emitting `None` as a route instead of `"evaluate"` or `"complete"` after the follow-up loop was added. The ADK graph logged: "Node 'conduct_interview' has conditional/DEFAULT edges but none were matched." Fix: explicitly emitting the route string from the node's generator function.

These weren't just bugs, they were the exact agentic failure modes the course covered: context loss, output schema violations, and routing failures in stateful loops.

---

## What GrillKit Produces

After completing a session, GrillKit generates a structured Markdown report covering strong areas with specific evidence from the session, weak areas with concrete reasons and suggested reading, and 3 adversarial follow-up questions to practice before the real interview.

In a test session on a mock ML Engineer CV, GrillKit correctly distinguished between strong architectural answers and weak production deployment answers- flagging that the candidate described a system conceptually without specifying concrete operational parameters. That level of targeted specificity is what generic interview prep cannot produce.

---

## Lessons Learned

**Vibe coding is fast but fragile.** GrillKit was built in days using Antigravity as the implementation engine. But every feature addition risked regressing a previously fixed bug. The Day 5 SDD whitepaper is right: without behavioral specs as the source of truth, AI-generated changes break invariants silently. The production path for GrillKit starts with Gherkin specs for each skill before touching code.

**State management in cyclic workflows requires explicit design.** ADK does not automatically carry state across `RequestInput` resume points, this must be built into each node. Production agents need explicit token budget management per node and careful route emission at every branch point.

---

## Known Limitations and Future Work

- API rate limits interrupt long sessions on the free tier; exponential backoff retry logic is the recommended fix
- Adaptive interviewing- moving deeper into strong areas and pivoting away from weak ones- would significantly improve realism
- Persistent sessions across server restarts would allow multi-day practice
- A frontend interface would make GrillKit accessible without the ADK playground

---

## Setup

```bash
git clone https://github.com/nyda1908/GrillKit.git
cd GrillKit
uvx google-agents-cli setup
uv sync
cp .env.example .env
# Add your GEMINI_API_KEY to .env
agents-cli playground
```

Open `http://127.0.0.1:8080/dev-ui/?app=app`, upload your CV PDF, specify your target role, and get grilled.

---

*Built for the Kaggle 5-Day AI Agents Intensive Capstone, June 2026.*  
*Author: Nidhi Maheshwari — [LinkedIn](https://linkedin.com/in/placeholder) | [GitHub](https://github.com/nyda1908)*
