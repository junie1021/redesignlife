import { useState } from "react";
import {
  Calendar, Clock, Bot, ArrowRight, Target, Brain, Lightbulb, Lock, Shuffle,
} from "lucide-react";
import type { DailyAIAnalysis, TypeKey, Task, TLRow } from "../types";
import { CATS, getCat } from "../data/categories";
import { TYPE_DATA } from "../data/typeData";
import { Timeline } from "./Timeline";
import { StarRating } from "./ui/StarRating";
import { ScoreRing } from "./ui/ScoreRing";
import { InsightCard } from "./ui/InsightCard";
import { ScheduleToggle } from "./ui/ScheduleToggle";
import { apiFetch, formatLocalDate, getApiError } from "../utils/api";

let s2IdCounter = 0;

interface Section2Props {
  typeKey: TypeKey;
  userId: string | null;
  onNext: () => void;
}

export function Section2({ typeKey, userId, onNext }: Section2Props) {
  const type = TYPE_DATA[typeKey];

  const [tasks, setTasks] = useState<Task[]>(
    type.initialTasks.map(t => ({ ...t, id: ++s2IdCounter })),
  );
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [analysis, setAnalysis] = useState<DailyAIAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const update = (id: number, patch: Partial<Task>) =>
    setTasks(prev => prev.map(t => t.id === id ? { ...t, ...patch } : t));

  const doneCount = tasks.filter(t => t.done).length;

  const handleAnalysis = async () => {
    setIsAnalyzing(true);
    setAnalysisError(null);

    try {
      if (!userId) {
        throw new Error("먼저 나의 유형 알아보기에서 성향 테스트를 완료해주세요.");
      }

      const today = formatLocalDate(new Date());
      const response = await apiFetch(`/api/days/${today}/analysis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          date: today,
          tasks: tasks.map(task => ({
            title: task.name,
            start_time: task.startTime || null,
            end_time: task.endTime || null,
            is_completed: task.done,
            satisfaction: task.satisfaction || null,
            schedule_type: task.scheduleType === "fixed" ? "FIXED" : "ADJUSTABLE",
            category: getCat(task.name),
          })),
        }),
      });

      if (!response.ok) {
        throw new Error(await getApiError(response));
      }

      const body = await response.json();
      setAnalysis(body.data);
      setShowAnalysis(true);
    } catch (error) {
      setAnalysisError(error instanceof Error ? error.message : "AI 분석 요청에 실패했습니다.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const tlRows: TLRow[] = tasks.map(t => ({
    id: t.id,
    name: t.name,
    startTime: t.startTime,
    endTime: t.endTime,
    catKey: getCat(t.name),
    scheduleType: t.scheduleType,
  }));

  return (
    <div className="min-h-[calc(100vh-64px)] bg-background py-10 px-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-7">
          <span className={`inline-flex items-center gap-2 ${type.tagBg} ${type.tagText} text-xs font-bold px-3 py-1.5 rounded-full mb-3`}>
            <span className="text-base">{type.emoji}</span>{type.name}
          </span>
          <h1 className="text-2xl font-extrabold text-foreground mb-1">
            안녕하세요 👋 오늘 하루 어떠셨나요?
          </h1>
          <p className="text-sm text-muted-foreground">
            AI가 오늘의 하루를 분석했어요. 판단 없이, 이해하는 시선으로요.
          </p>
        </div>

        {/* Schedule type guide */}
        <div className="grid grid-cols-2 gap-3 mb-5">
          <div className="flex items-start gap-3 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3">
            <Lock className="w-4 h-4 text-slate-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-xs font-bold text-slate-700">🔒 고정 일정</p>
              <p className="text-xs text-slate-500 mt-0.5">
                AI가 시간과 내용을 변경하지 않아요 (수업, 회의, 병원 예약 등)
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 bg-violet-50 border border-violet-200 rounded-xl px-4 py-3">
            <Shuffle className="w-4 h-4 text-violet-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-xs font-bold text-violet-700">🔄 AI 조정 가능</p>
              <p className="text-xs text-violet-500 mt-0.5">
                AI가 시간, 순서, 소요 시간 등을 제안할 수 있어요
              </p>
            </div>
          </div>
        </div>

        {/* Task table */}
        <div className="bg-card rounded-2xl border border-border overflow-hidden mb-5">
          <div className="flex items-center justify-between px-6 py-4 border-b border-border">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <h2 className="text-sm font-bold text-foreground">오늘 할 일 목록</h2>
              <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${type.tagBg} ${type.tagText}`}>
                {doneCount}/{tasks.length} 완료
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
                  <th className="px-3 py-3 text-center w-12">완료</th>
                  <th className="px-3 py-3 text-left">할 일</th>
                  <th className="px-3 py-3 text-center w-28">시작</th>
                  <th className="px-3 py-3 text-center w-28">끝</th>
                  <th className="px-3 py-3 text-center w-32">
                    <span className="flex items-center justify-center gap-1">
                      <Bot className="w-3 h-3 text-violet-400" />카테고리
                    </span>
                  </th>
                  <th className="px-3 py-3 text-center w-32">만족도</th>
                  <th className="px-3 py-3 text-center w-36">일정 유형</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {tasks.map(task => {
                  const cat = CATS[getCat(task.name)];
                  return (
                    <tr
                      key={task.id}
                      className={`transition-colors ${task.done ? "bg-green-50/50" : "bg-white"} hover:bg-muted/10`}
                    >
                      <td className="px-3 py-3 text-center">
                        <button
                          onClick={() => update(task.id, { done: !task.done })}
                          className={`w-5 h-5 rounded-md border-2 flex items-center justify-center mx-auto transition-colors ${
                            task.done
                              ? "bg-green-400 border-green-400"
                              : "border-gray-300 hover:border-green-400"
                          }`}
                        >
                          {task.done && (
                            <svg className="w-3 h-3 text-white" viewBox="0 0 12 12" fill="none">
                              <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                          )}
                        </button>
                      </td>
                      <td className="px-3 py-3">
                        <span className={`font-medium ${task.done ? "line-through text-muted-foreground" : "text-foreground"}`}>
                          {task.name}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-center">
                        <input
                          type="time"
                          value={task.startTime}
                          onChange={e => update(task.id, { startTime: e.target.value })}
                          className="w-24 text-center text-xs bg-muted/50 border border-border rounded-lg px-1.5 py-1 focus:outline-none focus:ring-2 focus:ring-orange-300 cursor-pointer"
                        />
                      </td>
                      <td className="px-3 py-3 text-center">
                        <input
                          type="time"
                          value={task.endTime}
                          onChange={e => update(task.id, { endTime: e.target.value })}
                          className="w-24 text-center text-xs bg-muted/50 border border-border rounded-lg px-1.5 py-1 focus:outline-none focus:ring-2 focus:ring-orange-300 cursor-pointer"
                        />
                      </td>
                      <td className="px-3 py-3 text-center">
                        <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full ${cat.bg} ${cat.text}`}>
                          <Bot className="w-3 h-3" />{cat.label}
                        </span>
                      </td>
                      <td className="px-3 py-3">
                        <div className="flex justify-center">
                          <StarRating
                            value={task.satisfaction}
                            onChange={v => update(task.id, { satisfaction: v })}
                          />
                        </div>
                      </td>
                      <td className="px-3 py-3 text-center">
                        <ScheduleToggle
                          value={task.scheduleType}
                          onChange={v => update(task.id, { scheduleType: v })}
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Timeline */}
        <div className="bg-card rounded-2xl border border-border overflow-hidden mb-5">
          <div className="px-6 py-4 border-b border-border">
            <h2 className="text-sm font-bold text-foreground flex items-center gap-2">
              <Clock className="w-4 h-4 text-muted-foreground" />하루 타임라인
              <span className="text-xs font-normal text-muted-foreground ml-1">
                시작·끝 시간을 입력하면 자동으로 표시돼요
              </span>
            </h2>
          </div>
          <div className="px-6 py-5">
            <Timeline rows={tlRows} />
          </div>
        </div>

        {/* AI trigger or results */}
        {!showAnalysis ? (
          <div className="bg-card rounded-2xl border border-border p-8 flex flex-col items-center text-center">
            <div className="w-14 h-14 bg-violet-100 rounded-2xl flex items-center justify-center mb-4">
              <Bot className="w-7 h-7 text-violet-500" />
            </div>
            <h3 className="text-base font-bold text-foreground mb-1">
              할 일 목록과 타임라인 입력이 끝났나요?
            </h3>
            <p className="text-sm text-muted-foreground mb-6 leading-relaxed max-w-md">
              AI가 오늘 하루를 분석해볼게요.<br />
              완료 여부·시간·만족도·일정 유형을 채울수록 더 정확한 분석이 나와요.
            </p>
            {analysisError && (
              <p role="alert" className="mb-4 text-sm font-semibold text-red-600">
                {analysisError}
              </p>
            )}
            <button
              onClick={handleAnalysis}
              disabled={isAnalyzing}
              className="inline-flex items-center gap-2.5 px-8 py-3.5 rounded-xl font-bold text-sm text-white shadow-md hover:shadow-lg hover:scale-[1.02] transition-all duration-200"
              style={{ background: "linear-gradient(135deg, #7C6EF8 0%, #9F8BFA 100%)" }}
            >
              <Bot className="w-4 h-4" />{isAnalyzing ? "AI 분석 중..." : "AI의 하루 분석 보기"}<ArrowRight className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <>
            {/* Score + insights */}
            <div className="grid grid-cols-4 gap-5 mb-5">
              <div className="col-span-1 bg-card rounded-2xl border border-border p-6 flex flex-col items-center justify-center text-center">
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4">
                  하루 점수
                </p>
                <div className="relative w-28 h-28 mb-3">
                    <ScoreRing score={analysis?.score ?? 0} color={type.accentColor} />
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-3xl font-extrabold text-foreground">{analysis?.score ?? 0}</span>
                    <span className="text-xs text-muted-foreground font-medium">/ 100</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground leading-snug">{analysis?.summary}</p>
              </div>

              <div className="col-span-3 grid grid-rows-3 gap-3">
                <InsightCard
                  icon={<Target className="w-4 h-4 text-red-500" />}
                  iconBg="bg-red-50"
                  title="오늘의 문제"
                  body={analysis?.problem ?? ""}
                />
                <InsightCard
                  icon={<Brain className="w-4 h-4 text-violet-500" />}
                  iconBg="bg-violet-50"
                  title="AI가 발견한 행동 패턴"
                  body={analysis?.pattern ?? ""}
                />
                <InsightCard
                  icon={<Lightbulb className="w-4 h-4 text-amber-500" />}
                  iconBg="bg-amber-50"
                  title="내일을 위한 작은 변화"
                  body={analysis?.suggestion ?? ""}
                />
              </div>
            </div>

            {/* CTA to Section 3 */}
            <div
              className="rounded-2xl p-7 flex items-center justify-between"
              style={{ background: "linear-gradient(135deg, #FF6B47 0%, #FF8C6B 100%)" }}
            >
              <div>
                <h3 className="text-white font-extrabold text-lg mb-1">
                  AI와 내일을 계획해볼까요? 🗓️
                </h3>
                <p className="text-orange-100 text-sm">
                  오늘의 패턴을 바탕으로 AI가 내일 더 나은 하루를 함께 설계해요.
                </p>
              </div>
              <button
                onClick={onNext}
                className="flex-shrink-0 ml-6 flex items-center gap-2 px-6 py-3 bg-white text-orange-600 rounded-xl font-bold text-sm hover:bg-orange-50 transition-colors shadow-md"
              >
                AI와 내일 계획하기<ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
