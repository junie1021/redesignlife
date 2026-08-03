import json
import os
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from openai import APITimeoutError, AsyncOpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

from ..ai_schemas import DailyAnalysisAIOutput, OptimizeAIOutput, RecoveryAIOutput


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

StructuredOutput = TypeVar("StructuredOutput", bound=BaseModel)


class AINotConfiguredError(RuntimeError):
    pass


class AIServiceTimeoutError(RuntimeError):
    pass


class AIServiceError(RuntimeError):
    pass


class AIOutputValidationError(RuntimeError):
    pass


class AIService:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-5.6")

    async def _generate(
        self,
        output_model: type[StructuredOutput],
        instructions: str,
        context: dict[str, object],
    ) -> StructuredOutput:
        if not self.api_key:
            raise AINotConfiguredError

        client = AsyncOpenAI(api_key=self.api_key, timeout=30.0, max_retries=0)
        try:
            response = await client.responses.parse(
                model=self.model,
                instructions=instructions,
                input=json.dumps(context, ensure_ascii=False),
                text_format=output_model,
            )
        except APITimeoutError as exc:
            raise AIServiceTimeoutError from exc
        except ValidationError as exc:
            raise AIOutputValidationError from exc
        except OpenAIError as exc:
            raise AIServiceError from exc
        finally:
            await client.close()

        parsed = response.output_parsed
        if parsed is None:
            raise AIOutputValidationError
        return parsed

    async def generate_recovery(
        self,
        context: dict[str, object],
    ) -> RecoveryAIOutput:
        instructions = (
            "당신은 사용자를 비난하지 않는 현실적인 일정 관리 코치입니다. "
            "제공된 사용자 유형을 낙인처럼 단정하지 말고 참고만 하세요. "
            "현재 시각 이후의 실행 가능한 짧은 복구 계획을 한국어로 제안하세요. "
            "제공된 일정 ID만 source_schedule_id로 사용하고, 새 ID를 만들지 마세요. "
            "기존 FIXED 일정과 겹치지 않으며 복구 계획끼리도 겹치지 않게 하세요."
        )
        return await self._generate(RecoveryAIOutput, instructions, context)

    async def analyze_day(
        self,
        context: dict[str, object],
    ) -> DailyAnalysisAIOutput:
        instructions = (
            "당신은 사용자의 하루를 평가하는 비판단적 일정 코치입니다. "
            "완료 여부, 계획 시간, 만족도, 일정 유형과 사용자 성향을 근거로 "
            "0~100점과 짧고 구체적인 한국어 분석을 제공하세요."
        )
        return await self._generate(DailyAnalysisAIOutput, instructions, context)

    async def optimize_plan(
        self,
        context: dict[str, object],
        retry_feedback: str | None = None,
    ) -> OptimizeAIOutput:
        instructions = (
            "당신은 사용자를 비난하지 않는 현실적인 일정 관리 코치입니다. "
            "입력된 할 일만 사용해 한국어 계획을 제안하세요. 일정 사이 휴식을 고려하고, "
            "사용 가능 시간과 기존 FIXED 일정을 침범하지 마세요. 시간을 줄이지 말고 "
            "배치할 수 없는 일은 unscheduled_tasks에 넣으세요. 모든 생성 일정의 "
            "schedule_type은 ADJUSTABLE이어야 합니다."
        )
        if retry_feedback:
            instructions += f" 이전 결과 검증 실패를 수정하세요: {retry_feedback}"
        return await self._generate(OptimizeAIOutput, instructions, context)


def get_ai_service() -> AIService:
    return AIService()
