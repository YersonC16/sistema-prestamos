import Icon from "@/components/common/Icon";
import type { IconName } from "@/components/common/Icon/Icon";
import type { Tone } from "@/types/ui";

interface StatCardProps {
  label: string;
  value: number | string;
  icon: IconName;
  tone?: Tone;
}

function StatCard({ label, value, icon, tone = "info" }: StatCardProps) {
  return (
    <div className="stat-card">
      <div className={`stat-icon stat-${tone}`}>
        <Icon name={icon} size={22} />
      </div>
      <div>
        <p className="stat-value">{value}</p>
        <p className="stat-label">{label}</p>
      </div>
    </div>
  );
}

export default StatCard;
