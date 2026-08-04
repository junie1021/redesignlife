import asyncio

import httpx
import pytest
from openai import APITimeoutError, OpenAIError

from backend.ai_schemas import RecoveryAIOutput
from backend.services import ai_service


class FakeParsedResponse:
    def __init__(self, output_parsed) -> None:
        self.output_parsed = output_parsed


class FakeResponses:
    def __init__(self, result=None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.kwargs = None

    async def parse(self, **kwargs):
        self.kwargs = kwargs
        if self.error is not None:
            raise self.error
        return FakeParsedResponse(self.result)


class FakeOpenAIClient:
    def __init__(self, responses: FakeResponses) -> None:
        self.responses = responses
        self.closed = False

    async def close(self) -> None:
        self.closed = True


def valid_recovery_output() -> RecoveryAIOutput:
    return RecoveryAIOutput(
        summary="요약",
        strengths=[],
        improvements=[],
        today_recovery_plan=[],
        move_to_tomorrow=[],
        advice="조언",
    )


def test_ai_service_uses_async_responses_structured_output(monkeypatch) -> None:
    parsed_output = valid_recovery_output()
    responses = FakeResponses(result=parsed_output)
    client = FakeOpenAIClient(responses)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setattr(ai_service, "AsyncOpenAI", lambda **_: client)
    service = ai_service.AIService()

    result = asyncio.run(service.generate_recovery({"date": "2026-08-02"}))

    assert result is parsed_output
    assert responses.kwargs["model"] == "gpt-5-mini"
    assert responses.kwargs["text_format"] is RecoveryAIOutput
    assert client.closed is True


@pytest.mark.parametrize(
    ("sdk_error", "service_error"),
    [
        (
            APITimeoutError(request=httpx.Request("POST", "https://api.openai.com")),
            ai_service.AIServiceTimeoutError,
        ),
        (OpenAIError("service failed"), ai_service.AIServiceError),
    ],
)
def test_ai_service_maps_sdk_errors(monkeypatch, sdk_error, service_error) -> None:
    client = FakeOpenAIClient(FakeResponses(error=sdk_error))
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(ai_service, "AsyncOpenAI", lambda **_: client)
    service = ai_service.AIService()

    with pytest.raises(service_error):
        asyncio.run(service.generate_recovery({"date": "2026-08-02"}))

    assert client.closed is True
