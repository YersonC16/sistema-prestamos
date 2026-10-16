import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { LoanSummary } from "@/types/loan";
import "./Charts.css";

interface LoanStatusChartProps {
  summary: LoanSummary;
}

const COLORS = { activo: "#2563eb", devuelto: "#16a34a", atrasado: "#dc2626" };

function LoanStatusChart({ summary }: LoanStatusChartProps) {
  const data = [
    { name: "Activos", value: summary.activo, color: COLORS.activo },
    { name: "Devueltos", value: summary.devuelto, color: COLORS.devuelto },
    { name: "Atrasados", value: summary.atrasado, color: COLORS.atrasado },
  ];

  if (summary.total === 0) {
    return (
      <p className="muted chart-empty">Aún no hay préstamos registrados</p>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart
        data={data}
        margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
      >
        <XAxis
          dataKey="name"
          tick={{ fontSize: 12, fill: "var(--color-text-light)" }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          allowDecimals={false}
          tick={{ fontSize: 12, fill: "var(--color-text-light)" }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          cursor={{ fill: "var(--color-background)" }}
          contentStyle={{
            borderRadius: 10,
            border: "1px solid var(--color-border)",
            fontSize: 13,
          }}
          formatter={(value) => [`${value} préstamos`, ""]}
        />
        <Bar
          dataKey="value"
          radius={[8, 8, 0, 0]}
          animationDuration={700}
          animationEasing="ease-out"
        >
          {data.map((entry) => (
            <Cell key={entry.name} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export default LoanStatusChart;
