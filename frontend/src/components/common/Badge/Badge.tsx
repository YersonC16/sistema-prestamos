import type { ReactNode } from "react";
import type { Tone } from "@/types/ui";

interface BadgeProps {
  children: ReactNode;
  tone?: Tone;
}

function Badge({ children, tone = "neutral" }: BadgeProps) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

export default Badge;
