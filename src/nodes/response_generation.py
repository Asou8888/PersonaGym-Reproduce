from typing import TypedDict

from langchain_litellm import ChatLiteLLM

from src.config import RESPONSE_GENERATION_CONFIG
from src.prompts.persona import PERSONA_SYSTEM_PROMPT


class AnswerGenerationTask(TypedDict):
    persona: str
    task: str
    question: str


async def generate_answer_for_question(state: AnswerGenerationTask) -> dict:
    """Role-play the persona and answer a single question generated for one task."""
    model = ChatLiteLLM(**RESPONSE_GENERATION_CONFIG.to_kwargs())
    messages = [
        ("system", PERSONA_SYSTEM_PROMPT.format(persona=state["persona"])),
        ("human", state["question"]),
    ]
    response = await model.ainvoke(messages)
    return {"qa_by_task": {state["task"]: [(state["question"], response.content)]}}
