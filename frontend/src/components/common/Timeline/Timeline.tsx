import type { TimelineItem } from "@/types/ui";
import { formatDateTime } from "@/utils/format";

interface TimelineProps {
  items: TimelineItem[];
  emptyMessage?: string;
}

function Timeline({
  items,
  emptyMessage = "Sin movimientos registrados",
}: TimelineProps) {
  if (items.length === 0) {
    return <p className="muted">{emptyMessage}</p>;
  }

  return (
    <ol className="timeline">
      {items.map((item) => (
        <li key={item.id} className="timeline-item">
          <span className={`timeline-dot timeline-${item.tone ?? "neutral"}`} />
          <div>
            <p className="timeline-title">{item.title}</p>
            {item.detail && <p className="timeline-detail">{item.detail}</p>}
            <p className="timeline-meta">
              {item.actor ? `${item.actor} · ` : ""}
              {formatDateTime(item.date)}
            </p>
          </div>
        </li>
      ))}
    </ol>
  );
}

export default Timeline;
