export type TypeKey = "perfectionist" | "dopamine" | "overloaded" | "worry";
export type ViewKey = "s1" | "s2" | "s3";
export type ScheduleType = "fixed" | "adjustable";

export interface Task {
  id: number;
  name: string;
  done: boolean;
  startTime: string;
  endTime: string;
  satisfaction: number;
  scheduleType: ScheduleType;
}

export interface PlanTask {
  id: number;
  name: string;
  startTime: string;
  endTime: string;
  priority: number;
  scheduleType: ScheduleType;
  category?: CatKey;
}

export interface AIOptTask {
  id: number;
  name: string;
  aiStart: string;
  aiEnd: string;
  isFixed: boolean;
  isAIAdded: boolean;
  changed: boolean;
  catKey: CatKey;
  note: string;
  reason: string;
}

export interface AnalysisCard {
  icon: string;
  verdict: string;
  text: string;
  good: boolean;
}

export interface PlanAnalysis {
  problemSolved: AnalysisCard;
  personalityFit: AnalysisCard;
  timeEfficiency: AnalysisCard;
}

export interface TLRow {
  id: number;
  name: string;
  startTime: string;
  endTime: string;
  catKey: CatKey;
  scheduleType?: ScheduleType;
  isAIAdded?: boolean;
  isFixed?: boolean;
}

// Re-export CatKey so consumers import from one place
export type CatKey = "exercise" | "study" | "work" | "life" | "rest" | "social" | "self" | "other";
