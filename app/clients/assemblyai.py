import asyncio

import httpx

from app.models import TranscriptResponse, Utterance

ASSEMBLYAI_BASE_URL = "https://api.assemblyai.com/v2"
MAX_POLLING_ATTEMPTS = 150
POLL_INTERVAL_SECONDS = 2


class AssemblyAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    @property
    def _headers(self) -> dict[str, str]:
        return {"authorization": self.api_key}

    async def transcribe(self, audio_bytes: bytes, speaker_labels: bool = True) -> TranscriptResponse:
        async with httpx.AsyncClient(timeout=60.0) as client:
            upload_resp = await client.post(
                f"{ASSEMBLYAI_BASE_URL}/upload",
                content=audio_bytes,
                headers=self._headers,
            )
            upload_resp.raise_for_status()
            upload_url = upload_resp.json()["upload_url"]

            transcript_resp = await client.post(
                f"{ASSEMBLYAI_BASE_URL}/transcript",
                json={"audio_url": upload_url, "speaker_labels": speaker_labels},
                headers=self._headers,
            )
            transcript_resp.raise_for_status()
            transcript_id = transcript_resp.json()["id"]

            polls = 0
            while polls < MAX_POLLING_ATTEMPTS:
                polls += 1
                poll_resp = await client.get(
                    f"{ASSEMBLYAI_BASE_URL}/transcript/{transcript_id}",
                    headers=self._headers,
                )
                poll_resp.raise_for_status()
                payload = poll_resp.json()
                status = payload.get("status")
                if status == "completed":
                    utterances = [
                        Utterance(
                            speaker=f"speaker_{item.get('speaker', 'unknown')}",
                            text=item.get("text", ""),
                            start_ms=item.get("start", 0),
                            end_ms=item.get("end", 0),
                        )
                        for item in payload.get("utterances", [])
                    ]
                    return TranscriptResponse(utterances=utterances)
                if status == "error":
                    raise RuntimeError(payload.get("error", "AssemblyAI transcription failed"))
                await asyncio.sleep(POLL_INTERVAL_SECONDS)
            raise RuntimeError("Transcription timed out after 5 minutes")
