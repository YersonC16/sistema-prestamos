export type Tone = "success" | "warning" | "danger" | "info" | "neutral";

export interface TimelineItem {
  id: number | string;
  title: string;
  detail?: string | null;
  actor?: string | null;
  date: string;
  tone?: Tone;
}
