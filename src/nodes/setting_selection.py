from langchain_litellm import ChatLiteLLM

from src.config import SETTING_SELECTION_CONFIG
from src.data.settings_catalog import SETTINGS_CATALOG
from src.graph.state import BenchmarkState
from src.models.schemas import SettingSelection
from src.prompts.setting_selection import SETTING_SELECTION_PROMPT


async def select_settings(state: BenchmarkState) -> dict:
    """Pick the settings from the catalog that are most relevant to the persona."""
    model = (
        ChatLiteLLM(**SETTING_SELECTION_CONFIG.to_kwargs())
        .with_structured_output(SettingSelection)
        .with_retry(stop_after_attempt=3)
    )
    prompt = SETTING_SELECTION_PROMPT.format(
        persona=state["persona"], settings_catalog=SETTINGS_CATALOG
    )
    result: SettingSelection = await model.ainvoke(prompt)
    return {"settings": result.settings}
