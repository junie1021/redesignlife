interface ScoreRingProps {
  score: number;
  color: string;
}

export function ScoreRing({ score, color }: ScoreRingProps) {
  const circumference = 2 * Math.PI * 40;

  return (
    <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
      <circle cx="50" cy="50" r="40" fill="none" stroke="#F5EDE6" strokeWidth="10" />
      <circle
        cx="50" cy="50" r="40"
        fill="none"
        stroke={color}
        strokeWidth="10"
        strokeLinecap="round"
        strokeDasharray={`${circumference}`}
        strokeDashoffset={circumference - (score / 100) * circumference}
        style={{ transition: "stroke-dashoffset 1s ease" }}
      />
    </svg>
  );
}
