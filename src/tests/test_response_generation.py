import asyncio
import json
import os

from dotenv import load_dotenv

from src.nodes.response_generation import generate_answer_for_question
from src.tests.test_question_generation import test_generate_questions

# Load .env
load_dotenv(".test.env")
assert "OPENAI_API_KEY" in os.environ, "OPENAI_API_KEY is not set in the environment variables."


async def test_generate_answers(persona: str, n_questions: int) -> dict:
    questions_by_task = await test_generate_questions(persona=persona, n_questions=n_questions)

    results = await asyncio.gather(
        *(
            generate_answer_for_question({"persona": persona, "task": task, "question": question})
            for task, questions in questions_by_task.items()
            for question in questions
        )
    )

    answers_by_task: dict[str, list[tuple[str, str]]] = {task: [] for task in questions_by_task}
    for result in results:
        for task, qa_pairs in result["qa_by_task"].items():
            answers_by_task[task].extend(qa_pairs)
    return answers_by_task


if __name__ == "__main__":
    persona = "Asian software engineer"
    n_questions = 5
    answers = asyncio.run(test_generate_answers(persona=persona, n_questions=n_questions))
    print(json.dumps(answers, indent=2))
