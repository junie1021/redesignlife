import { useState } from "react";
import { Star } from "lucide-react";

interface StarRatingProps {
  value: number;
  onChange: (value: number) => void;
  max?: number;
}

export function StarRating({ value, onChange, max = 5 }: StarRatingProps) {
  const [hovered, setHovered] = useState(0);

  return (
    <div className="flex gap-0.5">
      {Array.from({ length: max }, (_, i) => i + 1).map(s => (
        <button
          key={s}
          type="button"
          onClick={() => onChange(s === value ? 0 : s)}
          onMouseEnter={() => setHovered(s)}
          onMouseLeave={() => setHovered(0)}
          className="transition-transform hover:scale-110"
        >
          <Star
            className={`w-4 h-4 ${
              s <= (hovered || value)
                ? "text-amber-400 fill-amber-400"
                : "text-gray-200 fill-gray-200"
            }`}
          />
        </button>
      ))}
    </div>
  );
}
