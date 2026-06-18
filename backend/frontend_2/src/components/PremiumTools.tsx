import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import type { MozMetrics, FastAuditCheck, KeywordInsight, SemrushVolume } from "../types";
import { fetchMozMetrics, fetchFastAudit, fetchKeywordResearch, fetchSemrushVolume } from "../services/api";
import AuthorityCard from "./AuthorityCard";
import TechnicalSecurityCard from "./TechnicalSecurityCard";
import AdvancedKeywordsCard from "./AdvancedKeywordsCard";
import { Shield, Search, Lock, Loader2 } from "lucide-react";
import UpgradeModal from "./UpgradeModal";

interface Props {
  url: string;
  domain: string;
}

export default function PremiumTools({ url, domain }: Props) {
  const { isPro } = useAuth();
  const [activeTool, setActiveTool] = useState<"authority" | "security" | "keywords">("authority");
  const [keywordInput, setKeywordInput] = useState("");
  const [showUpgrade, setShowUpgrade] = useState(false);

  const [mozData, setMozData] = useState<MozMetrics | null>(null);
  const [sslData, setSslData] = useState<FastAuditCheck | null>(null);
  const [robotsData, setRobotsData] = useState<FastAuditCheck | null>(null);
  const [sitemapData, setSitemapData] = useState<FastAuditCheck | null>(null);
  const [webShieldData, setWebShieldData] = useState<FastAuditCheck | null>(null);
  const [keywordResearch, setKeywordResearch] = useState<KeywordInsight | null>(null);
  const [semrushVolume, setSemrushVolume] = useState<SemrushVolume | null>(null);
  const [kwLoading, setKwLoading] = useState(false);

  useEffect(() => {
    if (!isPro) return;
    fetchMozMetrics(domain).then(setMozData);
    fetchFastAudit(url).then((r) => {
      setSslData(r.ssl);
      setRobotsData(r.robots);
      setSitemapData(r.sitemap);
      setWebShieldData(r.webShield);
    });
  }, [url, domain, isPro]);

  const handleKeywordSearch = async () => {
    if (!keywordInput.trim()) return;
    if (!isPro) { setShowUpgrade(true); return; }
    setKwLoading(true);
    const [kr, sv] = await Promise.all([
      fetchKeywordResearch(keywordInput.trim()),
      fetchSemrushVolume(keywordInput.trim()),
    ]);
    setKeywordResearch(kr);
    setSemrushVolume(sv);
    setKwLoading(false);
    setActiveTool("keywords");
  };

  const freeOverlay = (tool: string) => (
    <div className="absolute inset-0 bg-white/80 backdrop-blur-[1px] flex flex-col items-center justify-center rounded-xl z-10">
      <Lock size={28} className="text-slate-300 mb-2" />
      <p className="text-sm text-slate-500 mb-3">{tool} is available on the Pro plan</p>
      <button className="btn-primary text-sm px-4 py-2" onClick={() => setShowUpgrade(true)}>Upgrade to Pro</button>
    </div>
  );

  const TOOLS = [
    { id: "authority" as const, label: "Authority", icon: <Shield size={16} /> },
    { id: "security" as const, label: "Security", icon: <Shield size={16} /> },
    { id: "keywords" as const, label: "Keyword Insights", icon: <Search size={16} /> },
  ];

  return (
    <div className="premium-tools">
      <div className="flex items-center gap-2 mb-4">
        <h3 className="text-lg font-semibold text-slate-800">Advanced SEO Tools</h3>
        {!isPro && (
          <span className="text-xs font-medium text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">Pro</span>
        )}
      </div>

      <div className="flex gap-2 mb-5 overflow-x-auto pb-1">
        {TOOLS.map((tool) => (
          <button
            key={tool.id}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              activeTool === tool.id
                ? "bg-purple-100 text-purple-700"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
            onClick={() => setActiveTool(tool.id)}
          >
            {tool.icon}
            {tool.label}
          </button>
        ))}
      </div>

      <div className="relative">
        {!isPro && freeOverlay("Advanced SEO")}

        <div className={activeTool === "authority" ? "block" : "hidden"}>
          <AuthorityCard data={mozData || { status: "error", error: "Loading authority data..." }} domain={domain} />
        </div>

        <div className={activeTool === "security" ? "block" : "hidden"}>
          <TechnicalSecurityCard
            ssl={sslData || { status: "error", error: "Pending" }}
            robots={robotsData || { status: "error", error: "Pending" }}
            sitemap={sitemapData || { status: "error", error: "Pending" }}
            webShield={webShieldData || { status: "error", error: "Pending" }}
            url={domain}
          />
        </div>

        <div className={activeTool === "keywords" ? "block" : "hidden"}>
          <div className="mb-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={keywordInput}
                onChange={(e) => setKeywordInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleKeywordSearch()}
                placeholder="Enter a keyword to analyze..."
                className="flex-1 px-4 py-2.5 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-400"
              />
              <button
                onClick={handleKeywordSearch}
                disabled={kwLoading}
                className="px-5 py-2.5 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors disabled:opacity-50"
              >
                {kwLoading ? <Loader2 size={16} className="animate-spin" /> : "Analyze"}
              </button>
            </div>
          </div>
          <AdvancedKeywordsCard
            keywordResearch={keywordResearch}
            semrushVolume={semrushVolume}
            loading={kwLoading}
          />
        </div>
      </div>

      <UpgradeModal open={showUpgrade} onClose={() => setShowUpgrade(false)} feature="Advanced SEO Tools" />
    </div>
  );
}
