import { useState } from "react";
import { ChevronRight, ChevronLeft, Sparkles, Check, Star, ArrowRight, RotateCcw } from "lucide-react";
import type { TypeKey } from "../types";
import { TYPE_DATA } from "../data/typeData";
import { QUESTIONS } from "../data/questions";

interface Section1Props {
  typeKey: TypeKey | null;
  onSetType: (t: TypeKey) => void;
  onUserReady?: (userId: string) => void;
  onNext: () => void;
}

export function Section1({ typeKey, onSetType, onUserReady, onNext }: Section1Props) {
  const [stage, setStage] = useState<"quiz" | "result">(typeKey ? "result" : "quiz");
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<(TypeKey | null)[]>(
    Array(QUESTIONS.length).fill(null),
  );

  const currentAnswer = answers[currentQ];
  const isFirst = currentQ === 0;
  const isLast = currentQ === QUESTIONS.length - 1;
  const question = QUESTIONS[currentQ];
  const resolvedType: TypeKey = typeKey ?? "perfectionist";

  const handleSelect = (t: TypeKey) => {
    const updated = [...answers];
    updated[currentQ] = t;
    setAnswers(updated);
  };

  const handleNext = async () => {
    if (!currentAnswer) return;
    if (isLast) {
      const counts: Record<TypeKey, number> = {
        perfectionist: 0, dopamine: 0, overloaded: 0, worry: 0,
      };
      answers.forEach(a => { if (a) counts[a]++; });
      const dominant = Object.entries(counts).sort(
        ([, a], [, b]) => b - a,
      )[0][0] as TypeKey;
      onSetType(dominant);

      try {
        const response = await fetch("/api/users/type-test", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            answers: answers.filter(Boolean) as TypeKey[],
          }),
        });

        if (response.ok) {
          const body = await response.json();
          onUserReady?.(body.data.user_id);
        }
      } catch {
        // Ignore backend sync errors and continue with the local UX.
      }

      setStage("result");
    } else {
      setCurrentQ(q => q + 1);
    }
  };

  const retake = () => {
    setStage("quiz");
    setCurrentQ(0);
    setAnswers(Array(QUESTIONS.length).fill(null));
  };

  if (stage === "quiz") {
    return (
      <div className="min-h-[calc(100vh-64px)] bg-background flex flex-col items-center justify-center py-16 px-6">
        <div className="w-full max-w-2xl">
          {/* Header */}
          <div className="text-center mb-10">
            <span className="inline-flex items-center gap-2 bg-orange-100 text-orange-600 text-sm font-semibold px-4 py-1.5 rounded-full mb-5">
              <Sparkles className="w-3.5 h-3.5" />나의 유형 찾기
            </span>
            <div className="flex items-center justify-center gap-2.5 mb-4">
              {QUESTIONS.map((_, i) => (
                <div
                  key={i}
                  className={`rounded-full transition-all duration-300 ${
                    i < currentQ
                      ? "w-7 h-2.5 bg-orange-400"
                      : i === currentQ
                      ? "w-10 h-2.5 bg-orange-500"
                      : "w-7 h-2.5 bg-orange-100"
                  }`}
                />
              ))}
            </div>
            <p className="text-sm font-semibold text-muted-foreground">
              {currentQ + 1} / {QUESTIONS.length}
            </p>
          </div>

          {/* Question card */}
          <div className="bg-card rounded-3xl border border-border shadow-sm p-8 mb-6">
            <h2 className="text-xl font-bold text-foreground text-center leading-relaxed mb-8">
              {question.text}
            </h2>
            <div className="grid grid-cols-2 gap-4">
              {question.options.map((opt, i) => {
                const isSel = currentAnswer === opt.type;
                return (
                  <button
                    key={i}
                    onClick={() => handleSelect(opt.type)}
                    className={`relative p-5 rounded-2xl border-2 text-left transition-all duration-200 cursor-pointer ${
                      isSel
                        ? "border-orange-400 bg-orange-50 shadow-md"
                        : "border-border bg-white hover:border-orange-200 hover:bg-orange-50/40 hover:shadow-sm"
                    }`}
                  >
                    {isSel && (
                      <div className="absolute top-3 right-3 w-5 h-5 bg-orange-400 rounded-full flex items-center justify-center">
                        <Check className="w-3 h-3 text-white" strokeWidth={3} />
                      </div>
                    )}
                    <span className={`block text-sm font-medium leading-relaxed ${isSel ? "text-orange-800" : "text-foreground"}`}>
                      {opt.text}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <button
              onClick={() => !isFirst && setCurrentQ(q => q - 1)}
              disabled={isFirst}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-muted-foreground hover:text-foreground hover:bg-muted transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />이전
            </button>
            <button
              onClick={handleNext}
              disabled={!currentAnswer}
              className="flex items-center gap-2 px-8 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-xl font-bold transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed shadow-sm hover:shadow-md"
            >
              {isLast ? "결과 보기" : "다음"}<ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <p className="text-center text-xs text-muted-foreground mt-8">
            틀린 답은 없어요. 솔직하게 고르는 게 가장 정확해요 ✨
          </p>
        </div>
      </div>
    );
  }

  // Result stage
  const type = TYPE_DATA[resolvedType];

  return (
    <div className="min-h-[calc(100vh-64px)] bg-background flex flex-col items-center justify-center py-16 px-6">
      <div className="w-full max-w-xl">
        <div className="text-center mb-6">
          <span className="inline-flex items-center gap-2 bg-white border border-border text-muted-foreground text-sm font-semibold px-4 py-1.5 rounded-full shadow-sm">
            <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />테스트 결과
          </span>
        </div>

        <div className="bg-card rounded-3xl border border-border shadow-xl overflow-hidden mb-5">
          {/* Mascot area */}
          <div className={`${type.cardBg} px-8 pt-10 pb-8 text-center`}>
            <div
              className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-white shadow-md text-5xl mb-5"
              style={{ boxShadow: `0 8px 24px ${type.accentColor}30` }}
            >
              {type.emoji}
            </div>
            <p className={`text-xs font-bold uppercase tracking-widest ${type.tagText} mb-2`}>
              당신의 유형은
            </p>
            <h1 className="text-2xl font-extrabold text-foreground mb-2">{type.name}</h1>
            <span className={`inline-block text-sm font-semibold px-3 py-1 rounded-full ${type.tagBg} ${type.tagText}`}>
              {type.tagline}
            </span>
          </div>

          {/* Description */}
          <div className="px-8 py-6 border-b border-border">
            <p className="text-foreground/75 leading-relaxed text-sm text-center">
              {type.description}
            </p>
          </div>

          {/* Traits */}
          <div className="px-8 py-6 border-b border-border">
            <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4">
              이런 특징이 있어요
            </p>
            <ul className="space-y-3">
              {type.traits.map((trait, i) => (
                <li key={i} className="flex items-start gap-3">
                  <div className={`mt-0.5 w-5 h-5 rounded-full ${type.traitBg} flex items-center justify-center flex-shrink-0`}>
                    <span className={`text-xs font-extrabold ${type.traitText}`}>{i + 1}</span>
                  </div>
                  <span className="text-sm text-foreground/80 leading-relaxed">{trait}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* CTA */}
          <div className="px-8 py-7">
            <div className="bg-muted rounded-2xl p-4 text-center mb-5">
              <p className="text-sm font-bold text-foreground mb-1">오늘 하루를 돌아볼 준비가 됐나요?</p>
              <p className="text-xs text-muted-foreground">
                AI가 오늘의 하루를 분석하고 더 나은 내일을 함께 설계해요
              </p>
            </div>
            <button
              onClick={onNext}
              className="w-full py-4 bg-orange-500 hover:bg-orange-600 text-white font-bold rounded-2xl text-base transition-all duration-200 shadow-md hover:shadow-lg flex items-center justify-center gap-2.5"
            >
              오늘 하루 돌아보기<ArrowRight className="w-5 h-5" />
            </button>
            <button
              onClick={retake}
              className="w-full py-2.5 mt-3 text-sm font-semibold text-muted-foreground hover:text-foreground transition-colors flex items-center justify-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />다시 테스트하기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
