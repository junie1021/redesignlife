import type { TypeKey, PlanTask, AIOptTask, CatKey, PlanAnalysis } from "../types";
import { getCat } from "../data/categories";
import { toMin, fromMin } from "./timeline";

// ── Internal helpers ──────────────────────────────────────────────────────────

function findFreeSlots(
  fixed: { start: number; end: number }[],
  dayStart = 9 * 60,
  dayEnd = 22 * 60,
): { start: number; end: number }[] {
  const sorted = [...fixed].sort((a, b) => a.start - b.start);
  const slots: { start: number; end: number }[] = [];
  let cur = dayStart;
  for (const r of sorted) {
    if (r.start > cur + 15) slots.push({ start: cur, end: r.start });
    cur = Math.max(cur, r.end);
  }
  if (cur < dayEnd) slots.push({ start: cur, end: dayEnd });
  return slots;
}

function advancePastFixed(
  cursor: number,
  occupied: { start: number; end: number }[],
): number {
  let c = cursor;
  let changed = true;
  while (changed) {
    changed = false;
    for (const o of occupied) {
      if (c >= o.start && c < o.end) { c = o.end; changed = true; }
    }
  }
  return c;
}

function push(
  result: AIOptTask[],
  id: number,
  name: string,
  start: number,
  dur: number,
  isAIAdded: boolean,
  changed: boolean,
  catKey: CatKey,
  note: string,
  reason: string,
): void {
  result.push({
    id, name,
    aiStart: fromMin(start), aiEnd: fromMin(start + dur),
    isFixed: false, isAIAdded, changed, catKey, note, reason,
  });
}

// ── AI Optimizer ──────────────────────────────────────────────────────────────

