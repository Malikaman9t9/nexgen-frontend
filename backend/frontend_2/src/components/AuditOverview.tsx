import type { AuditScores } from "../types";
import { getScoreColor } from "../services/audit";
import { PieChart, Pie, Cell } from "recharts";
import { AlertTriangle, AlertCircle, CheckCircle } from "lucide-react";

interface Props {
  scores: AuditScores;
}

export default function AuditOverview({ scores }: Props) {
  const { overall, critical, warnings, passed } = scores;
  const color = getScoreColor(overall);

  const data = [
    { name: "Score", value: Math.max(overall, 0) },
    { name: "Remaining", value: Math.max(100 - overall, 0) },
  ];

  const getGrade = (s: number) => {
    if (s >= 90) return "A";
    if (s >= 80) return "B";
    if (s >= 70) return "C";
    if (s >= 60) return "D";
    return "F";
  };

  const getLabel = (s: number) => {
    if (s >= 90) return "Excellent";
    if (s >= 70) return "Good";
    if (s >= 50) return "Needs Work";
    return "Poor";
  };

  return (
    <div className="audit-overview">
      <div className="overview-header">
        <div>
          <h3>Audit Overview</h3>
          <span className="overview-sub">Comprehensive technical analysis</span>
        </div>
        <div className="overview-grade">
          <span className="grade-badge" style={{ background: color }}>{getGrade(overall)}</span>
          <span className="grade-label">{getLabel(overall)}</span>
        </div>
      </div>

      <div className="overview-body">
        <div className="overview-donut">
          <PieChart width={220} height={220}>
            <Pie
              data={data}
              cx={110} cy={110}
              innerRadius={75} outerRadius={100}
              startAngle={90} endAngle={-270}
              dataKey="value" stroke="none"
            >
              <Cell fill={color} />
              <Cell fill="#f1f5f9" />
            </Pie>
          </PieChart>
          <div className="donut-label">{overall}</div>
          <div className="donut-sublabel">out of 100</div>
        </div>

        <div className="overview-cards">
          <div className="issue-card issue-critical">
            <AlertTriangle size={24} className="issue-icon" />
            <div className="issue-count">{critical}</div>
            <div className="issue-label">Critical Issues</div>
          </div>
          <div className="issue-card issue-warning">
            <AlertCircle size={24} className="issue-icon" />
            <div className="issue-count">{warnings}</div>
            <div className="issue-label">Warnings</div>
          </div>
          <div className="issue-card issue-passed">
            <CheckCircle size={24} className="issue-icon" />
            <div className="issue-count">{passed}</div>
            <div className="issue-label">Passed Checks</div>
          </div>
        </div>
      </div>
    </div>
  );
}
