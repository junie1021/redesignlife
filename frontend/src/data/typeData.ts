import type { TypeKey, Task, ScheduleType } from "../types";

export interface TypeData {
  name: string;
  emoji: string;
  accentColor: string;
  tagBg: string;
  tagText: string;
  cardBg: string;
  traitBg: string;
  traitText: string;
  tagline: string;
  description: string;
  traits: string[];
  aiSummary: string;
  aiScore: number;
  problem: string;
  pattern: string;
  suggestion: string;
  initialTasks: Omit<Task, "id">[];
}

export const TYPE_DATA: Record<TypeKey, TypeData> = {
  perfectionist: {
    name: "완벽주의 나무늘보", emoji: "🦥", accentColor: "#F59E0B",
    tagBg: "bg-amber-100", tagText: "text-amber-700", cardBg: "bg-amber-50",
    traitBg: "bg-amber-100", traitText: "text-amber-700",
    tagline: "완벽한 계획, 느린 시작",
    description:
      "높은 기준을 가진 당신은 완벽하지 않으면 시작하기가 어려워요. 계획이 어긋나면 아예 포기해버리는 패턴이 나타나지만, 그건 게으름이 아니라 완벽함에 대한 열망이에요.",
    traits: [
      "계획이 조금만 어긋나도 전부 포기하고 싶어져요",
      "할 일 목록이 너무 완벽해서 실천하기가 힘들어요",
      "오늘 못 하면 내일 더 빡빡한 계획을 세워요",
    ],
    aiSummary: "오늘은 계획한 일 8개 중 3개를 완성했어요.",
    aiScore: 65,
    problem: "오늘의 목표가 8개였어요. 처음부터 너무 많이 잡아서 지치는 패턴이 보여요.",
    pattern: "계획이 많을수록 완성률이 낮아지는 경향이 있어요. 3개 완성이 8개 포기보다 훨씬 나아요.",
    suggestion: "내일은 딱 3가지만 도전해보세요. 작은 성공이 쌓이면 큰 변화가 생겨요 🌱",
    initialTasks: [
      { name: "운동 1시간",      done: true,  startTime: "07:00", endTime: "08:00", satisfaction: 5, scheduleType: "adjustable" as ScheduleType },
      { name: "영어 공부 2시간", done: true,  startTime: "09:00", endTime: "11:00", satisfaction: 4, scheduleType: "adjustable" as ScheduleType },
      { name: "프로젝트 보고서", done: false, startTime: "13:00", endTime: "14:30", satisfaction: 0, scheduleType: "adjustable" as ScheduleType },
      { name: "독서 30분",       done: false, startTime: "",      endTime: "",      satisfaction: 0, scheduleType: "adjustable" as ScheduleType },
      { name: "집 청소",         done: false, startTime: "",      endTime: "",      satisfaction: 0, scheduleType: "adjustable" as ScheduleType },
      { name: "친구에게 연락",   done: true,  startTime: "20:00", endTime: "20:30", satisfaction: 3, scheduleType: "adjustable" as ScheduleType },
      { name: "저녁 요리",       done: false, startTime: "",      endTime: "",      satisfaction: 0, scheduleType: "adjustable" as ScheduleType },
      { name: "일기 쓰기",       done: false, startTime: "",      endTime: "",      satisfaction: 0, scheduleType: "adjustable" as ScheduleType },
    ],
  },
  dopamine: {
    name: "도파민 청개구리", emoji: "🐸", accentColor: "#10B981",
    tagBg: "bg-emerald-100", tagText: "text-emerald-700", cardBg: "bg-emerald-50",
    traitBg: "bg-emerald-100", traitText: "text-emerald-700",
    tagline: "지금 이 순간의 재미를 거부하기 어려워요",
    description:
      "자극적인 것에 쉽게 끌리는 당신은 즉각적인 즐거움을 찾는 데 달인이에요. 해야 할 일이 있을수록 재밌는 것을 더 찾게 되는 건 의지력 부족이 아니에요.",
    traits: [
      "유튜브나 SNS를 잠깐만 볼 생각이었는데 시간이 다 가요",
      "해야 할 일이 많을수록 오히려 딴 것을 더 하게 돼요",
      "시작은 잘 했는데 흥미가 금방 사라져요",
    ],
    aiSummary: "오늘은 콘텐츠 시청이 계획보다 3시간 더 길어졌어요.",
    aiScore: 55,
    problem: "콘텐츠 시청 시간이 예상보다 3시간 더 걸렸어요. 과제 시작 자체가 어려웠어요.",
    pattern: "해야 할 일이 많을수록 먼저 쉬운 콘텐츠를 찾는 경향이 보여요. 환경을 바꾸는 게 열쇠예요.",
    suggestion: "내일은 과제를 4시간 하려고 하기보다, 15분만 시작해보는 건 어떨까요? ⏱️",
    initialTasks: [
      { name: "전공 수업",  done: true,  startTime: "09:00", endTime: "11:00", satisfaction: 3, scheduleType: "fixed" as ScheduleType },
      { name: "운동 30분",  done: true,  startTime: "07:30", endTime: "08:00", satisfaction: 4, scheduleType: "adjustable" as ScheduleType },
      { name: "과제 4시간", done: false, startTime: "14:00", endTime: "15:30", satisfaction: 0, scheduleType: "adjustable" as ScheduleType },
      { name: "독서 1시간", done: false, startTime: "",      endTime: "",      satisfaction: 0, scheduleType: "adjustable" as ScheduleType },
      { name: "저녁 요리",  done: true,  startTime: "18:30", endTime: "19:30", satisfaction: 3, scheduleType: "adjustable" as ScheduleType },
    ],
  },
  overloaded: {
    name: "과부하 개미", emoji: "🐜", accentColor: "#8B5CF6",
    tagBg: "bg-violet-100", tagText: "text-violet-700", cardBg: "bg-violet-50",
    traitBg: "bg-violet-100", traitText: "text-violet-700",
    tagline: "남의 부탁을 거절하기가 참 어려워요",
    description:
      "책임감이 강한 당신은 다른 사람의 요청을 먼저 처리하다보니 정작 내 할 일을 못 하게 돼요. 그 따뜻한 마음은 당신의 진짜 강점이에요.",
    traits: [
      "내 할 일이 있어도 남의 부탁을 먼저 들어줘요",
      "하루를 마무리하면 내 일보다 남의 일을 더 많이 한 느낌이에요",
      "거절하면 관계가 나빠질까봐 걱정이 돼요",
    ],
    aiSummary: "오늘 완성한 일 5개 중 3개가 다른 사람의 부탁이었어요.",
    aiScore: 70,
    problem: "내 할 일보다 남의 부탁을 더 많이 처리했어요. 프레젠테이션 준비를 못 했어요.",
    pattern: "부탁이 들어오면 내 일정보다 남의 일정을 먼저 채워주는 패턴이에요.",
    suggestion: "내일 오전 2시간은 나만의 집중 시간으로 미리 블록킹해보세요 🛡️",
    initialTasks: [
      { name: "팀 회의",           done: true,  startTime: "10:00", endTime: "11:30", satisfaction: 3, scheduleType: "fixed" as ScheduleType },
      { name: "운동 1시간",        done: true,  startTime: "07:00", endTime: "08:00", satisfaction: 5, scheduleType: "adjustable" as ScheduleType },
      { name: "프레젠테이션 준비", done: false, startTime: "",      endTime: "",      satisfaction: 0, scheduleType: "adjustable" as ScheduleType },
      { name: "개인 프로젝트",     done: false, startTime: "13:00", endTime: "13:30", satisfaction: 0, scheduleType: "adjustable" as ScheduleType },
      { name: "저녁 요리",         done: true,  startTime: "18:30", endTime: "19:30", satisfaction: 4, scheduleType: "adjustable" as ScheduleType },
    ],
  },
  worry: {
    name: "걱정인형", emoji: "🪆", accentColor: "#3B82F6",
    tagBg: "bg-blue-100", tagText: "text-blue-700", cardBg: "bg-blue-50",
    traitBg: "bg-blue-100", traitText: "text-blue-700",
    tagline: "시작하기 전에 걱정부터 앞서요",
    description:
      "신중한 당신은 실패할까봐, 잘 못할까봐 걱정이 많아요. 그 불안이 오히려 시작을 방해하고 있지만, 그 걱정은 당신이 결과를 얼마나 소중히 여기는지 보여줘요.",
    traits: [
      "시작하기 전에 걱정이 너무 많아서 미루게 돼요",
      "내일도 잘 할 수 있을까 하는 불안이 자주 들어요",
      "완벽하게 할 자신이 없으면 아예 시작을 못 해요",
    ],
    aiSummary: "오늘 시작 전 고민 시간이 실제 작업 시간보다 더 길었어요.",
    aiScore: 60,
    problem: "시작 전 준비 시간이 너무 길었어요. 보고서를 어떻게 써야 할지 고민하다가 결국 못 시작했어요.",
    pattern: "시작하기 전 걱정하는 시간이 실제 작업 시간보다 길어요. 걱정은 준비가 아니에요.",
    suggestion: "완벽하게 시작하지 않아도 괜찮아요. 내일은 파일만 열어보는 것부터 시작해봐요 💙",
    initialTasks: [
      { name: "운동 1시간",  done: true,  startTime: "07:00", endTime: "08:00", satisfaction: 4, scheduleType: "adjustable" as ScheduleType },
      { name: "보고서 작성", done: false, startTime: "10:00", endTime: "10:15", satisfaction: 0, scheduleType: "adjustable" as ScheduleType },
      { name: "요리 연습",   done: true,  startTime: "18:00", endTime: "19:00", satisfaction: 5, scheduleType: "adjustable" as ScheduleType },
      { name: "영어 공부",   done: false, startTime: "",      endTime: "",      satisfaction: 0, scheduleType: "adjustable" as ScheduleType },
    ],
  },
};