export function aiOptimizePlan(tasks: PlanTask[], typeKey: TypeKey): AIOptTask[] {
  const valid = tasks.filter(t => t.name.trim());
  const fixed = valid
    .filter(t => t.scheduleType === "fixed")
    .sort((a, b) => toMin(a.startTime) - toMin(b.startTime));
  const adjustable = valid
    .filter(t => t.scheduleType === "adjustable")
    .sort((a, b) => (b.priority || 0) - (a.priority || 0));

  const result: AIOptTask[] = [];

  // Fixed tasks: place exactly as entered, never modified
  fixed.forEach(t => {
    result.push({
      id: t.id, name: t.name,
      aiStart: t.startTime || "09:00", aiEnd: t.endTime || "10:00",
      isFixed: true, isAIAdded: false, changed: false,
      catKey: getCat(t.name), note: "", reason: "",
    });
  });

  const occupied = fixed
    .filter(t => t.startTime && t.endTime && toMin(t.endTime) > toMin(t.startTime))
    .map(t => ({ start: toMin(t.startTime), end: toMin(t.endTime) }));

  let cursor = advancePastFixed(9 * 60, occupied);

  if (typeKey === "perfectionist") {
    const top = adjustable.slice(0, 4);
    if (adjustable.length > 4) {
      const names = adjustable.slice(4).map(t => t.name).join(", ");
      push(result, -99,
        `⚠️ "${names}" 등 ${adjustable.length - 4}개는 내일로 미뤄요`,
        cursor, 0, true, false, "other", "",
        `완벽주의 나무늘보 유형은 너무 많은 목표를 세우면 계획이 틀어졌을 때 전체를 포기하기 쉬워요. 목표를 4개 이하로 줄였어요.`,
      );
    }
    top.forEach(t => {
      cursor = advancePastFixed(cursor, occupied);
      const dur = t.startTime && t.endTime
        ? Math.max(60, toMin(t.endTime) - toMin(t.startTime))
        : 90;
      push(result, t.id, t.name, cursor, dur, false,
        t.startTime !== fromMin(cursor), getCat(t.name), "",
        dur !== (toMin(t.endTime) - toMin(t.startTime))
          ? "충분한 시간을 확보했어요. 여유 있게 진행해봐요." : "",
      );
      cursor = advancePastFixed(cursor + dur + 30, occupied);
    });
  }

  if (typeKey === "dopamine") {
    adjustable.forEach(t => {
      cursor = advancePastFixed(cursor, occupied);
      const dur = t.startTime && t.endTime ? toMin(t.endTime) - toMin(t.startTime) : 60;
      if (dur > 50) {
        const blocks = Math.ceil(dur / 25);
        for (let b = 0; b < blocks; b++) {
          cursor = advancePastFixed(cursor, occupied);
          const bd = Math.min(25, dur - b * 25);
          push(result,
            b === 0 ? t.id : t.id * 100 + b,
            b === 0 ? t.name : `${t.name} (계속)`,
            cursor, bd, b > 0, b === 0 && t.startTime !== fromMin(cursor),
            getCat(t.name), "25분 집중 블록 🍅",
            b === 0
              ? `"${t.name}"을(를) 25분 단위로 나눴어요. 도파민 청개구리 유형은 짧은 목표로 시작할 때 실행하기 쉬워요.`
              : "",
          );
          cursor += bd;
          if (b < blocks - 1) {
            cursor = advancePastFixed(cursor, occupied);
            push(result, t.id * 100 + b + 5000, "🍃 짧은 휴식", cursor, 5, true, false, "rest", "AI 추천 휴식", "");
            cursor += 5;
          }
        }
      } else {
        push(result, t.id, t.name, cursor, dur || 45, false,
          t.startTime !== fromMin(cursor), getCat(t.name), "", "");
        cursor += dur || 45;
      }
      cursor = advancePastFixed(cursor + 10, occupied);
    });
  }

  if (typeKey === "overloaded") {
    const focusStart = advancePastFixed(9 * 60, occupied);
    const focusEnd = advancePastFixed(focusStart + 120, occupied);
    if (focusEnd - focusStart >= 60) {
      push(result, -1, "🛡️ 나만의 집중 시간 (방해 금지)", focusStart, focusEnd - focusStart,
        true, false, "self", "AI 블록킹",
        "오전 시간을 방해 금지 구역으로 설정했어요. 과부하 개미 유형은 다른 사람의 요청에 시간을 빼앗기기 쉬워 집중 시간을 보호하는 것이 중요해요.",
      );
      cursor = advancePastFixed(focusEnd, occupied);
    }
    const personal = adjustable.filter(t => getCat(t.name) !== "social");
    const social = adjustable.filter(t => getCat(t.name) === "social");
    personal.forEach(t => {
      cursor = advancePastFixed(cursor, occupied);
      const dur = t.startTime && t.endTime ? toMin(t.endTime) - toMin(t.startTime) : 60;
      push(result, t.id, t.name, cursor, dur || 60, false,
        t.startTime !== fromMin(cursor), getCat(t.name), "",
        `"${t.name}"을(를) 개인 집중 시간에 배치했어요. 내 일을 먼저 완료한 후 다른 사람의 부탁을 들어줘요.`,
      );
      cursor += (dur || 60) + 15;
    });
    if (cursor < 13 * 60) cursor = 13 * 60;
    cursor = advancePastFixed(cursor, occupied);
    social.forEach(t => {
      cursor = advancePastFixed(cursor, occupied);
      const dur = t.startTime && t.endTime ? toMin(t.endTime) - toMin(t.startTime) : 45;
      push(result, t.id, t.name, cursor, dur || 45, false,
        t.startTime !== fromMin(cursor), getCat(t.name), "오후 배치",
        `"${t.name}"을(를) 오후로 배치했어요. 소통/관계 관련 일정은 개인 업무 이후에 처리하도록 해요.`,
      );
      cursor += (dur || 45) + 15;
    });
  }

  if (typeKey === "worry") {
    cursor = advancePastFixed(9 * 60, occupied);
    push(result, -2, "🌅 가볍게 워밍업 (스트레칭·음악)", cursor, 15, true, false, "self",
      "AI 추가",
      "바로 어려운 일을 시작하기보다 가벼운 활동으로 시작하면 진입 장벽을 낮출 수 있어요.",
    );
    cursor += 15;
    const easy = adjustable.filter(t => ["social", "life", "exercise"].includes(getCat(t.name)));
    const hard = adjustable.filter(t => !["social", "life", "exercise"].includes(getCat(t.name)));
    [...easy, ...hard].forEach(t => {
      const cat = getCat(t.name);
      cursor = advancePastFixed(cursor, occupied);
      if (["study", "work", "other"].includes(cat)) {
        push(result, t.id * 100 + 9000, `📋 "${t.name}" 준비하기`, cursor, 10, true, false, "self",
          "AI 추가",
          `"${t.name}" 시작 전에 '준비하기' 단계를 추가했어요. 걱정인형 유형은 준비 단계를 거치면 시작 불안을 줄일 수 있어요.`,
        );
        cursor += 10;
        cursor = advancePastFixed(cursor, occupied);
      }
      const dur = t.startTime && t.endTime ? toMin(t.endTime) - toMin(t.startTime) : 50;
      push(result, t.id, t.name, cursor, dur || 50, false,
        t.startTime !== fromMin(cursor), cat, "",
        ["study", "work"].includes(cat) ? `"${t.name}"을(를) 준비 단계 이후에 배치했어요.` : "",
      );
      cursor += (dur || 50) + 20;
    });
  }

  // Discard zero-duration placeholder warnings (id -99 with dur 0 won't overlap anything)
  return result
    .filter(t => t.id !== -99 || t.name.startsWith("⚠️"))
    .sort((a, b) => toMin(a.aiStart) - toMin(b.aiStart));
}

// ── Plan analysis ─────────────────────────────────────────────────────────────

