from pydantic import BaseModel, Field


class Utterance(BaseModel):
    speaker: str
    text: str
    start_ms: int = Field(ge=0)
    end_ms: int = Field(ge=0)


class TranscriptResponse(BaseModel):
    utterances: list[Utterance]


class InterruptionEvent(BaseModel):
    interrupter: str
    interrupted: str
    timestamp: str
    snippet: str


class IdeaAttributionEvent(BaseModel):
    original_speaker: str
    repeater: str
    idea_summary: str
    confidence: float = Field(ge=0, le=1)


class IgnoredContribution(BaseModel):
    speaker: str
    contribution: str
    response: str


class AnalysisResult(BaseModel):
    talk_time: dict[str, float]
    interruptions: list[InterruptionEvent]
    idea_theft: list[IdeaAttributionEvent]
    ignored_contributions: list[IgnoredContribution]
    question_equity: dict
    summary_narrative: str
    nudges: list[str]


class AnalyzeRequest(BaseModel):
    utterances: list[Utterance]
    speaker_labels: dict[str, str] = Field(default_factory=dict)
