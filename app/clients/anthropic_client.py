import asyncio

import httpx

from app.config import settings
from app.models import AnalysisResult
from app.prompting import build_analysis_prompt, extract_json_object

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
MAX_ATTEMPTS = 2
RETRY_DELAY_SECONDS = 3
ANTHROPIC_OVERLOAD_STATUS_CODE = 529


class AnthropicClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    async def analyze_transcript(self, transcript: str) -> AnalysisResult:
        payload = {
            "model": settings.anthropic_model,
            "max_tokens": 1800,
            "temperature": 0,
            "messages": [{"role": "user", "content": build_analysis_prompt(transcript)}],
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            for attempt in range(MAX_ATTEMPTS):
                try:
                    response = await client.post(ANTHROPIC_URL, headers=self._headers, json=payload)
                    response.raise_for_status()
                    break
                except httpx.HTTPStatusError as exc:
                    if attempt == MAX_ATTEMPTS - 1 or exc.response.status_code != ANTHROPIC_OVERLOAD_STATUS_CODE:
                        raise
                    await asyncio.sleep(RETRY_DELAY_SECONDS)

        data = response.json()
        content = data.get("content", [])
        text_blocks = [item.get("text", "") for item in content if item.get("type") == "text"]
        combined_text = "\n".join(text_blocks)

        structured = extract_json_object(combined_text)
        return AnalysisResult.model_validate(structured)
