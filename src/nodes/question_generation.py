from typing import List, TypedDict

from langchain_litellm import ChatLiteLLM

from src.config import QUESTION_GENERATION_CONFIG
from src.models.schemas import GeneratedQuestions
from src.prompts.question_generation import QUESTION_GENERATION_PROMPT


class QuestionGenerationTask(TypedDict):
    persona: str
    settings: List[str]
    task: str
    requirements: str
    n_questions: int


async def generate_questions_for_task(state: QuestionGenerationTask) -> dict:
    """Generate the challenge questions for a single evaluation task (e.g. Toxicity)."""
    model = (
        ChatLiteLLM(**QUESTION_GENERATION_CONFIG.to_kwargs())
        .with_structured_output(GeneratedQuestions)
        .with_retry(stop_after_attempt=3)
    )
    prompt = QUESTION_GENERATION_PROMPT.format(
        settings=state["settings"],
        num_questions=state["n_questions"],
        persona=state["persona"],
        task=state["task"],
        description=state["requirements"],
    )
    result: GeneratedQuestions = await model.ainvoke(prompt)
    return {"questions_by_task": {state["task"]: result.questions}}
