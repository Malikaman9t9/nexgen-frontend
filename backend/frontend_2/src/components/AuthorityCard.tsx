import type { MozMetrics } from "../types";
import { Shield, TrendingUp, AlertCircle } from "lucide-react";

interface Props {
  data: MozMetrics;
  domain: string;
}

function CircularScore({ value, label, color }: { value: number; label: string; color: string }) {
  const radius = 48;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.min(value, 100) / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-28 h-28 flex items-center justify-center">
        <svg className="w-28 h-28 -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r={radius} fill="none" stroke="#f1f5f9" strokeWidth="8" />
          <circle
            cx="60" cy="60" r={radius}
            fill="none" stroke={color} strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />
        </svg>
        <span className="absolute text-2xl font-bold text-slate-800">{value}</span>
      </div>
      <span className="text-sm font-medium text-slate-500">{label}</span>
    </div>
  );
}

function getScoreColor(score: number): string {
  if (score >= 80) return "#16a34a";
  if (score >= 50) return "#ea580c";
  return "#dc2626";
}

function getScoreLabel(score: number): string {
  if (score >= 80) return "Strong";
  if (score >= 50) return "Moderate";
  return "Weak";
}

export default function AuthorityCard({ data, domain }: Props) {
  if (data.status === "error" || !data.data) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Shield size={18} className="text-purple-500" />
          <h4 className="text-lg font-semibold text-slate-800">Domain Authority</h4>
        </div>
        <div className="flex items-center gap-3 text-amber-600 bg-amber-50 rounded-lg p-4">
          <AlertCircle size={20} />
          <span className="text-sm">{data.error || "Authority data unavailable"}</span>
        </div>
      </div>
    );
  }

  const domainKey = Object.keys(data.data)[0];
  const metrics = domainKey ? data.data[domainKey] : null;
  const da = metrics?.da ?? 0;
  const pa = metrics?.pa ?? 0;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
      <div className="flex items-center gap-2 mb-6">
        <Shield size={18} className="text-purple-500" />
        <h4 className="text-lg font-semibold text-slate-800">Domain & Page Authority</h4>
      </div>

      <div className="flex items-center justify-evenly mb-6">
        <CircularScore value={da} label="Domain Authority (DA)" color={getScoreColor(da)} />
        <CircularScore value={pa} label="Page Authority (PA)" color={getScoreColor(pa)} />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="bg-slate-50 rounded-lg p-3 text-center">
          <div className="text-xs text-slate-500 mb-1">DA Rating</div>
          <div className="flex items-center justify-center gap-1">
            <TrendingUp size={14} className={da >= 50 ? "text-green-500" : "text-orange-500"} />
            <span className="text-sm font-semibold text-slate-700">{getScoreLabel(da)}</span>
          </div>
        </div>
        <div className="bg-slate-50 rounded-lg p-3 text-center">
          <div className="text-xs text-slate-500 mb-1">PA Rating</div>
          <div className="flex items-center justify-center gap-1">
            <TrendingUp size={14} className={pa >= 50 ? "text-green-500" : "text-orange-500"} />
            <span className="text-sm font-semibold text-slate-700">{getScoreLabel(pa)}</span>
          </div>
        </div>
      </div>

      <div className="mt-4 text-xs text-slate-400 text-center">
        Data via Moz API for <span className="font-medium text-slate-500">{domain}</span>
      </div>
    </div>
  );
}