export function analyzePlan(tasks: PlanTask[], typeKey: TypeKey): PlanAnalysis {
  const valid = tasks.filter(t => t.name.trim());
  const withTime = valid.filter(
    t => t.startTime && t.endTime && toMin(t.endTime) > toMin(t.startTime),
  );
  const totalMins = withTime.reduce(
    (s, t) => s + toMin(t.endTime) - toMin(t.startTime), 0,
  );
  const count = valid.length;
  const adjCount = valid.filter(t => t.scheduleType === "adjustable").length;
  const h = (totalMins / 60).toFixed(1);

  const map: Record<TypeKey, PlanAnalysis> = {
    perfectionist: {
      problemSolved: {
        icon: "🌱",
        verdict: count <= 4 ? "개선됐어요!" : "조금 많아요",
        text: count <= 4
          ? `${count}가지 목표, 딱 적당해요. 오늘의 '과부하' 패턴이 개선됐네요!`
          : `목표가 ${count}개예요. 오늘처럼 지칠 수 있어요. AI가 상위 4개만 최적화할게요.`,
        good: count <= 4,
      },
      personalityFit: {
        icon: "🦥",
        verdict: "나무늘보 유형 분석",
        text: adjCount > 0
          ? `AI가 조정 가능한 ${adjCount}개 항목을 최적화할게요. 각 할 일 사이에 30분 휴식을 추가해서 완성률을 높여요.`
          : "모든 항목이 고정 일정이에요. AI 조정 가능 항목을 추가해보세요.",
        good: count <= 5,
      },
      timeEfficiency: {
        icon: "⏱️",
        verdict: withTime.length > 0 ? `총 ${h}시간 계획` : "시간 미입력",
        text: withTime.length > 0
          ? `${withTime.length}개 항목에 시간을 배정했어요. 과제 사이 30분 여유를 두면 완성률이 높아져요.`
          : "시작·끝 시간을 입력하면 더 정확한 분석이 가능해요.",
        good: withTime.length >= Math.ceil(count / 2),
      },
    },
    dopamine: {
      problemSolved: {
        icon: "🐸", verdict: "패턴 개선 중",
        text: `오늘은 긴 과제를 통째로 하려다 중단했어요. AI가 ${adjCount}개 조정 가능 항목을 25분 블록으로 쪼개서 달성하기 쉽게 만들게요.`,
        good: true,
      },
      personalityFit: {
        icon: "⚡", verdict: "포모도로 최적화",
        text: "도파민 유형은 짧고 완결되는 단위가 핵심이에요. 긴 과제를 쪼갠 후 각각 완료 체크하면 보람이 생겨요.",
        good: true,
      },
      timeEfficiency: {
        icon: "⏱️",
        verdict: withTime.length > 0 ? `총 ${h}시간 계획` : "시간 미입력",
        text: totalMins > 360
          ? "계획한 시간이 꽤 길어요. 10분 자유 시간을 중간에 넣으면 집중력이 오래 유지돼요."
          : "적절한 시간이에요. AI가 25분 단위로 재배치할게요.",
        good: totalMins <= 360,
      },
    },
    overloaded: {
      problemSolved: {
        icon: "🛡️",
        verdict: valid.some(t => t.scheduleType === "fixed") ? "고정 일정 보호 중" : "집중 시간 필요",
        text: `오늘은 남의 부탁이 너무 많았죠. AI가 ${valid.some(t => t.scheduleType === "fixed") ? "고정 일정을 지키면서 " : ""}오전에 방해 금지 구역을 만들어드릴게요.`,
        good: true,
      },
      personalityFit: {
        icon: "🐜", verdict: "개미 유형 맞춤",
        text: `AI가 소통/관계 항목을 오후로 배치하고, 개인 할 일을 오전에 먼저 채워요. ${adjCount}개 조정 가능 항목을 최적화할게요.`,
        good: true,
      },
      timeEfficiency: {
        icon: "⏱️",
        verdict: withTime.length > 0 ? `총 ${h}시간 계획` : "시간 미입력",
        text: "과부하 개미는 예상보다 30%씩 시간이 더 걸리는 경향이 있어요. AI가 여유 시간을 충분히 확보해드릴게요.",
        good: true,
      },
    },
    worry: {
      problemSolved: {
        icon: "💙",
        verdict: count <= 4 ? "부담 없는 계획!" : "조금 많아요",
        text: `오늘은 시작을 못 했죠. AI가 각 할 일 앞에 '준비하기' 단계를 추가해서 ${adjCount}개 항목의 시작 장벽을 낮춰줄게요.`,
        good: count <= 4,
      },
      personalityFit: {
        icon: "🪆", verdict: "걱정인형 맞춤",
        text: "걱정인형 유형은 '쉬운 것 먼저' 전략이 효과적이에요. 워밍업과 준비 단계로 첫 성공 경험을 만들어줄게요.",
        good: true,
      },
      timeEfficiency: {
        icon: "⏱️",
        verdict: withTime.length > 0 ? `총 ${h}시간 계획` : "시간 미입력",
        text: "각 할 일 사이에 20분 여유를 추가할게요. '다음 할 일 걱정'을 줄이고 지금에 집중할 수 있어요.",
        good: true,
      },
    },
  };

  return map[typeKey];
}
