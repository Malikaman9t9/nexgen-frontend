import { useState } from "react";
import UrlInputBar from "./UrlInputBar";
import AuditOverview from "./AuditOverview";
import OnPageResults from "./OnPageResults";
import SpeedVitals from "./SpeedVitals";
import TrafficTab from "./TrafficTab";
import AiStrategy from "./AiStrategy";
import ExportTab from "./ExportTab";
import PremiumTools from "./PremiumTools";
import UpgradeModal from "./UpgradeModal";
import { useAuth } from "../context/AuthContext";
import { fetchOnPage, fetchSpeed, fetchTraffic, fetchAIRecommendations } from "../services/api";
import { calculateScores } from "../services/audit";
import type { OnPageData, SpeedData, TrafficData, AIResult } from "../types";
import { Globe, Zap, TrendingUp, Cpu, FileText, Layers } from "lucide-react";

const DAILY_LIMIT_FREE = 3;
const DAILY_LIMIT_KEY = "ngwl_audit_count";

function getDailyAudits(): number {
  try {
    const today = new Date().toISOString().slice(0, 10);
    const raw = localStorage.getItem(DAILY_LIMIT_KEY);
    if (!raw) return 0;
    const { date, count } = JSON.parse(raw);
    return date === today ? count : 0;
  } catch {
    return 0;
  }
}

function incrementDailyAudits(): void {
  try {
    const today = new Date().toISOString().slice(0, 10);
    const count = getDailyAudits() + 1;
    localStorage.setItem(DAILY_LIMIT_KEY, JSON.stringify({ date: today, count }));
  } catch {
    // localStorage may be full or unavailable
  }
}

function validateURL(input: string): { target: string; clean: string; error: string | null } {
  try {
    let url = input.trim();
    if (!url.startsWith("http://") && !url.startsWith("https://")) url = `https://${url}`;
    const parsed = new URL(url);
    const hostname = parsed.hostname.split("@").pop()?.split(":")[0] || "";
    const invalidHosts = ["localhost", "127.0.0.1", "0.0.0.0"];
    if (invalidHosts.some((h) => hostname.startsWith(h)) || hostname.startsWith("192.168.") || hostname.startsWith("10.") || hostname.startsWith("172."))
      return { target: "", clean: "", error: "Cannot audit local or private addresses. Please enter a public domain." };
    if (!parsed.hostname.includes("."))
      return { target: "", clean: "", error: "Please enter a valid domain with a proper extension (e.g., example.com)." };
    const clean = parsed.hostname.replace(/^www\./, "");
    return { target: url, clean, error: null };
  } catch {
    return { target: "", clean: "", error: "Invalid URL format. Please enter a valid domain (e.g., example.com)." };
  }
}

type TabId = "onpage" | "speed" | "traffic" | "ai" | "advanced" | "export";

