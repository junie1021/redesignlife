import { Lock, Shuffle, Bot } from "lucide-react";
import { CATS } from "../data/categories";
import { HOUR_LABELS, toPct, widthPct, toMin } from "../utils/timeline";
import type { TLRow } from "../types";

interface TimelineProps {
  rows: TLRow[];
}

export function Timeline({ rows }: TimelineProps) {
  const usedCats = [...new Set(rows.map(r => r.catKey))];

  return (
    <div>
      {/* Hour axis */}
      <div className="flex ml-40 mb-1">
        {HOUR_LABELS.map((h, i) => (
          <div
            key={h}
            className="text-[10px] text-muted-foreground font-medium"
            style={{
              width: `${100 / (HOUR_LABELS.length - 1)}%`,
              textAlign: i === HOUR_LABELS.length - 1 ? "right" : "left",
            }}
          >
            {h}:00
          </div>
        ))}
      </div>

      {/* Grid + rows */}
      <div className="relative">
        <div className="absolute inset-0 ml-40 pointer-events-none">
          {HOUR_LABELS.map((_, i) => (
            <div
              key={i}
              className="absolute top-0 bottom-0 border-l border-border/50"
              style={{ left: `${(i / (HOUR_LABELS.length - 1)) * 100}%` }}
            />
          ))}
        </div>

        <div className="space-y-2">
          {rows.map(row => {
            const hasTime =
              row.startTime && row.endTime && toMin(row.endTime) > toMin(row.startTime);
            const left = hasTime ? toPct(row.startTime) : 0;
            const width = hasTime ? widthPct(row.startTime, row.endTime) : 0;
            const cat = CATS[row.catKey];
            const isFixed = row.isFixed || row.scheduleType === "fixed";
            const isAI = row.isAIAdded;

            return (
              <div key={row.id} className="flex items-center h-7">
                {/* Label */}
                <div className="w-40 flex-shrink-0 pr-3 flex items-center justify-end gap-1.5">
                  {isAI && <Bot className="w-3 h-3 text-violet-400 flex-shrink-0" />}
                  {isFixed && !isAI && <Lock className="w-3 h-3 text-slate-400 flex-shrink-0" />}
                  <span
                    className={`text-[11px] font-medium truncate max-w-[130px] ${
                      isAI ? "text-violet-500 italic" : "text-foreground"
                    }`}
                  >
                    {row.name}
                  </span>
                </div>

                {/* Block */}
                <div className="flex-1 relative h-5 bg-muted/40 rounded-md overflow-hidden">
                  {hasTime ? (
                    <div
                      className="absolute top-0.5 bottom-0.5 rounded-md flex items-center gap-1 px-2 overflow-hidden"
                      style={{
                        left: `${left}%`,
                        width: `${width}%`,
                        backgroundColor: cat.dot + (isAI ? "22" : "28"),
                        borderLeft: `3px solid ${cat.dot}`,
                        opacity: isAI ? 0.85 : 1,
                      }}
                    >
                      {isFixed && (
                        <Lock className="w-2.5 h-2.5 flex-shrink-0" style={{ color: cat.dot }} />
                      )}
                      {isAI && (
                        <Bot className="w-2.5 h-2.5 flex-shrink-0" style={{ color: cat.dot }} />
                      )}
                      <span
                        className="text-[10px] font-semibold whitespace-nowrap"
                        style={{ color: cat.dot }}
                      >
                        {row.startTime}–{row.endTime}
                      </span>
                    </div>
                  ) : (
                    <div className="absolute inset-0 flex items-center px-3">
                      <span className="text-[10px] text-muted-foreground/40 italic">미입력</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      {usedCats.length > 0 && (
        <div className="mt-4 pt-3 border-t border-border flex flex-wrap gap-x-4 gap-y-2 items-center">
          {usedCats.map(k => (
            <span key={k} className="flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground">
              <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: CATS[k].dot }} />
              {CATS[k].label}
            </span>
          ))}
          <span className="ml-auto flex items-center gap-3 text-[11px] text-muted-foreground">
            <span className="flex items-center gap-1"><Lock className="w-3 h-3" />고정</span>
            <span className="flex items-center gap-1"><Shuffle className="w-3 h-3 text-violet-400" />AI 조정</span>
            <span className="flex items-center gap-1"><Bot className="w-3 h-3 text-violet-400" />AI 추가</span>
          </span>
        </div>
      )}
    </div>
  );
}
