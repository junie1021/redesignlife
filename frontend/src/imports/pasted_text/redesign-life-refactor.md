Please refactor and reorganize the existing RedesignLife web service based on the current implementation.

IMPORTANT:
Do NOT completely redesign the existing UI from scratch.
Preserve the current visual design system, styling, components, interactions, and overall visual quality as much as possible.

The current design system is:
- Warm cream background: #FFFAF6
- Primary coral orange: #FF6B47
- Noto Sans KR for Korean text
- Rounded cards
- Friendly, warm, playful AI lifestyle service
- Category-based colors
- Gradient CTA sections
- Responsive desktop web layout
- 1440 × 1024 desktop design 기준

The current service should now be reorganized into exactly THREE major sections.

==================================================
OVERALL SERVICE STRUCTURE
==================================================

SECTION 1. 나의 유형 알아보기
→ Personality Quiz + Personality Type Result

SECTION 2. 오늘 하루 AI 분석
→ Today's Task List + Timeline + AI Day Analysis

SECTION 3. AI와 내일 계획하기
→ Tomorrow Planning + Fixed/Adjustable Schedule + AI Recommendations

The overall user journey should communicate:

"나를 이해하기"
→ "오늘을 돌아보기"
→ "내일을 다시 설계하기"

The navigation should clearly show these three sections.

Use a consistent top navigation:
1. 나의 유형 알아보기
2. 오늘 하루 AI 분석
3. AI와 내일 계획하기

Users can freely navigate between sections for hackathon demo purposes, but the primary recommended flow should be Section 1 → Section 2 → Section 3.

==================================================
SECTION 1. 나의 유형 알아보기
PERSONALITY QUIZ + RESULT COMBINED
==================================================

Combine the existing Quiz and Result into ONE unified section.

Keep the existing 4-question sequential personality quiz.

Existing functionality to preserve:
- 4 questions
- Progress dots
- "X / 4" progress indicator
- 2×2 answer card grid
- Orange highlight and check indicator when an answer is selected
- Previous / Next buttons
- Next button disabled until an answer is selected
- Automatically move to the result after the final question

After completing the 4 questions, show the personality type result within the SAME section.

Keep the existing four personality types and their unique visual themes:

1. 완벽주의 나무늘보
2. 도파민 청개구리
3. 과부하 개미
4. 걱정인형

Keep:
- Unique color theme for each personality
- Emoji mascot
- Personality type name
- Tagline
- "이런 특징이 있어요" numbered list

Improve the transition between the quiz and result.

The result should feel like the natural conclusion of the quiz, not like a separate unrelated page.

Add a primary CTA:
"오늘 하루 돌아보기"

This CTA should navigate to Section 2.

The final structure should be:

Section 1
┌──────────────────────────┐
│ Personality Quiz         │
│ Q1 → Q2 → Q3 → Q4       │
└────────────┬─────────────┘
             ↓
┌──────────────────────────┐
│ My Personality Result    │
│ Type + Mascot + Traits   │
└────────────┬─────────────┘
             ↓
       오늘 하루 돌아보기

==================================================
SECTION 2. 오늘 하루 AI 분석
TODAY'S TASKS + TIMELINE + AI ANALYSIS
==================================================

Reorganize the existing "어제의 할 일 목록" into "오늘 할 일 목록".

The page should appear in this order:

1. 오늘 할 일 목록
2. 하루 타임라인
3. AI의 하루 분석 보기 CTA
4. AI 분석 결과

-----------------------------------
2-1. 오늘 할 일 목록
-----------------------------------

Keep the existing 5-column task table.

Columns:
1. 완료 여부
2. 할 일
3. 시작 시간
4. 끝 시간
5. 카테고리
6. 만족도
7. 일정 유형

Add one important new column:

"일정 유형"

The user must be able to choose whether each task is:

🔒 고정 일정
or
🔄 AI 조정 가능

Use a clear toggle, segmented control, dropdown, or visual badge.

The meaning must be immediately understandable.

🔒 고정 일정:
"AI가 시간과 내용을 변경하지 않는 일정"
Examples:
- 수업
- 시험
- 병원 예약
- 회의
- 팀플
- 약속

🔄 AI 조정 가능:
"AI가 시간, 순서, 소요 시간 등을 제안할 수 있는 일정"
Examples:
- 공부
- 과제
- 운동
- 휴식
- 자기계발
- 개인 업무

Show the selected status as a clear badge in each row.

For example:

🔒 고정
🔄 AI 조정 가능

Use a subtle visual distinction:
- Fixed schedule: stable, neutral, trustworthy appearance
- AI-adjustable schedule: flexible, collaborative appearance

The user should be able to change this setting directly in the task table.

