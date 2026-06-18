import type { OnPageData } from "../types";
import { getAuditStatus, getSeverityClass } from "../services/audit";

interface Props {
  data: OnPageData;
}

function AuditCard({ label, data }: { label: string; data: ReturnType<typeof getAuditStatus> }) {
  const severityMap: Record<string, string> = {
    danger: "var(--red)",
    warning: "var(--amber)",
    success: "var(--green)",
    info: "var(--blue)",
  };

  return (
    <div className={`audit-item ${getSeverityClass(data.severity)}`}>
      <div className="audit-header">
        <div className="audit-status-dot" style={{ background: severityMap[data.severity] || "var(--slate-400)" }} />
        <div className="audit-item-content">
          <span className="audit-item-title">{label}</span>
          <span className="audit-item-desc">{data.message}</span>
        </div>
      </div>
      <div className="actual-data-box">{data.actual}</div>
      <details className="seo-tip">
        <summary>How to fix</summary>
        <p>{data.tip}</p>
      </details>
    </div>
  );
}

export default function OnPageResults({ data }: Props) {
  const contentPairs: [string, string][] = [
    ["Title Tag", "title"],
    ["Meta Description", "meta"],
    ["H1 Heading", "h1"],
    ["Content Length", "word_count"],
    ["Image ALT Attributes", "images"],
    ["Server Response Time", "response_time"],
    ["HTML Size", "html_size"],
    ["CSS Minification", "minified_css"],
    ["JS Minification", "minified_js"],
  ];

  const techPairs: [string, string][] = [
    ["Canonical URL", "canonical"],
    ["Meta Robots", "meta_robots"],
    ["HTML Language", "lang"],
    ["Open Graph Tags", "og"],
    ["Schema Markup", "schema"],
    ["SSL (HTTPS)", "https"],
    ["Directory Listing", "dir_listing"],
    ["Internal Links", "internal_links"],
    ["External Links", "external_links"],
  ];

  return (
    <div className="onpage-grid">
      <div>
        <h5 className="column-header">Content & Performance</h5>
        {contentPairs.map(([label, key]) => (
          <AuditCard key={key} label={label} data={getAuditStatus(data, key)} />
        ))}
      </div>
      <div>
        <h5 className="column-header">Technical & Advanced</h5>
        {techPairs.map(([label, key]) => (
          <AuditCard key={key} label={label} data={getAuditStatus(data, key)} />
        ))}
      </div>
    </div>
  );
}
