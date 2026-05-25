from app.models import AnalyzeRequest, Utterance
from app.prompting import apply_speaker_labels, extract_json_object


def test_apply_speaker_labels_uses_mapping():
    payload = AnalyzeRequest(
        utterances=[
            Utterance(speaker="speaker_A", text="I think we should ship this.", start_ms=0, end_ms=1200)
        ],
        speaker_labels={"speaker_A": "Alex"},
    )

    transcript = apply_speaker_labels(payload)
    assert "Alex" in transcript
    assert "speaker_A" not in transcript


def test_extract_json_object_parses_fenced_json():
    raw = "```json\n{\"talk_time\": {\"Alex\": 10}, \"interruptions\": [], \"idea_theft\": [], \"ignored_contributions\": [], \"question_equity\": {}, \"summary_narrative\": \"ok\", \"nudges\": []}\n```"
    obj = extract_json_object(raw)
    assert obj["talk_time"]["Alex"] == 10
