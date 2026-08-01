INVALID_TEST_ANSWERS_RESPONSE = {
    "success": False,
    "error": {
        "code": "INVALID_TEST_ANSWERS",
        "message": "심리테스트 답변을 올바르게 입력해주세요.",
    },
}
INVALID_SCHEDULE_RESPONSE = {
    "success": False,
    "error": {
        "code": "INVALID_SCHEDULE_DATA",
        "message": "일정 정보를 올바르게 입력해주세요.",
    },
}
USER_NOT_FOUND_RESPONSE = {
    "success": False,
    "error": {
        "code": "USER_NOT_FOUND",
        "message": "해당 사용자를 찾을 수 없습니다.",
    },
}
INVALID_TIME_RANGE_RESPONSE = {
    "success": False,
    "error": {
        "code": "INVALID_TIME_RANGE",
        "message": "시작 시간은 종료 시간보다 빨라야 합니다.",
    },
}
SCHEDULE_NOT_FOUND_RESPONSE = {
    "success": False,
    "error": {
        "code": "SCHEDULE_NOT_FOUND",
        "message": "해당 일정을 찾을 수 없습니다.",
    },
}
NO_UPDATE_FIELDS_RESPONSE = {
    "success": False,
    "error": {
        "code": "NO_UPDATE_FIELDS",
        "message": "수정할 항목을 입력해주세요.",
    },
}
INVALID_DATE_RANGE_RESPONSE = {
    "success": False,
    "error": {
        "code": "INVALID_DATE_RANGE",
        "message": "조회 기간은 31일 이내로 입력해주세요.",
    },
}
NO_SCHEDULES_RESPONSE = {
    "success": False,
    "error": {
        "code": "NO_SCHEDULES",
        "message": "해당 날짜에 등록된 일정이 없습니다.",
    },
}
INVALID_RECOVERY_REQUEST_RESPONSE = {
    "success": False,
    "error": {
        "code": "INVALID_RECOVERY_REQUEST",
        "message": "복구 계획 요청값을 올바르게 입력해주세요.",
    },
}
INVALID_PLAN_RESPONSE = {
    "success": False,
    "error": {
        "code": "INVALID_PLAN_DATA",
        "message": "최적화할 계획 정보를 올바르게 입력해주세요.",
    },
}
AI_NOT_CONFIGURED_RESPONSE = {
    "success": False,
    "error": {
        "code": "AI_NOT_CONFIGURED",
        "message": "AI 서비스가 설정되지 않았습니다.",
    },
}
AI_TIMEOUT_RESPONSE = {
    "success": False,
    "error": {
        "code": "AI_TIMEOUT",
        "message": "AI 서비스 응답 시간이 초과되었습니다.",
    },
}
AI_SERVICE_ERROR_RESPONSE = {
    "success": False,
    "error": {
        "code": "AI_SERVICE_ERROR",
        "message": "AI 서비스 요청을 처리하지 못했습니다.",
    },
}
AI_INVALID_OUTPUT_RESPONSE = {
    "success": False,
    "error": {
        "code": "AI_INVALID_OUTPUT",
        "message": "AI가 생성한 계획을 안전하게 검증하지 못했습니다.",
    },
}
DATABASE_UNAVAILABLE_RESPONSE = {
    "success": False,
    "error": {
        "code": "DB_UNAVAILABLE",
        "message": "데이터베이스 연결 상태를 확인해주세요.",
    },
}
