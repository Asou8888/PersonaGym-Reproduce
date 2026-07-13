# PersonaGym-Reproduce

A from-scratch reproduction of [**PersonaGym**](https://arxiv.org/abs/2407.18416), a benchmark for evaluating how consistently an LLM can role-play a given persona. Built as a learning project — not affiliated with the original paper's authors.

The pipeline takes a natural-language persona description (e.g. *"A 71-year-old retired nurse from Italy, volunteering in hospice care"*), puts it through five evaluation tasks, and produces a 1–5 consistency score per task plus an overall score.

## How it works

The benchmark is implemented as a [LangGraph](https://github.com/langchain-ai/langgraph) map-reduce pipeline (`src/graph/builder.py`) with four stages:

1. **Setting selection** — an LLM picks realistic scenarios (from a catalog of ~150) that fit the persona, e.g. a "Wedding" or a "Science Laboratory."
2. **Question generation** — for each of the 5 evaluation tasks below, an LLM generates challenge questions designed to probe that specific dimension, grounded in the selected settings.
3. **Response generation** — the persona is role-played by an LLM to answer every generated question in character.
4. **Response evaluation & aggregation** — one or more LLM judges score every (question, answer) pair 1–5 against a task-specific rubric, using generated calibration examples per score level. Scores are batched, averaged across judges, and rolled up into a per-task score and an overall score.

Each stage fans out with LangGraph's `Send` API (per task, then per question, then per batch) so questions, answers, and judgments are generated concurrently.

### The 5 evaluation tasks

|Task|What it measures|
|---|---|
|**Expected Action**|Does the persona take actions consistent with its characteristics in the given setting?|
|**Toxicity**|Does the persona avoid toxic responses when provoked?|
|**Linguistic Habits**|Does the persona maintain its distinctive speech/language style?|
|**Persona Consistency**|Does the persona stick to its defined attributes without fabricating new ones?|
|**Action Justification**|Can the persona coherently justify its own actions?|

See `src/data/evaluation_tasks.py` for the full task descriptions used to steer question generation, and `src/prompts/response_evaluation.py` for the scoring rubrics.

## Project layout

```text
src/
├── app.py                 # CLI entry point
├── config.py               # env-driven model config per pipeline stage
├── data/
│   ├── evaluation_tasks.py    # the 5 task definitions + question-generation guidance
│   ├── settings_catalog.py    # ~150 candidate settings/scenarios
│   └── sample_personas.py     # bundled example personas
├── graph/
│   ├── builder.py           # wires the LangGraph pipeline
│   ├── routing.py           # Send-based fan-out logic between stages
│   └── state.py              # shared graph state + reducers
├── models/schemas.py        # pydantic schemas for structured LLM outputs
├── nodes/                   # one module per pipeline stage (see "How it works")
├── prompts/                  # prompt templates and scoring rubrics
├── services/
│   ├── persona_dataset.py    # sample persona lookup
│   └── results_writer.py     # writes run results to JSON
└── tests/                    # pipeline smoke tests
```

## Setup

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.temp .env
```

Fill in `.env` with your `OPENAI_API_KEY` (calls are routed through [LiteLLM](https://github.com/BerriAI/litellm), so other providers work too — see `src/config.py`). Each pipeline stage has its own model/temperature/top_p env vars, so you can mix models (e.g. a cheaper model for question generation, stronger judges for evaluation).

> **Note:** the codebase's internal imports currently reference the package as `src_v2` while the directory on disk is `src`, so the pipeline won't import as-is. Rename the directory to `src_v2` (or update the imports to `src`) before running.

## Usage

```bash
# Evaluate a custom persona
python -m src.app "A 71-year-old retired nurse from Italy, volunteering in hospice care"

# Or pick one of the bundled sample personas
python -m src.app --sample-index 0

# Tune question count / output location
python -m src.app "A grumpy sea captain who never smiles" --n-questions 3 --output-dir results
```

Each run prints the overall score and per-task breakdown, and writes a timestamped JSON report to `results/`.

## Status

Work in progress — a learning reproduction, not a production benchmark. Expect rough edges.
