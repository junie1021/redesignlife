import type { TypeKey } from "../types";

export interface QuestionOption {
  text: string;
  type: TypeKey;
}

export interface Question {
  text: string;
  options: QuestionOption[];
}

export const QUESTIONS: Question[] = [
  {
    text: "계획한 일이 예상대로 되지 않았을 때 나는?",
    options: [
      { text: "그냥 포기하고 싶어진다", type: "perfectionist" },
      { text: "일단 재미있는 걸 하면서 기분을 풀고 싶다", type: "dopamine" },
      { text: "주변 사람들의 도움부터 구하러 간다", type: "overloaded" },
      { text: "실패할까봐 걱정하면서 시작을 계속 미룬다", type: "worry" },
    ],
  },
  {
    text: "오늘 해야 할 일이 있는데 시작이 안 될 때 나는?",
    options: [
      { text: "유튜브나 SNS를 잠깐 보다가 시간이 다 간다", type: "dopamine" },
      { text: "더 완벽한 계획을 세우다가 정작 못 시작한다", type: "perfectionist" },
      { text: "막연한 불안감에 멍하니 있다가 시간이 간다", type: "worry" },
      { text: "다른 사람의 부탁을 먼저 해결하게 된다", type: "overloaded" },
    ],
  },
  {
    text: "하루 할 일 목록을 만들 때 나는?",
    options: [
      { text: "너무 많이 적어서 다 못 하면 지쳐버린다", type: "perfectionist" },
      { text: "계획은 세우는데 재밌는 것에 끌려 흐지부지된다", type: "dopamine" },
      { text: "실패할까봐 걱정돼서 아예 목록을 안 만들기도 한다", type: "worry" },
      { text: "내 할 일보다 남의 부탁이 자꾸 먼저 들어온다", type: "overloaded" },
    ],
  },
  {
    text: "하루를 마무리할 때 자주 드는 생각은?",
    options: [
      { text: "내일 또 잘 할 수 있을까? 불안하고 막막하다", type: "worry" },
      { text: "오늘도 계획대로 못 했어. 내일은 더 열심히 해야지", type: "perfectionist" },
      { text: "시간이 어디로 갔지? 콘텐츠 보다 보니 다 됐네", type: "dopamine" },
      { text: "오늘도 내 할 일보다 남의 일을 더 많이 한 것 같아", type: "overloaded" },
    ],
  },
];
