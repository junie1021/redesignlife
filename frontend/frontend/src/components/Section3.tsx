import { useState } from "react";
import {
  Calendar, Clock, Bot, ArrowRight, Plus, Trash2, RotateCcw,
  Lock, Shuffle, Zap, Star, ShieldCheck, Brain, TrendingUp, Check,
} from "lucide-react";
import type { TypeKey, PlanTask, AIOptTask, TLRow, PlanAnalysis } from "../types";
import { getCat } from "../data/categories";
import { CATS } from "../data/categories";
import { TYPE_DATA } from "../data/typeData";
import { aiOptimizePlan, analyzePlan } from "../utils/aiOptimizer";
import { Timeline } from "./Timeline";
import { ScheduleToggle } from "./ui/ScheduleToggle";

let s3IdCounter = 0;
const mkPlan = (): PlanTask => ({
  id: ++s3IdCounter,
  name: "",
  startTime: "",
  endTime: "",
  priority: 0,
  scheduleType: "adjustable",
  category: undefined,
});

const normalizeTimeInput = (value: string) => {
  const digits = value.replace(/\D/g, "").slice(0, 4);
  if (digits.length <= 2) return digits;
  if (digits.length === 3) return `${digits.slice(0, 2)}:${digits.slice(2)}`;
  return `${digits.slice(0, 2)}:${digits.slice(2, 4)}`;
};

interface Section3Props {
  typeKey: TypeKey;
  userId: string | null;
  onRestart: () => void;
}

