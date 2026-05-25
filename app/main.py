from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.clients.anthropic_client import AnthropicClient
from app.clients.assemblyai import AssemblyAIClient
from app.config import settings
from app.models import AnalysisResult, AnalyzeRequest, TranscriptResponse
from app.prompting import apply_speaker_labels

app = FastAPI(title="Bias Mirror API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/transcribe", response_model=TranscriptResponse)
async def transcribe(file: UploadFile = File(...), speaker_labels: bool = True) -> TranscriptResponse:
    if not settings.assemblyai_api_key:
        raise HTTPException(status_code=500, detail="ASSEMBLYAI_API_KEY is not configured")

    audio = await file.read()
    client = AssemblyAIClient(api_key=settings.assemblyai_api_key)
    try:
        return await client.transcribe(audio_bytes=audio, speaker_labels=speaker_labels)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Transcription failed: {exc}") from exc


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze(request: AnalyzeRequest) -> AnalysisResult:
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY is not configured")

    transcript = apply_speaker_labels(request)
    client = AnthropicClient(api_key=settings.anthropic_api_key)
    try:
        return await client.analyze_transcript(transcript=transcript)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Analysis failed: {exc}") from exc


@app.post("/api/report", response_model=AnalysisResult)
async def report(request: AnalyzeRequest) -> AnalysisResult:
    # Kept as a stable external route name for frontend integrations.
    return await analyze(request)
