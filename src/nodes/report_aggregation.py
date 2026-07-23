from src.graph.state import BenchmarkState
from src.utils.aggregation import average


def aggregate_scores(state: BenchmarkState) -> dict:
    """Collapse per-batch scores into one score per task and an overall average."""
    task_scores = {
        task: average(scores)
        for task, scores in state["batch_scores_by_task"].items()
        if scores
    }
    overall_score = average(list(task_scores.values()))
    return {"task_scores": task_scores, "overall_score": overall_score}
