from src_v2.data.sample_personas import SAMPLE_PERSONAS


def list_sample_personas() -> list[str]:
    return list(SAMPLE_PERSONAS)


def get_sample_persona(index: int) -> str:
    return SAMPLE_PERSONAS[index]