Keep existing functionality:
- Clickable completion checkbox
- Completed row changes to light green
- Completed task text gets strikethrough
- Start/end time input using native time picker
- AI category badge
- Automatic category classification
- 5-star interactive satisfaction rating
- Add/edit task functionality if already implemented

-----------------------------------
2-2. 하루 타임라인
-----------------------------------

Keep the existing timeline visualization.

Requirements:
- 06:00–24:00 horizontal time axis
- Time blocks rendered according to start/end time
- Category-based colors
- Start/end time displayed inside blocks
- "시간 미입력" message when time is missing
- Legend only for categories currently used
- Timeline updates immediately when table times are edited

Additionally, visually distinguish:
- 🔒 Fixed schedules
- 🔄 AI-adjustable schedules

For fixed schedule blocks, show a small lock icon.
For AI-adjustable blocks, show a small AI/flexible icon.

-----------------------------------
2-3. AI의 하루 분석 보기
-----------------------------------

After the user finishes entering today's tasks and timeline, show a prominent CTA card:

"할 일 목록과 타임라인 입력이 끝났다면
AI가 오늘 하루를 분석해볼까요?"

Button:
"AI의 하루 분석 보기"

Use the existing purple gradient button style.

When clicked, reveal the AI analysis results below.

Once opened, the AI analysis should remain visible and should not automatically collapse.

-----------------------------------
2-4. AI 분석 결과
-----------------------------------

Keep the existing analysis UI:

1. Today's day score shown with a circular gauge
2. Planned vs completed task comparison
3. Additional completed tasks if any
4. 오늘의 문제
5. AI 행동 패턴
6. 내일을 위한 변화

Use structured insight cards.

The AI analysis should consider:
- User's personality type from Section 1
- Today's planned tasks
- Completed tasks
- Completion rate
- Satisfaction ratings
- Time usage
- Categories
- Fixed vs AI-adjustable schedule status

Important:
Fixed schedules should be considered as constraints when analyzing the day.
AI-adjustable schedules can be analyzed for potential behavioral improvements.

Add a CTA at the end:
"AI와 내일 계획하기"

This CTA navigates to Section 3.

==================================================
SECTION 3. AI와 내일 계획하기
TOMORROW PLANNING WITH AI
==================================================

This section is the most important personalized planning feature.

The user creates tomorrow's schedule and collaborates with AI.

The AI should NOT freely modify every task.

Every task must include the same schedule type setting:

🔒 고정 일정
🔄 AI 조정 가능

-----------------------------------
3-1. 내일 계획 테이블
-----------------------------------

Create a planning table similar to the Section 2 task table.

Columns:

1. 할 일
2. 시작 시간
3. 끝 시간
4. 카테고리
5. 우선순위
6. 일정 유형

The user can:
- Enter task text
- Enter start time
- Enter end time
- Automatically classify category with AI
- Set priority with 3-star priority rating
- Choose fixed or AI-adjustable schedule
- Add tasks
- Delete tasks

Do NOT show completion status in this section because this is tomorrow's planning stage.

For each task, allow the user to choose:

🔒 고정 일정
"AI가 변경하지 않아요"

🔄 AI 조정 가능
"AI가 더 나은 시간과 순서를 제안할 수 있어요"

The selected status should be visually clear.

-----------------------------------
3-2. 내 계획 타임라인
-----------------------------------

Keep the same timeline visualization style as Section 2.

When users enter tasks and times, show them immediately on the timeline.

Display:
- 06:00–24:00 timeline
- Category-based blocks
- Start/end times
- Fixed schedule lock icon
- AI-adjustable schedule AI/flexible icon

The timeline must update in real time when task times are edited.

-----------------------------------
3-3. AI 분석 시작하기
-----------------------------------

Add a prominent button:

"AI 분석 시작하기"

When clicked, analyze tomorrow's plan using:

1. User's personality type
2. Today's AI analysis
3. Today's behavioral patterns
4. Tomorrow's planned tasks
5. Task categories
6. Task priorities
7. Fixed vs AI-adjustable schedule settings

Show three analysis cards:

CARD 1. 오늘의 문제 해결 여부

Compare today's behavioral problem with tomorrow's plan.

Example:
"오늘은 해야 할 일이 많을수록 과제 시작을 미루는 패턴이 있었어요."

"내일 계획에는 과제를 30분 단위로 나누어 시작하도록 반영했어요."

CARD 2. 성격 유형 적합도

Provide personalized analysis based on the user's personality type.

완벽주의 나무늘보:
- Avoid excessive number of goals
- Recommend a realistic number of important tasks
- Include sufficient breaks

도파민 청개구리:
- Use 25-minute focus + 5-minute break Pomodoro blocks
- Reduce long uninterrupted tasks
- Make task entry easier

