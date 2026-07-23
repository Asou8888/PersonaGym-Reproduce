import asyncio
import json
import os

from dotenv import load_dotenv

from src.graph.builder import build_benchmark_graph

# Load .env
load_dotenv(".test.env")
assert "OPENAI_API_KEY" in os.environ, "OPENAI_API_KEY is not set in the environment variables."


async def test_full_pipeline(persona: str, n_questions: int) -> dict:
    graph = build_benchmark_graph()
    return await graph.ainvoke({"persona": persona, "n_questions": n_questions})


if __name__ == "__main__":
    persona = "Asian software engineer"
    n_questions = 5
    final_state = asyncio.run(test_full_pipeline(persona=persona, n_questions=n_questions))
    print(f"Overall Score: {final_state['overall_score']}")
    print(f"Scores by Task: {json.dumps(final_state['task_scores'], indent=2)}")
