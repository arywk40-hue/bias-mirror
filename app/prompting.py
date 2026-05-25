import json
import re

from app.models import AnalyzeRequest


def apply_speaker_labels(request: AnalyzeRequest) -> str:
    lines: list[str] = []
    for u in request.utterances:
        label = request.speaker_labels.get(u.speaker, u.speaker)
        timestamp = f"{u.start_ms / 1000:.1f}s"
        lines.append(f"[{timestamp}] {label}: {u.text}")
    return "\n".join(lines)


def build_analysis_prompt(transcript: str) -> str:
    return (
        "You are an organizational psychology expert analyzing a meeting transcript "
        "for participation equity. The transcript has speaker labels.\n\n"
        "Analyze and return STRICT JSON with keys:\n"
        "1. talk_time: { speaker: seconds }\n"
        "2. interruptions: [ { interrupter, interrupted, timestamp, snippet } ]\n"
        "3. idea_theft: [ { original_speaker, repeater, idea_summary, confidence } ]\n"
        "4. ignored_contributions: [ { speaker, contribution, response: \"none/minimal/acknowledged\" } ]\n"
        "5. question_equity: { questions_asked_to: { speaker: count } }\n"
        "6. summary_narrative: \"2-3 sentence plain-English team dynamics summary\"\n"
        "7. nudges: [\"3 actionable suggestions for the next meeting\"]\n\n"
        "Do not wrap JSON in markdown fences and do not include extra keys.\n\n"
        f"Transcript:\n{transcript}"
    )


def extract_json_object(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\\s*", "", text)
        text = re.sub(r"\\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model response")

    return json.loads(text[start : end + 1])
