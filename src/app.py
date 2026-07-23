import argparse
import asyncio
import json

from src.config import DEFAULT_N_QUESTIONS
from src.graph.builder import build_benchmark_graph
from src.services.persona_dataset import get_sample_persona
from src.services.results_writer import write_results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the PersonaGym persona-consistency benchmark for a single persona."
    )
    persona_group = parser.add_mutually_exclusive_group(required=True)
    persona_group.add_argument(
        "persona", nargs="?", help="Natural-language description of the persona to evaluate."
    )
    persona_group.add_argument(
        "--sample-index",
        type=int,
        help="Pick a persona from the bundled sample dataset instead of typing one out.",
    )
    parser.add_argument(
        "--n-questions",
        type=int,
        default=DEFAULT_N_QUESTIONS,
        help="Questions generated per evaluation task.",
    )
    parser.add_argument(
        "--output-dir", default="results", help="Directory to write the JSON results file to."
    )
    return parser.parse_args()


async def run_benchmark(persona: str, n_questions: int) -> dict:
    graph = build_benchmark_graph()
    return await graph.ainvoke({"persona": persona, "n_questions": n_questions})


def main() -> None:
    args = parse_args()
    persona = get_sample_persona(args.sample_index) if args.sample_index is not None else args.persona

    final_state = asyncio.run(run_benchmark(persona, args.n_questions))

    print(f"Persona: {persona}")
    print(f"Overall Score: {final_state['overall_score']:.2f}")
    print(json.dumps(final_state["task_scores"], indent=2))

    output_path = write_results(
        persona=persona,
        task_scores=final_state["task_scores"],
        overall_score=final_state["overall_score"],
        output_dir=args.output_dir,
    )
    print(f"Results written to {output_path}")


if __name__ == "__main__":
    main()
