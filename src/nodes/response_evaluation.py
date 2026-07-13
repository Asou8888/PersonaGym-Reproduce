import asyncio
from typing import TypedDict
from langchain_litellm import ChatLiteLLM

from src_v2.config import RESPONSE_EVALUATION_EXAMPLE_CONFIG, RESPONSE_EVALUATION_JUDGE_CONFIGS
from src_v2.models.schemas import BatchEvaluation, ScoreExampleBatch, ScoreExampleSet
from src_v2.prompts.response_evaluation import (
    BATCH_EVALUATION_PROMPT,
    RUBRIC_SYSTEM_PROMPT,
    RUBRICS_BY_TASK,
    SCORE_EXAMPLE_GENERATION_PROMPT,
)
from src_v2.utils.aggregation import average


class EvaluationBatchTask(TypedDict):
    persona: str
    task: str
    qa_pairs: list[tuple[str, str]]


def _format_score_example(example: ScoreExampleSet) -> str:
    labels = ["Score 1", "Score 2", "Score 3", "Score 4", "Score 5"]
    return "\n\n".join(
        f"{label}: Response - {text}" for label, text in zip(labels, example.as_list())
    )


async def _generate_score_examples(
    persona: str, qa_pairs: list[tuple[str, str]], rubric: str
) -> ScoreExampleBatch:
    example_model = (
        ChatLiteLLM(**RESPONSE_EVALUATION_EXAMPLE_CONFIG.to_kwargs())
        .with_structured_output(ScoreExampleBatch)
        .with_retry(stop_after_attempt=3)
    )
    questions_block = "\n".join(f"{i + 1}. {question}" for i, (question, _) in enumerate(qa_pairs))
    prompt = SCORE_EXAMPLE_GENERATION_PROMPT.format(
        persona=persona, questions=questions_block, rubric=rubric
    )
    return await example_model.ainvoke(prompt)


async def _evaluate_with_model(combined_prompt: str, judge_model) -> float:
    result: BatchEvaluation = await judge_model.ainvoke(
        [("system", RUBRIC_SYSTEM_PROMPT), ("human", combined_prompt)]
    )
    return average([evaluation.score for evaluation in result.evaluations])


async def evaluate_batch(state: EvaluationBatchTask) -> dict:
    """Score a batch of up to `EVALUATION_BATCH_SIZE` (question, answer) pairs for one task.

    Steps: generate calibration examples for each score level, build one combined
    rubric prompt for the batch, then judge it with every configured eval model in
    parallel and average their scores.
    """
    # Generate score examples
    persona = state["persona"]
    task = state["task"]
    qa_pairs = state["qa_pairs"]
    rubric = RUBRICS_BY_TASK[task]
    example_batch = await _generate_score_examples(persona, qa_pairs, rubric)

    # Judge the models
    judge_models = [
        ChatLiteLLM(**judge_config.to_kwargs())
        .with_structured_output(BatchEvaluation)
        .with_retry(stop_after_attempt=3)
        for judge_config in RESPONSE_EVALUATION_JUDGE_CONFIGS
    ]
    rubric_prompts = [
        rubric.format(
            persona=persona,
            question=question,
            response=answer,
            score_example=_format_score_example(example),
        )
        for (question, answer), example in zip(qa_pairs, example_batch.examples)
    ]
    combined_prompt = BATCH_EVALUATION_PROMPT.format(rubrics="\n\n".join(rubric_prompts))

    batch_scores = await asyncio.gather(
        *(_evaluate_with_model(combined_prompt, judge_model) for judge_model in judge_models)
    )
    return {"batch_scores_by_task": {task: [average(list(batch_scores))]}}
