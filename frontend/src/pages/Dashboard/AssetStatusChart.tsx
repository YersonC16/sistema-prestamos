import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { AssetSummary } from "@/types/asset";
import "./Charts.css";

interface AssetStatusChartProps {
  summary: AssetSummary;
}

const COLORS = {
  disponible: "#16a34a",
  prestado: "#2563eb",
  mantenimiento: "#d97706",
};

function AssetStatusChart({ summary }: AssetStatusChartProps) {
  const data = [
    { name: "Disponible", value: summary.disponible, color: COLORS.disponible },
    { name: "Prestado", value: summary.prestado, color: COLORS.prestado },
    {
      name: "Mantenimiento",
      value: summary.mantenimiento,
      color: COLORS.mantenimiento,
    },
  ].filter((item) => item.value > 0);

  if (summary.total === 0) {
    return <p className="muted chart-empty">Aún no hay activos registrados</p>;
  }

  return (
    <div className="chart-donut-wrapper">
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius={62}
            outerRadius={92}
            paddingAngle={3}
            cornerRadius={6}
            animationBegin={0}
            animationDuration={700}
            animationEasing="ease-out"
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.color} stroke="none" />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              borderRadius: 10,
              border: "1px solid var(--color-border)",
              fontSize: 13,
            }}
            formatter={(value, name) => [`${value} activos`, name]}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="chart-donut-center">
        <span className="chart-donut-total">{summary.total}</span>
        <span className="chart-donut-label">activos</span>
      </div>
      <div className="chart-legend">
        {data.map((item) => (
          <span key={item.name} className="chart-legend-item">
            <span
              className="chart-legend-dot"
              style={{ background: item.color }}
            />
            {item.name} ({item.value})
          </span>
        ))}
      </div>
    </div>
  );
}

export default AssetStatusChart;
