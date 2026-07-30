import type { ReactNode } from "react";

interface InsightCardProps {
  icon: ReactNode;
  iconBg: string;
  title: string;
  body: string;
}

export function InsightCard({ icon, iconBg, title, body }: InsightCardProps) {
  return (
    <div className="bg-card rounded-2xl border border-border p-5">
      <div className="flex items-center gap-2.5 mb-3">
        <div className={`w-8 h-8 ${iconBg} rounded-xl flex items-center justify-center flex-shrink-0`}>
          {icon}
        </div>
        <p className="text-sm font-bold text-foreground">{title}</p>
      </div>
      <p className="text-sm text-foreground/70 leading-relaxed">{body}</p>
    </div>
  );
}
