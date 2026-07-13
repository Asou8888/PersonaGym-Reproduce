from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src_v2.graph.routing import (
    dispatch_question_generation,
    dispatch_response_evaluation,
    dispatch_response_generation,
)
from src_v2.graph.state import BenchmarkState
from src_v2.nodes.question_generation import generate_questions_for_task
from src_v2.nodes.report_aggregation import aggregate_scores
from src_v2.nodes.response_evaluation import evaluate_batch
from src_v2.nodes.response_generation import generate_answer_for_question
from src_v2.nodes.setting_selection import select_settings


def _barrier(state: BenchmarkState) -> dict:
    """No-op join node.

    A conditional edge attached directly to a Send-fanned-out node only ever sees
    that one branch's local view, not the state merged across all sibling branches.
    Routing a fan-out's parallel branches through a plain (non-conditional) edge into
    one of these barrier nodes forces LangGraph to wait for every branch and merge
    their writes before the *next* fan-out's routing function runs, so that function
    sees the fully accumulated state (e.g. all tasks' questions, not just one task's).
    """
    return {}


def build_benchmark_graph() -> CompiledStateGraph:
    """Wire the PersonaGym pipeline as a LangGraph map-reduce graph:

    select_settings -> generate_questions_for_task (fan-out per task)
                     -> generate_answer_for_question (fan-out per question)
                     -> evaluate_batch (fan-out per batch of answers)
                     -> aggregate_scores
    """
    graph = StateGraph(BenchmarkState)

    graph.add_node("select_settings", select_settings)
    graph.add_node("generate_questions_for_task", generate_questions_for_task)
    graph.add_node("questions_ready", _barrier)
    graph.add_node("generate_answer_for_question", generate_answer_for_question)
    graph.add_node("answers_ready", _barrier)
    graph.add_node("evaluate_batch", evaluate_batch)
    graph.add_node("aggregate_scores", aggregate_scores)

    graph.add_edge(START, "select_settings")
    graph.add_conditional_edges(
        "select_settings", dispatch_question_generation, ["generate_questions_for_task"]
    )
    graph.add_edge("generate_questions_for_task", "questions_ready")
    graph.add_conditional_edges(
        "questions_ready",
        dispatch_response_generation,
        ["generate_answer_for_question"],
    )
    graph.add_edge("generate_answer_for_question", "answers_ready")
    graph.add_conditional_edges(
        "answers_ready", dispatch_response_evaluation, ["evaluate_batch"]
    )
    graph.add_edge("evaluate_batch", "aggregate_scores")
    graph.add_edge("aggregate_scores", END)

    return graph.compile()
