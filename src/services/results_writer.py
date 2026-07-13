import json
from datetime import datetime, timezone
from pathlib import Path


def write_results(
    persona: str,
    task_scores: dict[str, float],
    overall_score: float,
    output_dir: Path | str = "results",
) -> Path:
    """Persist a benchmark run's scores to a timestamped JSON file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"benchmark_{timestamp}.json"
    payload = {
        "persona": persona,
        "task_scores": task_scores,
        "overall_score": overall_score,
        "generated_at": timestamp,
    }
    path.write_text(json.dumps(payload, indent=2))
    return path