export function Section3({ typeKey, userId, onRestart }: Section3Props) {
  const type = TYPE_DATA[typeKey];

  const [tasks, setTasks] = useState<PlanTask[]>([mkPlan(), mkPlan(), mkPlan()]);
  const [showAI, setShowAI] = useState(false);
  const [aiData, setAiData] = useState<{
    analysis: PlanAnalysis;
    optimized: AIOptTask[];
  } | null>(null);
  const [confirmed, setConfirmed] = useState(false);

  const update = (id: number, patch: Partial<PlanTask>) =>
    setTasks(prev => prev.map(t => t.id === id ? { ...t, ...patch } : t));
  const addTask = () => setTasks(prev => [...prev, mkPlan()]);
  const deleteTask = (id: number) => setTasks(prev => prev.filter(t => t.id !== id));

  const handleAI = async () => {
    const analysis = analyzePlan(tasks, typeKey);
    const fallbackOptimized = aiOptimizePlan(tasks, typeKey);

    try {
      if (!userId) {
        throw new Error("missing user id");
      }

      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);

      const response = await fetch("/api/plans/optimize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          date: tomorrow.toISOString().slice(0, 10),
          available_start_time: "09:00",
          available_end_time: "18:00",
          tasks: tasks
            .filter(task => task.name.trim())
            .map(task => ({
              title: task.name,
              estimated_minutes: Math.max(
                30,
                task.startTime && task.endTime
                  ? Math.max(30, Math.round((Number(task.endTime.slice(0, 2)) * 60 + Number(task.endTime.slice(3, 5)) - (Number(task.startTime.slice(0, 2)) * 60 + Number(task.startTime.slice(3, 5)))) / 15) * 15)
                  : 60,
              ),
              priority: Math.max(1, Math.min(3, task.priority || 1)),
              category: task.category ?? getCat(task.name),
            })),
        }),
      });

      if (!response.ok) {
        throw new Error("ai request failed");
      }

      const body = await response.json();
      const optimized = body.data.optimized_schedules.map((item: {
        title: string;
        start_time: string;
        end_time: string;
        reason: string;
        category?: string | null;
      }, index: number): AIOptTask => ({
        id: index + 1,
        name: item.title,
        aiStart: item.start_time,
        aiEnd: item.end_time,
        isFixed: false,
        isAIAdded: true,
        changed: true,
        catKey: getCat(item.title),
        note: item.category ?? "",
        reason: item.reason,
      }));

      setAiData({ analysis, optimized });
    } catch {
      setAiData({
        analysis,
        optimized: fallbackOptimized,
      });
    }

    setShowAI(true);
  };

  const tlRows: TLRow[] = tasks.filter(t => t.name.trim()).map(t => ({
    id: t.id, name: t.name, startTime: t.startTime, endTime: t.endTime,
    catKey: getCat(t.name), scheduleType: t.scheduleType,
  }));

  const aiRows: TLRow[] = (aiData?.optimized ?? []).map(t => ({
    id: t.id, name: t.name, startTime: t.aiStart, endTime: t.aiEnd,
    catKey: t.catKey, isFixed: t.isFixed, isAIAdded: t.isAIAdded,
  }));

  const reasons = (aiData?.optimized ?? []).filter(t => t.reason);

  // ── Success state ────────────────────────────────────────────────────────────

  if (confirmed) {
    return (
      <div className="min-h-[calc(100vh-64px)] bg-background flex flex-col items-center justify-center py-16 px-6">
        <div className="w-full max-w-md text-center">
          <div className="text-7xl mb-6">🌱</div>
          <h1 className="text-2xl font-extrabold text-foreground mb-3">
            내일의 하루가 준비됐어요!
          </h1>
          <p className="text-foreground/70 leading-relaxed mb-2">완벽한 하루보다,</p>
          <p className="text-foreground font-semibold text-lg mb-8">
            나에게 맞는 하루를 만들어봐요.
          </p>

          <div className={`${type.cardBg} rounded-2xl p-5 mb-8 text-left`}>
            <p className={`text-xs font-bold ${type.tagText} mb-3`}>내일의 계획 요약</p>
            <ul className="space-y-2">
              {(aiData?.optimized ?? [])
                .filter(t => !t.name.startsWith("⚠️"))
                .slice(0, 6)
                .map(t => (
                  <li key={t.id} className="flex items-center gap-2.5 text-sm">
                    {t.isFixed ? (
                      <Lock className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                    ) : t.isAIAdded ? (
                      <Bot className="w-3.5 h-3.5 text-violet-400 flex-shrink-0" />
                    ) : (
                      <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                    )}
                    <span className={t.isAIAdded ? "text-violet-600 italic" : "text-foreground"}>
                      {t.name}
                    </span>
                    <span className="text-xs text-muted-foreground ml-auto">
                      {t.aiStart}–{t.aiEnd}
                    </span>
                  </li>
                ))}
            </ul>
          </div>

          <button
            onClick={onRestart}
            className="flex items-center gap-2 px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-xl font-bold transition-colors shadow-md mx-auto"
          >
            <RotateCcw className="w-4 h-4" />처음부터 다시 시작하기
          </button>
        </div>
      </div>
    );
  }

  // ── Planning view ────────────────────────────────────────────────────────────

  return (
    <div className="min-h-[calc(100vh-64px)] bg-background py-10 px-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-7">
          <span className={`inline-flex items-center gap-2 ${type.tagBg} ${type.tagText} text-xs font-bold px-3 py-1.5 rounded-full mb-3`}>
            <span className="text-base">{type.emoji}</span>{type.name}
          </span>
          <h1 className="text-2xl font-extrabold text-foreground mb-1">
            내일을 미리 설계해봐요 🗓️
          </h1>
          <p className="text-sm text-muted-foreground">
            고정 일정은 AI가 건드리지 않아요. AI 조정 가능 항목만 최적화할게요.
          </p>
        </div>

        {/* Today's problem reminder */}
        <div className="bg-amber-50 border border-amber-200 rounded-2xl px-5 py-4 mb-5 flex items-start gap-3">
          <span className="text-lg mt-0.5">💡</span>
          <div>
            <p className="text-sm font-bold text-amber-800 mb-0.5">오늘 AI가 발견한 문제</p>
            <p className="text-sm text-amber-700 leading-relaxed">{type.problem}</p>
          </div>
        </div>

        {/* Schedule type guide */}
        <div className="grid grid-cols-2 gap-3 mb-5">
          <div className="flex items-start gap-3 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3">
            <Lock className="w-4 h-4 text-slate-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-xs font-bold text-slate-700">🔒 고정 일정 — AI가 변경하지 않아요</p>
              <p className="text-xs text-slate-500 mt-0.5">수업, 시험, 회의, 병원 예약, 팀플, 약속 등</p>
            </div>
          </div>
          <div className="flex items-start gap-3 bg-violet-50 border border-violet-200 rounded-xl px-4 py-3">
            <Shuffle className="w-4 h-4 text-violet-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-xs font-bold text-violet-700">🔄 AI 조정 가능 — 더 나은 시간과 순서를 제안</p>
              <p className="text-xs text-violet-500 mt-0.5">공부, 과제, 운동, 휴식, 자기계발 등</p>
            </div>
          </div>
        </div>

        {/* Plan table */}
        <div className="bg-card rounded-2xl border border-border overflow-hidden mb-5">
          <div className="flex items-center justify-between px-6 py-4 border-b border-border">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <h2 className="text-sm font-bold text-foreground">내일 할 일 목록</h2>
              <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
                {tasks.filter(t => t.name.trim()).length}개
              </span>
            </div>
            <span className="text-xs text-muted-foreground flex items-center gap-1">
              <Bot className="w-3.5 h-3.5 text-violet-400" />카테고리는 AI가 자동 분류
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-muted/50 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  <th className="px-3 py-3 text-left">할 일</th>
                  <th className="px-3 py-3 text-center w-28">시작</th>
                  <th className="px-3 py-3 text-center w-28">끝</th>
                  <th className="px-3 py-3 text-center w-32">
                    <span className="flex items-center justify-center gap-1">
                      <Bot className="w-3 h-3 text-violet-400" />카테고리
                    </span>
                  </th>
                  <th className="px-3 py-3 text-center w-28">우선순위</th>
                  <th className="px-3 py-3 text-center w-36">일정 유형</th>
                  <th className="px-3 py-3 w-10" />
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {tasks.map(task => {
                  const hasCat = task.name.trim().length > 0;
                  const catKey = task.category ?? (hasCat ? getCat(task.name) : "other");
                  const cat = CATS[catKey];
                  return (
                    <tr key={task.id} className="bg-white hover:bg-muted/10 transition-colors">
                      <td className="px-3 py-3">
                        <input
                          type="text"
                          value={task.name}
                          onChange={e => update(task.id, { name: e.target.value })}
                          placeholder="할 일을 입력하세요"
                          className="w-full text-sm text-foreground bg-transparent focus:outline-none placeholder:text-muted-foreground/40"
                        />
                      </td>
                      <td className="px-3 py-3 text-center">
                        <input
                          type="text"
                          inputMode="numeric"
                          maxLength={5}
                          placeholder="09:00"
                          value={task.startTime}
                          onChange={e => update(task.id, { startTime: normalizeTimeInput(e.target.value) })}
                          className="w-24 text-center text-xs bg-muted/50 border border-border rounded-lg px-1.5 py-1 focus:outline-none focus:ring-2 focus:ring-orange-300"
                        />
                      </td>
                      <td className="px-3 py-3 text-center">
                        <input
                          type="text"
                          inputMode="numeric"
                          maxLength={5}
                          placeholder="10:00"
                          value={task.endTime}
                          onChange={e => update(task.id, { endTime: normalizeTimeInput(e.target.value) })}
                          className="w-24 text-center text-xs bg-muted/50 border border-border rounded-lg px-1.5 py-1 focus:outline-none focus:ring-2 focus:ring-orange-300"
                        />
                      </td>
                      <td className="px-3 py-3 text-center">
                        {hasCat ? (
                          <div className="flex items-center justify-center gap-2">
                            <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full ${cat.bg} ${cat.text}`}>
                              <Bot className="w-3 h-3" />{cat.label}
                            </span>
                            <select
                              value={task.category ?? "auto"}
                              onChange={e => {
                                const next = e.target.value;
                                update(task.id, {
                                  category: next === "auto" ? undefined : next as CatKey,
                                });
                              }}
                              className="text-[11px] bg-muted/60 border border-border rounded-lg px-2 py-1 text-muted-foreground focus:outline-none focus:ring-2 focus:ring-orange-300"
                              aria-label="카테고리 수동 선택"
                            >
                              <option value="auto">AI 자동</option>
                              {Object.entries(CATS).map(([key, value]) => (
                                <option key={key} value={key}>{value.label}</option>
                              ))}
                            </select>
                          </div>
                        ) : (
                          <span className="text-xs text-muted-foreground/40">—</span>
                        )}
                      </td>
                      <td className="px-3 py-3">
                        <div className="flex justify-center gap-0.5">
                          {[1, 2, 3].map(s => (
                            <button
                              key={s}
                              type="button"
                              onClick={() => update(task.id, { priority: s === task.priority ? 0 : s })}
                              className="transition-transform hover:scale-110"
                            >
                              <Star
                                className={`w-4 h-4 ${
                                  s <= task.priority
                                    ? "text-amber-400 fill-amber-400"
                                    : "text-gray-200 fill-gray-200"
                                }`}
                              />
                            </button>
                          ))}
                        </div>
                      </td>
                      <td className="px-3 py-3 text-center">
                        <ScheduleToggle
                          value={task.scheduleType}
                          onChange={v => update(task.id, { scheduleType: v })}
                        />
                      </td>
                      <td className="px-3 py-3 text-center">
                        <button
                          onClick={() => deleteTask(task.id)}
                          className="w-6 h-6 flex items-center justify-center rounded-lg text-muted-foreground/40 hover:text-red-400 hover:bg-red-50 transition-colors mx-auto"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="px-4 py-3 border-t border-border">
            <button
              onClick={addTask}
              className="flex items-center gap-2 text-sm font-semibold text-orange-500 hover:text-orange-600 transition-colors"
            >
              <Plus className="w-4 h-4" />할 일 추가
            </button>
          </div>
        </div>

        {/* My plan timeline */}
        {tlRows.length > 0 && (
          <div className="bg-card rounded-2xl border border-border overflow-hidden mb-5">
            <div className="px-6 py-4 border-b border-border">
              <h2 className="text-sm font-bold text-foreground flex items-center gap-2">
                <Clock className="w-4 h-4 text-muted-foreground" />내 계획 타임라인
                <span className="text-xs font-normal text-muted-foreground ml-1">
                  시작·끝 시간 입력 시 자동 표시
                </span>
              </h2>
            </div>
            <div className="px-6 py-5">
              <Timeline rows={tlRows} />
            </div>
          </div>
        )}

        {/* AI trigger */}
        {!showAI ? (
          <div className="bg-card rounded-2xl border border-border p-8 flex flex-col items-center text-center">
            <div
              className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4"
              style={{ background: "linear-gradient(135deg, #7C6EF8 0%, #9F8BFA 100%)" }}
            >
              <Zap className="w-7 h-7 text-white" />
            </div>
            <h3 className="text-base font-bold text-foreground mb-1">
              내일 계획, AI가 분석해드릴게요
            </h3>
            <p className="text-sm text-muted-foreground mb-2 leading-relaxed max-w-md">
              오늘의 타임라인과 내일의 계획을 비교해서<br />
              성격 유형에 맞는 최적 타임라인을 추천해드려요.
            </p>
            <p className="text-xs text-violet-500 font-semibold mb-6">
              🔒 고정 일정은 절대 변경하지 않아요
            </p>
            <button
              onClick={handleAI}
              disabled={tasks.filter(t => t.name.trim()).length === 0}
              className="inline-flex items-center gap-2.5 px-8 py-3.5 rounded-xl font-bold text-sm text-white shadow-md hover:shadow-lg hover:scale-[1.02] disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200"
              style={{ background: "linear-gradient(135deg, #7C6EF8 0%, #9F8BFA 100%)" }}
            >
              <Bot className="w-4 h-4" />AI 분석 시작하기<ArrowRight className="w-4 h-4" />
            </button>
          </div>
        ) : aiData && (
          <>
            {/* Analysis cards */}
            <div className="grid grid-cols-3 gap-4 mb-5">
              {[
                {
                  d: aiData.analysis.problemSolved,
                  icon: <ShieldCheck className="w-4 h-4" />,
                  bg: "bg-emerald-50", ic: "text-emerald-500",
                },
                {
                  d: aiData.analysis.personalityFit,
                  icon: <Brain className="w-4 h-4" />,
                  bg: "bg-violet-50", ic: "text-violet-500",
                },
                {
                  d: aiData.analysis.timeEfficiency,
                  icon: <TrendingUp className="w-4 h-4" />,
                  bg: "bg-blue-50", ic: "text-blue-500",
                },
              ].map(({ d, icon, bg, ic }, i) => (
                <div key={i} className="bg-card rounded-2xl border border-border p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <div className={`w-8 h-8 ${bg} rounded-xl flex items-center justify-center ${ic}`}>
                      {icon}
                    </div>
                    <p className={`text-xs font-bold ${d.good ? "text-emerald-600" : "text-amber-600"}`}>
                      {d.icon} {d.verdict}
                    </p>
                  </div>
                  <p className="text-xs text-foreground/75 leading-relaxed">{d.text}</p>
                </div>
              ))}
            </div>

            {/* AI recommended timeline */}
            <div className="bg-card rounded-2xl border border-border overflow-hidden mb-5">
              <div className="px-6 py-4 border-b border-border flex items-center justify-between">
                <h2 className="text-sm font-bold text-foreground flex items-center gap-2">
                  <Bot className="w-4 h-4 text-violet-500" />AI 추천 타임라인
                </h2>
                <span className="text-xs text-violet-600 font-semibold bg-violet-50 px-3 py-1 rounded-full">
                  🔒 고정 일정은 그대로 유지돼요
                </span>
              </div>
              <div className="px-6 py-5">
                {aiRows.length > 0 ? (
                  <Timeline rows={aiRows} />
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    할 일을 입력하면 AI 추천 타임라인이 생성돼요
                  </p>
                )}
              </div>
            </div>

            {/* AI change reasons */}
            {reasons.length > 0 && (
              <div className="bg-violet-50 rounded-2xl border border-violet-200 overflow-hidden mb-5">
                <div className="px-6 py-4 border-b border-violet-200">
                  <h2 className="text-sm font-bold text-violet-800 flex items-center gap-2">
                    <Bot className="w-4 h-4" />AI가 이렇게 바꿨어요
                  </h2>
                </div>
                <div className="px-6 py-5 space-y-4">
                  {reasons.map(t => (
                    <div key={t.id} className="flex items-start gap-3">
                      <span className="w-1.5 h-1.5 rounded-full bg-violet-400 flex-shrink-0 mt-2" />
                      <div>
                        <p className="text-sm font-semibold text-violet-900">"{t.name}"</p>
                        <p className="text-xs text-violet-700 mt-0.5 leading-relaxed">{t.reason}</p>
                      </div>
                    </div>
                  ))}
                  <div className="mt-4 pt-4 border-t border-violet-200">
                    <p className="text-xs text-violet-600 leading-relaxed text-center">
                      AI는 사용자가 정한 고정 일정을 존중하고,<br />
                      변경 가능한 일정 안에서만 더 나은 하루를 제안합니다.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Final confirm */}
            <div
              className="rounded-2xl p-7 flex items-center justify-between"
              style={{ background: "linear-gradient(135deg, #7C6EF8 0%, #9F8BFA 100%)" }}
            >
              <div>
                <h3 className="text-white font-extrabold text-lg mb-1">
                  이 계획으로 내일 시작할까요? ✨
                </h3>
                <p className="text-violet-100 text-sm">완벽한 하루보다, 나에게 맞는 하루를 만들어봐요.</p>
              </div>
              <div className="flex items-center gap-3 flex-shrink-0 ml-6">
                <button
                  onClick={() => { setShowAI(false); setAiData(null); }}
                  className="flex items-center gap-2 px-4 py-2.5 bg-white/20 hover:bg-white/30 text-white rounded-xl font-semibold text-sm transition-colors"
                >
                  <RotateCcw className="w-3.5 h-3.5" />계획 수정
                </button>
                <button
                  onClick={() => setConfirmed(true)}
                  className="flex items-center gap-2 px-6 py-2.5 bg-white text-violet-600 rounded-xl font-bold text-sm hover:bg-violet-50 transition-colors shadow-md"
                >
                  이 계획으로 내일 시작하기<ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
