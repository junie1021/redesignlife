import { Lock, Shuffle } from "lucide-react";
import type { ScheduleType } from "../../types";

interface ScheduleToggleProps {
  value: ScheduleType;
  onChange: (value: ScheduleType) => void;
}

export function ScheduleToggle({ value, onChange }: ScheduleToggleProps) {
  return (
    <div className="inline-flex rounded-lg overflow-hidden border border-border text-[11px] font-bold">
      <button
        onClick={() => onChange("fixed")}
        className={`flex items-center gap-1 px-2.5 py-1.5 transition-colors ${
          value === "fixed"
            ? "bg-slate-700 text-white"
            : "bg-white text-muted-foreground hover:bg-slate-50"
        }`}
      >
        <Lock className="w-3 h-3" />고정
      </button>
      <button
        onClick={() => onChange("adjustable")}
        className={`flex items-center gap-1 px-2.5 py-1.5 transition-colors border-l border-border ${
          value === "adjustable"
            ? "bg-violet-500 text-white"
            : "bg-white text-muted-foreground hover:bg-violet-50"
        }`}
      >
        <Shuffle className="w-3 h-3" />AI 조정
      </button>
    </div>
  );
}
