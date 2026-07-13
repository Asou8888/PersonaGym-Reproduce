from pydantic import BaseModel, Field
from typing import List


class SettingSelection(BaseModel):
    settings: List[str] = Field(
        description="Settings selected from the catalog that best fit the persona."
    )


class GeneratedQuestions(BaseModel):
    questions: List[str] = Field(
        description="Challenging multi-step questions posed directly to the persona."
    )


class ScoreExampleSet(BaseModel):
    score_1: str = Field(description="Example response that would earn a score of 1.")
    score_2: str = Field(description="Example response that would earn a score of 2.")
    score_3: str = Field(description="Example response that would earn a score of 3.")
    score_4: str = Field(description="Example response that would earn a score of 4.")
    score_5: str = Field(description="Example response that would earn a score of 5.")

    def as_list(self) -> List[str]:
        return [self.score_1, self.score_2, self.score_3, self.score_4, self.score_5]


class ScoreExampleBatch(BaseModel):
    examples: List[ScoreExampleSet] = Field(
        description="One example set per question, in the same order as the questions were given."
    )


class RubricEvaluation(BaseModel):
    reasoning: str = Field(description="Justification for the assigned score.")
    score: int = Field(ge=1, le=5, description="Final score from 1 (worst) to 5 (best).")


class BatchEvaluation(BaseModel):
    evaluations: List[RubricEvaluation] = Field(
        description="One evaluation per rubric, in the same order as the rubrics were given."
    )
