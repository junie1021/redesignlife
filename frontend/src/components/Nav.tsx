import { Sparkles, Check } from "lucide-react";
import type { ViewKey } from "../types";

const NAV_ITEMS: { key: ViewKey; label: string }[] = [
  { key: "s1", label: "나의 유형 알아보기" },
  { key: "s2", label: "오늘 하루 AI 분석" },
  { key: "s3", label: "AI와 내일 계획하기" },
];

interface NavProps {
  view: ViewKey;
  onNavigate: (view: ViewKey) => void;
}

export function Nav({ view, onNavigate }: NavProps) {
  const currentIndex = NAV_ITEMS.findIndex(s => s.key === view);

  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-border">
      <div className="max-w-5xl mx-auto px-6 py-3.5 flex items-center justify-between">
        {/* Logo */}
        <button
          onClick={() => onNavigate("s1")}
          className="flex items-center gap-2.5 group"
        >
          <div className="w-8 h-8 bg-orange-500 rounded-xl flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span className="text-base font-extrabold text-foreground tracking-tight">
            RedesignLife
          </span>
        </button>

        {/* Steps */}
        <div className="flex items-center gap-1 bg-muted rounded-xl p-1">
          {NAV_ITEMS.map((item, i) => {
            const isActive = item.key === view;
            const isPast = i < currentIndex;
            return (
              <button
                key={item.key}
                onClick={() => onNavigate(item.key)}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                  isActive
                    ? "bg-orange-500 text-white shadow-sm"
                    : isPast
                    ? "text-orange-500 hover:bg-orange-50"
                    : "text-muted-foreground hover:bg-white/60"
                }`}
              >
                {isPast && !isActive && <Check className="w-3 h-3" strokeWidth={3} />}
                <span className="hidden lg:inline">{item.label}</span>
                <span className="lg:hidden">{i + 1}단계</span>
              </button>
            );
          })}
        </div>

        {/* Tagline */}
        <p className="text-xs text-muted-foreground hidden xl:block text-right leading-relaxed">
          실패한 하루도 <br />다시 설계할 수 있어요
        </p>
      </div>
    </nav>
  );
}
