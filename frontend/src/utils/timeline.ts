import type { TimelineItem } from "@/types/ui";
import { actionMeta } from "./labels";

interface HistoryLike {
  id: number;
  action: string;
  detail: string | null;
  performed_by: string;
  created_at: string;
}

export function toTimelineItems(entries: HistoryLike[]): TimelineItem[] {
  return entries.map((entry) => {
    const meta = actionMeta(entry.action);
    return {
      id: entry.id,
      title: meta.label,
      detail: entry.detail,
      actor: entry.performed_by,
      date: entry.created_at,
      tone: meta.tone,
    };
  });
}
