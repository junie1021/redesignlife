import type { CatKey } from "../types";

export const CATS: Record<CatKey, { label: string; bg: string; text: string; dot: string }> = {
  exercise: { label: "운동/건강",     bg: "bg-emerald-100", text: "text-emerald-700", dot: "#10B981" },
  study:    { label: "학습/공부",     bg: "bg-blue-100",    text: "text-blue-700",    dot: "#3B82F6" },
  work:     { label: "업무/프로젝트", bg: "bg-violet-100",  text: "text-violet-700",  dot: "#8B5CF6" },
  life:     { label: "생활/살림",     bg: "bg-amber-100",   text: "text-amber-700",   dot: "#F59E0B" },
  rest:     { label: "휴식/여가",     bg: "bg-orange-100",  text: "text-orange-700",  dot: "#F97316" },
  social:   { label: "소통/관계",     bg: "bg-pink-100",    text: "text-pink-700",    dot: "#EC4899" },
  self:     { label: "자기계발",      bg: "bg-teal-100",    text: "text-teal-700",    dot: "#14B8A6" },
  other:    { label: "기타",          bg: "bg-gray-100",    text: "text-gray-600",    dot: "#9CA3AF" },
};

export function getCat(name: string): CatKey {
  if (/운동|헬스|요가|달리기|산책|수영/.test(name)) return "exercise";
  if (/공부|독서|영어|강의|학습|수업|복습/.test(name)) return "study";
  if (/보고서|프로젝트|과제|미팅|업무|발표|프레젠테이션|팀플/.test(name)) return "work";
  if (/청소|요리|장보기|빨래|살림/.test(name)) return "life";
  if (/유튜브|게임|SNS|영화|드라마|휴식|여가|콘텐츠/.test(name)) return "rest";
  if (/친구|연락|전화|만남|약속|팀원|후배|동생|심부름|수업/.test(name)) return "social";
  if (/일기|명상|계획|정리|준비/.test(name)) return "self";
  return "other";
}
