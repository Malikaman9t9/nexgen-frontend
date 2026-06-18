import type { FastAuditCheck } from "../types";
import { Shield, ShieldCheck, ShieldX, FileText, Globe, Search, Loader2, AlertCircle } from "lucide-react";

interface Props {
  ssl: FastAuditCheck;
  robots: FastAuditCheck;
  sitemap: FastAuditCheck;
  webShield: FastAuditCheck;
  url: string;
}

interface CheckItem {
  label: string;
  icon: React.ReactNode;
  data: FastAuditCheck;
  passKey: string;
  reverse?: boolean;
}

function resolveStatus(data: FastAuditCheck, passKey: string, reverse?: boolean): "pass" | "fail" | "unknown" | "loading" {
  if (data.status === "error") return "unknown";
  const raw = data.data?.[passKey];
  if (raw === undefined) return "unknown";
  const bool = Boolean(raw);
  return reverse ? (bool ? "fail" : "pass") : (bool ? "pass" : "fail");
}

function StatusBadge({ status }: { status: "pass" | "fail" | "unknown" | "loading" }) {
  const styles = {
    pass: "bg-emerald-50 text-emerald-700 border-emerald-200",
    fail: "bg-red-50 text-red-700 border-red-200",
    unknown: "bg-slate-50 text-slate-500 border-slate-200",
    loading: "bg-slate-50 text-slate-400 border-slate-200",
  };
  const labels = {
    pass: "Secure",
    fail: "Issue Found",
    unknown: "Not Checked",
    loading: "Checking...",
  };
  const icons = {
    pass: <ShieldCheck size={16} className="text-emerald-500" />,
    fail: <ShieldX size={16} className="text-red-500" />,
    unknown: <AlertCircle size={16} className="text-slate-400" />,
    loading: <Loader2 size={16} className="animate-spin text-slate-400" />,
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border ${styles[status]}`}>
      {icons[status]}
      {labels[status]}
    </span>
  );
}

export default function TechnicalSecurityCard({ ssl, robots, sitemap, webShield, url }: Props) {
  const checks: CheckItem[] = [
    { label: "SSL / HTTPS Certificate", icon: <Shield size={18} />, data: ssl, passKey: "ssl_valid" },
    { label: "Robots.txt", icon: <FileText size={18} />, data: robots, passKey: "has_robots" },
    { label: "XML Sitemap", icon: <Globe size={18} />, data: sitemap, passKey: "has_sitemap" },
    { label: "Web Shield (XSS)", icon: <Search size={18} />, data: webShield, passKey: "xss_vulnerable", reverse: true },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
      <div className="flex items-center gap-2 mb-4">
        <ShieldCheck size={18} className="text-purple-500" />
        <h4 className="text-lg font-semibold text-slate-800">Technical Security Audit</h4>
      </div>

      <div className="space-y-3">
        {checks.map((check) => {
          const status = resolveStatus(check.data, check.passKey, check.reverse);
          return (
            <div
              key={check.label}
              className="flex items-center justify-between p-3 rounded-lg border border-slate-100 bg-slate-50/50"
            >
              <div className="flex items-center gap-3">
                <span className="text-slate-400">{check.icon}</span>
                <span className="text-sm font-medium text-slate-700">{check.label}</span>
              </div>
              <StatusBadge status={status} />
            </div>
          );
        })}
      </div>

      <div className="mt-4 text-xs text-slate-400 text-center">
        Scanned via Fast Audit API for <span className="font-medium text-slate-500">{url}</span>
      </div>
    </div>
  );
}
