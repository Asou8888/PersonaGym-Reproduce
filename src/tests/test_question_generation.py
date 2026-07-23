import asyncio
import json
import os

from dotenv import load_dotenv

from src.data.evaluation_tasks import EVALUATION_TASK_REQUIREMENTS
from src.nodes.question_generation import generate_questions_for_task
from srcs.nodes.setting_selection import select_settings

# Load .env
load_dotenv(".test.env")
assert "OPENAI_API_KEY" in os.environ, "OPENAI_API_KEY is not set in the environment variables."


async def test_generate_questions(persona: str, n_questions: int) -> dict:
    settings_update = await select_settings({"persona": persona})
    settings = settings_update["settings"]

    results = await asyncio.gather(
        *(
            generate_questions_for_task(
                {
                    "persona": persona,
                    "settings": settings,
                    "task": task,
                    "requirements": requirements,
                    "n_questions": n_questions,
                }
            )
            for task, requirements in EVALUATION_TASK_REQUIREMENTS.items()
        )
    )
    return {
        task: result["questions_by_task"][task]
        for task, result in zip(EVALUATION_TASK_REQUIREMENTS, results)
    }


if __name__ == "__main__":
    persona = "Asian software engineer"
    n_questions = 5
    questions = asyncio.run(test_generate_questions(persona=persona, n_questions=n_questions))
    print(json.dumps(questions, indent=2))
