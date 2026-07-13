from langgraph.types import Send

from src_v2.config import EVALUATION_BATCH_SIZE
from src_v2.data.evaluation_tasks import EVALUATION_TASK_REQUIREMENTS
from src_v2.graph.state import BenchmarkState
from src_v2.nodes.question_generation import QuestionGenerationTask
from src_v2.nodes.response_evaluation import EvaluationBatchTask
from src_v2.nodes.response_generation import AnswerGenerationTask


def dispatch_question_generation(state: BenchmarkState) -> list[Send]:
    """Fan out one question-generation call per evaluation task."""
    return [
        Send(
            "generate_questions_for_task",
            QuestionGenerationTask(
                persona=state["persona"],
                settings=state["settings"],
                task=task,
                requirements=requirements,
                n_questions=state["n_questions"],
            ),
        )
        for task, requirements in EVALUATION_TASK_REQUIREMENTS.items()
    ]


def dispatch_response_generation(state: BenchmarkState) -> list[Send]:
    """Fan out one persona role-play call per generated question, across all tasks."""
    return [
        Send(
            "generate_answer_for_question",
            AnswerGenerationTask(
                persona=state["persona"],
                task=task,
                question=question,
            ),
        )
        for task, questions in state["questions_by_task"].items()
        for question in questions
    ]


def dispatch_response_evaluation(state: BenchmarkState) -> list[Send]:
    """Fan out one judging call per batch of `EVALUATION_BATCH_SIZE` answers, per task."""
    sends = []
    for task, qa_pairs in state["qa_by_task"].items():
        for start in range(0, len(qa_pairs), EVALUATION_BATCH_SIZE):
            batch = qa_pairs[start : start + EVALUATION_BATCH_SIZE]
            sends.append(
                Send(
                    "evaluate_batch",
                    EvaluationBatchTask(
                        persona=state["persona"],
                        task=task,
                        qa_pairs=batch,
                    ),
                )
            )
    return sends
