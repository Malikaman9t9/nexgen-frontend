import type { SpeedData } from "../types";
import { getScoreColor } from "../services/audit";
import { PieChart, Pie, Cell } from "recharts";
import { AlertTriangle, CheckCircle, Minus } from "lucide-react";

interface Props {
  data: SpeedData;
}

function Gauge({ score, label }: { score: number; label: string }) {
  const color = getScoreColor(score);
  const pieData = [
    { value: Math.max(score, 0) },
    { value: Math.max(100 - score, 0) },
  ];

  return (
    <div className="gauge-wrapper">
      <div className="gauge-chart">
        <PieChart width={120} height={130}>
          <Pie
            data={pieData}
            cx={60} cy={60}
            innerRadius={42} outerRadius={56}
            startAngle={90} endAngle={-270}
            dataKey="value" stroke="none"
          >
            <Cell fill={color} />
            <Cell fill="var(--slate-100)" />
          </Pie>
        </PieChart>
        <div className="gauge-score">{score}</div>
      </div>
      <div className="gauge-label">{label}</div>
    </div>
  );
}

function MetricRow({ label, value, score }: { label: string; value: string; score: number }) {
  let color = "var(--red)";
  let Icon = AlertTriangle;
  if (score >= 0.9) { color = "var(--green)"; Icon = CheckCircle; }
  else if (score >= 0.5) { color = "var(--amber)"; Icon = Minus; }

  return (
    <div className="speed-metric-card">
      <div className="metric-left">
        <Icon size={14} style={{ color }} />
        <span className="metric-label">{label}</span>
      </div>
      <span className="metric-value" style={{ color }}>{value}</span>
    </div>
  );
}

function DevicePanel({ device, label }: { device: SpeedData["mobile"]; label: string }) {
  const categories: { key: "performance" | "accessibility" | "best-practices" | "seo"; label: string }[] = [
    { key: "performance", label: "Performance" },
    { key: "accessibility", label: "Accessibility" },
    { key: "best-practices", label: "Best Practices" },
    { key: "seo", label: "SEO" },
  ];

  return (
    <div className="device-panel">
      <h5 className="device-title">{label} Device</h5>
      <div className="gauge-grid">
        {categories.map(({ key, label: catLabel }) => (
          <Gauge key={key} score={device[key] ?? 0} label={catLabel} />
        ))}
      </div>

      <div className="metrics-section">
        <div className="metrics-grid">
          <div className="metrics-col">
            <MetricRow label="First Contentful Paint (FCP)" value={device.metrics.fcp.value} score={device.metrics.fcp.score} />
            <MetricRow label="Total Blocking Time (TBT)" value={device.metrics.tbt.value} score={device.metrics.tbt.score} />
            <MetricRow label="Speed Index" value={device.metrics.si.value} score={device.metrics.si.score} />
          </div>
          <div className="metrics-col">
            <MetricRow label="Largest Contentful Paint (LCP)" value={device.metrics.lcp.value} score={device.metrics.lcp.score} />
            <MetricRow label="Cumulative Layout Shift (CLS)" value={device.metrics.cls.value} score={device.metrics.cls.score} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SpeedVitals({ data }: Props) {
  return (
    <div className="speed-vitals">
      <DevicePanel device={data.mobile} label="Mobile" />
      <hr className="section-divider" />
      <DevicePanel device={data.desktop} label="Desktop" />
    </div>
  );
}
