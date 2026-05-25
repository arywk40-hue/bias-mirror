# bias-mirror

FastAPI backend for a meeting equity auditor.

## What this implements now
- Audio file transcription endpoint using AssemblyAI speaker diarization
- Transcript analysis endpoint using Claude (`claude-sonnet-4-20250514` by default)
- Structured equity report JSON output

## Quickstart

```bash
cd bias-mirror
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
export ASSEMBLYAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
uvicorn app.main:app --reload
```

## Endpoints

- `GET /health`
- `POST /api/transcribe` (multipart form with `file`)
- `POST /api/analyze` (JSON body with diarized utterances)
- `POST /api/report` (alias of analyze)

### Analyze payload example

```json
{
  "utterances": [
    { "speaker": "speaker_A", "text": "Let's start.", "start_ms": 0, "end_ms": 1000 },
    { "speaker": "speaker_B", "text": "I have an idea.", "start_ms": 1200, "end_ms": 3500 }
  ],
  "speaker_labels": {
    "speaker_A": "Alex",
    "speaker_B": "Jordan"
  }
}
```

## Notes
- Recall.ai meeting bot integration can be added as the next step by posting captured audio to `/api/transcribe`.
- In hackathon mode, this backend supports file-upload demos immediately.
