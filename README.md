# GrillKit 

**AI-powered technical interview coach that grills you on your own CV.**

GrillKit reads your CV and project documentation, extracts every technical claim you've made, and conducts a rigorous mock interview grounded in your actual work. It evaluates your answers, tracks where you're weak, and generates a detailed report at the end- so you know exactly what to fix before the real thing.

Built with Google ADK 2.0 and Agents CLI as part of the [Kaggle 5-Day AI Agents Intensive Course with Google](https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google).

---

## The Problem

Placement season is brutal. You have a CV full of projects but no good way to practice defending them. Mock interviews with friends don't work because they don't know your work deeply enough to probe it. Generic interview prep tools ask generic questions. GrillKit fixes this by turning your own CV into a personalized interviewer.

---

## Why Agents?

A plain LLM chat can answer questions about your CV if you paste it in. GrillKit is different:

- **Structured pipeline**: every user goes through the same rigorous flow: ingest → extract claims → generate grounded questions → evaluate answers → track weaknesses → report. The output is consistent and repeatable.
- **Persistent session state**: GrillKit tracks your answers across all 10 questions, accumulates your weakness pattern, and synthesizes everything into a final report. A chatbot forgets Q3 by Q7.
- **PDF upload**: upload your actual CV file. GrillKit parses and extracts the text automatically.
- **Deployable system**: not a prompt, a product. Anyone can upload their CV and get grilled.

---

## Architecture

GrillKit is an ADK 2.0 graph workflow agent with 8 modular skills:

```
START
  └─► ingest_cv_docs        # Parse CV text or PDF, validate inputs
        └─► extractor_agent      # Extract technical claims, metrics, decisions
              └─► question_generator_agent  # Generate grounded interview questions
                    └─► initialize_interview
                          └─► conduct_interview  ◄──────────────────────────┐ (loop)
                                ├─► follow_up_generator ──► save_followup ──┤ (follow-up)
                                ├─► evaluator_agent ──► process_evaluation ─┘
                                └─► report_generator_agent (on complete)
                                      └─► END
```

### Skills (`app/skills/`)

| Skill | File | What it does |
|---|---|---|
| Ingestion | `ingestion.py` | Parses CV text or PDF, validates inputs, persists state |
| Extraction | `extraction.py` | Extracts claims, technical choices, metrics, and decisions |
| Question Generation | `question_generation.py` | Generates role-specific questions grounded in extracted claims |
| Interview Flow | `interview_flow.py` | Drives the multi-turn Q&A loop using ADK Human-in-the-Loop |
| Follow-up Question | `follow_up.py` | Generates one adversarial follow-up question targeting the weakest part of the candidate's answer |
| Evaluation | `evaluation.py` | Evaluates each answer for accuracy, depth, and vagueness |
| State Tracking | `state_tracking.py` | Accumulates evaluations and tracks weak areas across the session |
| Reporting | `reporting.py` | Generates a final Markdown report with strong areas, weak areas, and follow-up questions |

---

## Tech Stack

- **Agent Framework**: Google ADK 2.0
- **Scaffolding**: Agents CLI
- **Model**: Gemini 2.5 Flash
- **PDF Parsing**: pypdf
- **Language**: Python 3.11+
- **Package Manager**: uv

---

## Course Concepts Demonstrated

| Concept | Where |
|---|---|
| Agent / Multi-agent system (ADK 2.0) | `app/agent.py`: graph workflow with 12 nodes and 14 edges |
| Agent Skills (Agents CLI) | `app/skills/`: 8 modular skills with progressive disclosure |
| Security features | Input sanitization in `ingestion.py`; no API keys in code; context boundary (agent only sees what the user uploads) |

---

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- Node.js 18+
- [Antigravity IDE](https://antigravity.google/download)
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Installation

```bash
# Clone the repo
git clone https://github.com/nyda1908/GrillKit.git
cd GrillKit

# Install Agents CLI
uvx google-agents-cli setup

# Install project dependencies
uv sync

# Set your API key in the .env file
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Run

```bash
agents-cli playground
```

Then open [http://127.0.0.1:8080/dev-ui/?app=app](http://127.0.0.1:8080/dev-ui/?app=app) in your browser.

---

## Usage

1. **Start a new session** in the playground
2. **Upload your CV as a PDF** using the + button, or paste your CV text directly
3. **Specify your target role** (e.g. ML Engineer, Quant Research, Data Scientist)
4. **Answer 10 questions**: each one grounded in something you actually claimed on your CV
5. **Receive your report**: strong areas, weak areas, and suggested follow-up questions to practice

---

## Example Output

After completing a session, GrillKit generates a structured report like:

```
Strong Areas:
- Multi-channel Transformer architecture and LTC neuron design
- TorchScript JIT optimization and FPGA porting analysis

Weak Areas:
- Operational risk management details in HFT context
- Concrete slippage estimation methodology

Suggested Follow-up Questions:
1. Design a circuit breaker for a live HFT options strategy...
2. Describe a dynamic methodology for real-time slippage estimation...
```

---

## Project Structure

```
GrillKit/
├── app/
│   ├── __init__.py
│   ├── agent.py              # Workflow graph definition
│   └── skills/
│       ├── ingestion.py
│       ├── extraction.py
│       ├── question_generation.py
│       ├── interview_flow.py
│       ├── follow_up.py
│       ├── evaluation.py
│       ├── state_tracking.py
│       └── reporting.py
├── tests/
│   └── eval/
│       ├── eval_config.yaml
│       └── datasets/
│           └── basic-dataset.json
├── .env.example
├── pyproject.toml
└── README.md
```

---

## Known Limitations

- Gemini API rate limits can interrupt long sessions during peak demand; adding retry logic with exponential backoff is the recommended production fix
- PDF parsing works best with text-based PDFs; scanned image PDFs are not supported
- Session state is in-memory; restarting the server clears all sessions

---

## Author

Nidhi Maheshwari — Mathematics and Computing, IIT Kharagpur  
[GitHub](https://github.com/nyda1908) • [LinkedIn](https://linkedin.com/in/)

---

*Built for the Kaggle 5-Day AI Agents Intensive Capstone, June 2026*
