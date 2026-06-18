import { useState, useRef } from "react";
import { useAuth } from "../context/AuthContext";
import { fetchOnPage, fetchSpeed, fetchAIRecommendations, fetchBulkExport } from "../services/api";
import type { BulkResult, AIRecommendation, OnPageData, SpeedData } from "../types";
import { Lock, Upload, Download, FileSpreadsheet, FileArchive } from "lucide-react";

export default function BulkAnalysis() {
  const { isPro } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [urls, setUrls] = useState<string[]>([]);
  const [results, setResults] = useState<BulkResult[]>([]);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [done, setDone] = useState(false);
  const [parseError, setParseError] = useState("");

  if (!isPro) {
    return (
      <div className="pro-lock-card">
        <Lock size={60} />
        <h2>Bulk Engine Locked</h2>
        <p>
          Bulk analysis is exclusive to Enterprise Pro. Audit hundreds of URLs at once.
        </p>
        <a href="https://nexgenweblab.com/upgrade" className="btn-primary btn-bulk-unlock">
          Unlock Enterprise Pro
        </a>
      </div>
    );
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setParseError("");
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const lines = text.split("\n").map((l) => l.trim()).filter(Boolean);
      const found: string[] = [];

      for (const line of lines) {
        const cols = line.split("\t");
        for (const col of cols) {
          const stripped = col.replace(/^["']|["']$/g, "").trim();
          if (stripped.startsWith("http") && !found.includes(stripped)) {
            found.push(stripped);
          }
        }
      }

      if (!found.length) {
        setParseError("No valid URLs (starting with http/https) found. Please ensure your file contains URLs.");
        return;
      }

      setUrls(found);
      setResults([]);
      setDone(false);
    } catch {
      setParseError("Failed to read file. Please upload a valid .txt or .csv file.");
    }
  };

  const handleProcess = async () => {
    if (!urls.length) return;
    setProcessing(true);
    setProgress(0);
    setDone(false);

    const bulkResults: BulkResult[] = [];

    for (let i = 0; i < urls.length; i++) {
      const url = urls[i];
      const pct = Math.round(((i + 1) / urls.length) * 100);
      setProgress(pct);

      const onpage = await fetchOnPage(url);
      const speed = await fetchSpeed(url);

      let aiRecommendations: AIRecommendation[] = [];
      let aiStatus = "";

      if (onpage) {
        const mPerf = speed?.mobile?.performance ?? 0;
        const dPerf = speed?.desktop?.performance ?? 0;
        const aiResult = await fetchAIRecommendations(onpage, mPerf, dPerf);
        aiRecommendations = aiResult.recommendations;
        aiStatus = aiResult.status;
      }

      bulkResults.push({ url, onpage, speed, ai_recommendations: aiRecommendations, ai_status: aiStatus });
    }

    setResults(bulkResults);
    setProcessing(false);
    setDone(true);
    setProgress(0);
  };

  const handleDownloadReport = (result: BulkResult) => {
    const domain = new URL(result.url).hostname.replace("www.", "");
    const text = generateReportText(result);
    const blob = new Blob([text], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${domain}_SEO_Report.txt`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const handleDownloadBulkReport = async () => {
    if (!results.length) return;
    
    const reports = results.map(r => ({
      url: r.url,
      onpage_data: r.onpage || {} as OnPageData,
      speed_data: r.speed || {} as SpeedData,
      ai_suggestions: r.ai_recommendations.map(ai => ({ title: ai.title, text: ai.text })),
      client_name: new URL(r.url).hostname.replace("www.", ""),
    }));
    
    const blob = await fetchBulkExport(reports);
    if (!blob) {
      alert("Failed to generate bulk report");
      return;
    }
    
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `bulk_seo_report_${Date.now()}.html`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <div className="bulk-analysis">
      <div className="hero-container">
        <h1 className="hero-title">Bulk <span>SEO</span> Analysis</h1>
      </div>

      <div className="bulk-card">
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.csv,.xlsx"
          onChange={handleFileUpload}
          style={{ display: "none" }}
        />
        <button className="btn-secondary btn-full" onClick={() => fileInputRef.current?.click()}>
          <Upload size={18} />
          Upload file with URLs
        </button>
        <p className="bulk-hint">Upload .txt or .csv file with URLs in any column</p>

        {parseError && <div className="error-banner">{parseError}</div>}

        {urls.length > 0 && !processing && (
          <div className="bulk-urls-info">
            <FileSpreadsheet size={20} />
            <span>Found {urls.length} unique URL(s).</span>
            <button className="btn-primary" onClick={handleProcess}>
              Generate Bulk Reports
            </button>
          </div>
        )}

        {processing && (
          <div className="progress-bar-container">
            <div className="progress-bar-track">
              <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
            </div>
            <span className="progress-text">Processing {progress}%</span>
          </div>
        )}

        {done && (
          <div className="bulk-results">
            <p className="bulk-success">Audited {results.length} URL(s). Download individual reports below or export all as HTML.</p>
            <div className="bulk-export-actions">
              <button className="btn-primary" onClick={handleDownloadBulkReport}>
                <FileArchive size={18} />
                Download All as HTML Report
              </button>
            </div>
            <hr className="section-divider" />
            {results.map((r, i) => (
              <div key={i} className="bulk-result-item">
                <span className="bulk-result-url">{r.url}</span>
                {r.onpage ? (
                  <button className="btn-secondary" onClick={() => handleDownloadReport(r)}>
                    <Download size={16} />
                    Download Report
                  </button>
                ) : (
                  <span className="bulk-failed">Failed to audit</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function generateReportText(result: BulkResult): string {
  const lines: string[] = [];
  lines.push("=".repeat(60));
  lines.push(`SEO AUDIT REPORT`);
  lines.push(`URL: ${result.url}`);
  lines.push("=".repeat(60));

  if (result.onpage) {
    lines.push("\n--- ON-PAGE SEO ---");
    lines.push(`Title: ${result.onpage.title}`);
    lines.push(`Meta Description: ${result.onpage.description}`);
    lines.push(`H1: ${result.onpage.h1.join(", ")}`);
    lines.push(`Word Count: ${result.onpage.word_count}`);
    lines.push(`HTTPS: ${result.onpage.is_https}`);
    lines.push(`Schema: ${result.onpage.schema}`);
    lines.push(`Missing ALT: ${result.onpage.missing_alt}`);
  }

  if (result.speed) {
    lines.push("\n--- SPEED ---");
    lines.push(`Mobile Performance: ${result.speed.mobile.performance}/100`);
    lines.push(`Desktop Performance: ${result.speed.desktop.performance}/100`);
  }

  if (result.ai_recommendations.length > 0) {
    lines.push("\n--- AI RECOMMENDATIONS ---");
    result.ai_recommendations.forEach((rec) => {
      lines.push(`\n${rec.title}`);
      lines.push(`  ${rec.text}`);
    });
  }

  return lines.join("\n");
}
