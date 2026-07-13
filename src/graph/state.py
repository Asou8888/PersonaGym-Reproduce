from typing import Annotated, TypedDict


def merge_dicts(left: dict | None, right: dict | None) -> dict:
    """Reducer for state keys where each parallel branch owns disjoint keys."""
    merged = dict(left or {})
    merged.update(right or {})
    return merged


def merge_list_dicts(
    left: dict[str, list] | None, right: dict[str, list] | None
) -> dict[str, list]:
    """Reducer for state keys where multiple parallel branches append to the same key."""
    merged = {key: list(values) for key, values in (left or {}).items()}
    for key, values in (right or {}).items():
        merged.setdefault(key, [])
        merged[key].extend(values)
    return merged


class BenchmarkState(TypedDict):
    """Shared state threaded through the persona-consistency benchmark graph."""

    persona: str
    n_questions: int

    settings: list[str]
    questions_by_task: Annotated[dict[str, list[str]], merge_dicts]
    qa_by_task: Annotated[dict[str, list[tuple[str, str]]], merge_list_dicts]
    batch_scores_by_task: Annotated[dict[str, list[float]], merge_list_dicts]

    task_scores: dict[str, float]
    overall_score: float