과부하 개미:
- Add protected focus time
- Recommend a "방해 금지" block
- Move communication and requests to appropriate times

걱정인형:
- Add a warm-up step
- Break difficult tasks into smaller steps
- Add "준비하기" before difficult tasks
- Start with an easy task to reduce entry barriers

CARD 3. 시간 효율

Show:
- Total planned hours
- Number of tasks
- Schedule density
- Break time
- Overloaded or underused time periods

-----------------------------------
3-4. AI 추천 타임라인
-----------------------------------

Generate an optimized timeline based on the user's personality type.

CRITICAL RULE:

The AI MUST NEVER change, move, delete, or reschedule tasks marked:

🔒 고정 일정

The AI may only modify or suggest changes to:

🔄 AI 조정 가능

The AI can:
- Change the time
- Change the order
- Split a task
- Adjust duration
- Add breaks
- Add preparation steps
- Add focus blocks

But only for tasks marked as 🔄 AI 조정 가능.

Fixed schedules must remain exactly where the user placed them.

Example:

09:00–12:00
수업
🔒 고정 일정
→ AI cannot modify

13:00–17:00
팀플
🔒 고정 일정
→ AI cannot modify

18:00–20:00
과제
🔄 AI 조정 가능
→ AI may split into smaller blocks

20:00–21:00
운동
🔄 AI 조정 가능
→ AI may move or adjust

AI recommendation:

09:00–12:00
수업
🔒 고정

13:00–17:00
팀플
🔒 고정

17:00–17:30
휴식
🔄 AI 추천

17:30–18:00
과제 준비하기
🔄 AI 추가

18:00–18:30
과제
🔄 AI 조정

18:30–19:00
휴식
🔄 AI 추천

20:00–21:00
운동
🔒 or 🔄 depending on user's setting

AI-added or AI-modified items should be visually distinguished using:
- Purple AI icon
- Italic text
- Subtle purple highlight
- "AI 추천" or "AI 추가" label

Do NOT make AI-generated recommendations look like user-created tasks.

-----------------------------------
3-5. AI 변경 이유
-----------------------------------

At the bottom of the AI recommendation timeline, show an explanation panel.

Title:
"AI가 이렇게 바꿨어요"

Show each recommendation and its reason.

Examples:

"과제를 30분 단위로 나눴어요."
→ "도파민 청개구리 유형은 긴 작업보다 짧은 목표로 시작할 때 실행하기 쉬워요."

"과제 시작 전에 '준비하기'를 추가했어요."
→ "걱정인형 유형은 바로 어려운 일을 시작하기보다 준비 단계를 거치면 진입 장벽을 낮출 수 있어요."

"오전 2시간을 방해 금지 시간으로 설정했어요."
→ "과부하 개미 유형은 다른 사람의 요청에 시간을 빼앗기기 쉬워 집중 시간을 보호하는 것이 좋아요."

"목표를 4개에서 2개로 줄였어요."
→ "완벽주의 나무늘보 유형은 너무 많은 목표를 세우면 계획이 틀어졌을 때 전체를 포기하기 쉬워요."

Clearly communicate that:
"AI는 사용자가 정한 고정 일정을 존중하고,
변경 가능한 일정 안에서만 더 나은 하루를 제안합니다."

-----------------------------------
3-6. 최종 계획 확정
-----------------------------------

Allow the user to:
- Accept AI recommendation
- Edit AI recommendation
- Keep original schedule
- Manually modify tasks
- Confirm final plan

Final CTA:
"이 계획으로 내일 시작하기"

After confirmation, show a friendly success state:

"내일의 하루가 준비됐어요 🌱"

"완벽한 하루보다,
나에게 맞는 하루를 만들어봐요."

==================================================
FINAL INFORMATION ARCHITECTURE
==================================================

The final service should have exactly three main sections:

SECTION 1
나의 유형 알아보기
- Personality Quiz
- Personality Result

SECTION 2
오늘 하루 AI 분석
- 오늘 할 일 목록
- Fixed / AI-adjustable schedule setting
- Today's Timeline
- AI Day Analysis

SECTION 3
AI와 내일 계획하기
- Tomorrow Task Planning
- Fixed / AI-adjustable schedule setting
- Tomorrow Timeline
- AI Planning Analysis
- AI Recommended Timeline
- AI Change Reasons
- Final Plan Confirmation

Keep the existing RedesignLife visual identity and improve the information architecture without losing the current implementation quality.

The most important concept to communicate visually is:

"AI가 내 하루를 마음대로 바꾸는 것이 아니라,
내가 정한 범위 안에서 AI가 더 나은 하루를 함께 설계한다."

Make this concept clear throughout Section 3.