export default function SiteAuditor() {
  const { isPro } = useAuth();
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressText, setProgressText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [_targetUrl, setTargetUrl] = useState("");
  const [domain, setDomain] = useState("");
  const [onpage, setOnpage] = useState<OnPageData | null>(null);
  const [speed, setSpeed] = useState<SpeedData | null>(null);
  const [traffic, setTraffic] = useState<TrafficData | null>(null);
  const [aiResult, setAiResult] = useState<AIResult>({ status: "", recommendations: [] });
  const [activeTab, setActiveTab] = useState<TabId>("onpage");
  const [showUpgrade, setShowUpgrade] = useState(false);

  const handleSubmit = async (rawUrl: string) => {
    if (!isPro) {
      const used = getDailyAudits();
      if (used >= DAILY_LIMIT_FREE) {
        setShowUpgrade(true);
        return;
      }
    }

    const { target, clean, error: valErr } = validateURL(rawUrl);
    if (valErr) { setError(valErr); return; }

    setError(null);
    setLoading(true);
    setTargetUrl(target);
    setDomain(clean);
    setActiveTab("onpage");

    setProgress(0); setProgressText("Initializing audit engine...");

    setProgress(15); setProgressText("Crawling page architecture...");
    const onpageData = await fetchOnPage(target);
    const fallback: OnPageData = {
      title: "Data Blocked", title_count: 0, description: "Data Blocked", desc_count: 0,
      h1: ["Blocked"], h2_count: 0, h3_count: 0, total_images: 0, missing_alt: 0,
      internal_links: 0, external_links: 0, canonical: "N/A", meta_robots: "N/A",
      has_noindex: false, lang: "N/A", og_title: "N/A", word_count: 0, schema: "Blocked",
      is_https: target.startsWith("https") ? "Yes" : "No",
      response_time: 0, html_size_kb: 0, unminified_css: 0, unminified_js: 0,
      dir_listing_secured: "Unknown",
    };
    const finalOnpage = onpageData ?? fallback;
    setOnpage(finalOnpage);

    setProgress(45); setProgressText("Running Core Web Vitals test...");
    const speedData = await fetchSpeed(target);
    setSpeed(speedData);

    setProgress(70); setProgressText(isPro ? "Fetching traffic intelligence..." : "Traffic analytics (Pro feature)");
    if (isPro) {
      const trafficData = await fetchTraffic(target);
      setTraffic(trafficData);
    } else {
      setTraffic(null);
    }

    setProgress(85); setProgressText("Generating AI recommendations...");
    const mPerf = speedData?.mobile?.performance ?? 0;
    const dPerf = speedData?.desktop?.performance ?? 0;
    const ai = await fetchAIRecommendations(finalOnpage, mPerf, dPerf);
    setAiResult(ai);

    setProgress(100); setProgressText("Audit complete.");
    setLoading(false);

    if (!isPro) incrementDailyAudits();
  };

  const scores = calculateScores(onpage, speed);
  const hasResults = !!onpage;

  const TABS: { id: TabId; label: string; icon: React.ReactNode; show?: boolean }[] = [
    { id: "onpage", label: "On-Page SEO", icon: <Globe size={16} /> },
    { id: "speed", label: "Speed Vitals", icon: <Zap size={16} /> },
    { id: "traffic", label: "Traffic", icon: <TrendingUp size={16} />, show: isPro && !!traffic },
    { id: "ai", label: "AI Strategy", icon: <Cpu size={16} /> },
    { id: "advanced", label: "Advanced", icon: <Layers size={16} /> },
    { id: "export", label: "Export", icon: <FileText size={16} /> },
  ];

  const visibleTabs = TABS.filter((t) => t.show !== false);

  return (
    <div className="site-auditor">
      {!isPro && (
        <div className="audit-limit-bar">
          <span>Free audits today: {getDailyAudits()}/{DAILY_LIMIT_FREE}</span>
          <a href="https://nexgenweblab.com/upgrade">Upgrade for unlimited</a>
        </div>
      )}

      <div className="hero-container">
        <h1 className="hero-title">Professional <span>SEO Auditor</span></h1>
        <p className="hero-subtitle">
          Analyze technical roadblocks, measure Core Web Vitals, and get AI-driven growth strategies for any website.
        </p>
      </div>

      <UrlInputBar onSubmit={handleSubmit} loading={loading} />

      {loading && (
        <div className="progress-bar-container">
          <div className="progress-bar-track">
            <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
          </div>
          <span className="progress-text">{progressText}</span>
        </div>
      )}

      {error && <div className="error-banner">{error}</div>}

      {hasResults && !loading && (
        <>
          <AuditOverview scores={scores} />

          <div className="tabs-container">
            <div className="tabs-bar">
              {visibleTabs.map((tab) => (
                <button
                  key={tab.id}
                  className={`tab-btn ${activeTab === tab.id ? "tab-active" : ""}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  {tab.icon}
                  {tab.label}
                </button>
              ))}
            </div>

            <div className="tab-content">
              {activeTab === "onpage" && onpage && <OnPageResults data={onpage} />}
              {activeTab === "speed" && speed && <SpeedVitals data={speed} />}
              {activeTab === "traffic" && traffic && <TrafficTab data={traffic} />}
              {activeTab === "ai" && <AiStrategy recommendations={aiResult.recommendations} status={aiResult.status} />}
              {activeTab === "advanced" && <PremiumTools url={_targetUrl || `https://${domain}`} domain={domain} />}
              {activeTab === "export" && (
                <ExportTab onpage={onpage} speed={speed} traffic={traffic} aiResult={aiResult} domain={domain} />
              )}
            </div>
          </div>
        </>
      )}

      <UpgradeModal open={showUpgrade} onClose={() => setShowUpgrade(false)} feature="unlimited audits" />
    </div>
  );
}
