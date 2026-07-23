import asyncio
import os

from dotenv import load_dotenv

from src.graph.state import BenchmarkState
from src.nodes.setting_selection import select_settings

# Load .env
load_dotenv(".test.env")
assert "OPENAI_API_KEY" in os.environ, "OPENAI_API_KEY is not set in the environment variables."


async def test_select_settings(persona: str) -> list[str]:
    state: BenchmarkState = {"persona": persona}
    result = await select_settings(state)
    return result["settings"]


if __name__ == "__main__":
    persona = "Asian software engineer"
    settings = asyncio.run(test_select_settings(persona=persona))
    print(settings)
