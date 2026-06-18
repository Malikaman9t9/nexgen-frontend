import { useState, useEffect, useRef } from "react";
import { useAuth } from "../context/AuthContext";
import UpgradeModal from "./UpgradeModal";
import type { OnPageData, SpeedData, TrafficData, AIResult } from "../types";
import { fetchExport, fetchHTMLPreview, fetchAIParagraphs } from "../services/api";
import { Download, Eye, Settings, FileText, FileCode, Loader2, RotateCw, Lock, FileDown } from "lucide-react";

interface Props {
  onpage: OnPageData | null;
  speed: SpeedData | null;
  traffic: TrafficData | null;
  aiResult: AIResult | null;
  domain: string;
  url?: string;
}

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "es", label: "Español" },
  { code: "fr", label: "Français" },
  { code: "de", label: "Deutsch" },
  { code: "ar", label: "العربية" },
  { code: "zh", label: "中文" },
];

export default function ExportTab({ onpage, speed, traffic, aiResult, domain, url }: Props) {
  const { isPro } = useAuth();
  const [agency, setAgency] = useState("NexGenWebLab");
  const [author, setAuthor] = useState("SEO Team");
  const [client, setClient] = useState(domain || "Client");
  const [logoUrl, setLogoUrl] = useState("");
  const [primaryColor, setPrimaryColor] = useState("#6D28D9");
  const [secondaryColor, setSecondaryColor] = useState("#DB2777");
  const [whiteLabel, setWhiteLabel] = useState(false);
  const [language, setLanguage] = useState("en");
  const [activeTab, setActiveTab] = useState<"preview" | "customize" | "export">("preview");
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [aiParagraphs, setAiParagraphs] = useState<Record<string, string> | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (onpage && activeTab === "preview") {
      generatePreview();
    }
  }, [onpage, primaryColor, secondaryColor, agency, language]);

  const generatePreview = async () => {
    if (!onpage) return;
    setPreviewLoading(true);
    try {
      const [html, paragraphsRes] = await Promise.all([
        fetchHTMLPreview(
          url || `https://${domain}`,
          onpage,
          speed,
          traffic,
          aiResult?.recommendations || [],
          agency,
          client,
          author,
          primaryColor,
          secondaryColor,
          whiteLabel,
          language,
          aiParagraphs,
        ),
        fetchAIParagraphs(
          onpage,
          speed?.mobile?.performance ?? 0,
          speed?.desktop?.performance ?? 0,
        ),
      ]);
      const paragraphs = paragraphsRes.status === "success" ? paragraphsRes.paragraphs : null;
      setAiParagraphs(paragraphs);
      const htmlWithParagraphs = await fetchHTMLPreview(
        url || `https://${domain}`,
        onpage,
        speed,
        traffic,
        aiResult?.recommendations || [],
        agency,
        client,
        author,
        primaryColor,
        secondaryColor,
        whiteLabel,
        language,
        paragraphs,
      );
      setPreviewUrl(htmlWithParagraphs || html);
    } catch (err) {
      console.error("Preview error:", err);
      if (!previewUrl) {
        try {
          const fallback = await fetchHTMLPreview(
            url || `https://${domain}`, onpage, speed, traffic,
            aiResult?.recommendations || [], agency, client, author,
            primaryColor, secondaryColor, whiteLabel, language,
          );
          setPreviewUrl(fallback);
        } catch { /* ignore */ }
      }
    }
    setPreviewLoading(false);
  };

  const handleDownloadPDF = async () => {
    if (!isPro) {
      setShowUpgrade(true);
      return;
    }
    if (!previewUrl) return;
    setPdfLoading(true);
    try {
      const { default: html2pdf } = await import("html2pdf.js");
      const container = document.createElement("div");
      container.innerHTML = previewUrl;
      container.style.position = "fixed";
      container.style.left = "-9999px";
      container.style.top = "0";
      document.body.appendChild(container);

      await html2pdf().set({
        margin: 0,
        filename: `${client.replace(/\s+/g, "_")}_SEO_Report.pdf`,
        image: { type: "jpeg", quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: { unit: "in", format: "letter", orientation: "portrait" },
      }).from(container).save();

      document.body.removeChild(container);
    } catch (err) {
      console.error("PDF generation error:", err);
      setErrorMessage("Failed to generate PDF. Please try again.");
    }
    setPdfLoading(false);
  };

  const handleDownloadDOCX = async () => {
    if (!isPro) {
      setShowUpgrade(true);
      return;
    }
    if (!onpage) {
      setErrorMessage("Please run an On-Page SEO audit first to download the report.");
      return;
    }
    setLoading(true);
    try {
      const blob = await fetchExport(
        url || `https://${domain}`,
        onpage,
        speed || { mobile: { performance: 0, accessibility: 0, "best-practices": 0, seo: 0, metrics: { fcp: { value: "N/A", score: 0 }, lcp: { value: "N/A", score: 0 }, tbt: { value: "N/A", score: 0 }, cls: { value: "N/A", score: 0 }, si: { value: "N/A", score: 0 } } }, desktop: { performance: 0, accessibility: 0, "best-practices": 0, seo: 0, metrics: { fcp: { value: "N/A", score: 0 }, lcp: { value: "N/A", score: 0 }, tbt: { value: "N/A", score: 0 }, cls: { value: "N/A", score: 0 }, si: { value: "N/A", score: 0 } } } } as SpeedData,
        traffic,
        aiResult?.recommendations.map(r => ({ ...r })) || [],
        agency,
        client,
        author,
      );
      if (!blob) {
        setErrorMessage("Failed to generate report. Please try again.");
        setLoading(false);
        return;
      }
      const downloadUrl = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = `${client.replace(/\s+/g, "_")}_SEO_Report.docx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      console.error("Download error:", err);
      const downloadErrMsg = err instanceof Error ? err.message : "Unknown error occurred";
      setErrorMessage(`Error downloading report: ${downloadErrMsg}.`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadHTML = () => {
    if (!isPro) {
      setShowUpgrade(true);
      return;
    }
    if (!previewUrl) return;
    const a = document.createElement("a");
    a.href = previewUrl;
    a.download = `${client.replace(/\s+/g, "_")}_SEO_Report.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const FreeOverlay = () => (
    <div className="export-free-overlay">
      <Lock size={32} />
      <h3>Export Locked</h3>
      <p>DOCX and HTML exports are available on the Pro plan.</p>
      <button className="btn-primary" onClick={() => setShowUpgrade(true)}>
        Upgrade to Pro
      </button>
    </div>
  );

  return (
    <div className="export-container">
      <div className="export-tabs">
        <button className={`export-tab-btn ${activeTab === "preview" ? "active" : ""}`} onClick={() => setActiveTab("preview")}>
          <Eye size={16} /> Preview
        </button>
        <button className={`export-tab-btn ${activeTab === "customize" ? "active" : ""}`} onClick={() => setActiveTab("customize")}>
          <Settings size={16} /> Customize
        </button>
        <button className={`export-tab-btn ${activeTab === "export" ? "active" : ""}`} onClick={() => setActiveTab("export")}>
          <Download size={16} /> Export
        </button>
      </div>

      {errorMessage && (
        <div className="error-banner" style={{ margin: "12px 16px 0" }}>
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage(null)} style={{ marginLeft: 12, fontWeight: 700, background: "none", border: "none", color: "inherit", cursor: "pointer" }}>✕</button>
        </div>
      )}

      {activeTab === "preview" && (
        <div className="preview-panel">
          <div className="preview-toolbar">
            <span className="preview-label">
              {previewLoading ? (
                <>
                  <Loader2 size={14} className="spin" /> Generating preview...
                </>
              ) : (
                <>
                  <FileCode size={14} /> HTML Report Preview
                </>
              )}
            </span>
            <div className="preview-actions">
              <button className="preview-btn" onClick={generatePreview} disabled={previewLoading}>
                <RotateCw size={14} /> Refresh
              </button>
              <button className="preview-btn" onClick={handleDownloadPDF} disabled={!previewUrl || pdfLoading}>
                {pdfLoading ? <Loader2 size={14} className="spin" /> : <FileDown size={14} />}
                {pdfLoading ? "Generating PDF..." : "Download PDF (High Quality)"}
              </button>
            </div>
          </div>
          <div className="preview-frame-container">
            {!isPro && <FreeOverlay />}
            {previewLoading && (
              <div className="preview-loading">
                <Loader2 size={32} className="spin" />
                <p>Generating your report...</p>
              </div>
            )}
            {previewUrl && !previewLoading && (
              <iframe ref={iframeRef} srcDoc={previewUrl} className="preview-iframe" title="Report Preview" />
            )}
            {!onpage && !previewLoading && (
              <div className="preview-empty">
                <FileText size={48} />
                <p>Run an audit to preview the report</p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "customize" && (
        <div className="customize-panel">
          <div className="customize-section">
            <h5>Branding</h5>
            <div className="customize-field">
              <label>Agency / Company Name</label>
              <input type="text" value={agency} onChange={(e) => setAgency(e.target.value)} placeholder="Your Company Name" />
            </div>
            <div className="customize-field">
              <label>Report Author</label>
              <input type="text" value={author} onChange={(e) => setAuthor(e.target.value)} placeholder="Author Name" />
            </div>
            <div className="customize-field">
              <label>Logo URL (optional)</label>
              <input type="text" value={logoUrl} onChange={(e) => setLogoUrl(e.target.value)} placeholder="https://yoursite.com/logo.png" />
            </div>
          </div>

          <div className="customize-section">
            <h5>Client Info</h5>
            <div className="customize-field">
              <label>Client / Project Name</label>
              <input type="text" value={client} onChange={(e) => setClient(e.target.value)} placeholder="Client Name" />
            </div>
          </div>

          <div className="customize-section">
            <h5>Colors</h5>
            <div className="customize-row">
              <div className="customize-field">
                <label>Primary Color</label>
                <div className="color-input-group">
                  <input type="color" value={primaryColor} onChange={(e) => setPrimaryColor(e.target.value)} />
                  <input type="text" value={primaryColor} onChange={(e) => setPrimaryColor(e.target.value)} />
                </div>
              </div>
              <div className="customize-field">
                <label>Secondary Color</label>
                <div className="color-input-group">
                  <input type="color" value={secondaryColor} onChange={(e) => setSecondaryColor(e.target.value)} />
                  <input type="text" value={secondaryColor} onChange={(e) => setSecondaryColor(e.target.value)} />
                </div>
              </div>
            </div>
          </div>

          <div className="customize-section">
            <h5>Language</h5>
            <div className="customize-field">
              <label>Report Language</label>
              <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                {LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>{lang.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="customize-section">
            <h5>White Label</h5>
            <label className="toggle-field">
              <input type="checkbox" checked={whiteLabel} onChange={(e) => setWhiteLabel(e.target.checked)} />
              <span>Remove NexGenWebLab branding</span>
            </label>
          </div>
        </div>
      )}

      {activeTab === "export" && (
        <div className="export-panel">
          <div className="export-options">
            <div className="export-card" style={{ opacity: !onpage ? 0.5 : 1, pointerEvents: !onpage ? "none" : "auto" }}>
              <div className="export-card-icon">
                <FileText size={32} />
              </div>
              <h5>Word Document (DOCX)</h5>
              <p>Download as editable .docx file for Microsoft Word</p>
              <button className="export-btn" disabled={!onpage || loading} onClick={(e) => { e.stopPropagation(); handleDownloadDOCX(); }}>
                {loading ? <Loader2 size={16} className="spin" /> : <Download size={16} />}
                {isPro ? "Download DOCX" : "Pro Feature"}
              </button>
            </div>

            <div className="export-card" style={{ opacity: !onpage ? 0.5 : 1, pointerEvents: !onpage ? "none" : "auto" }}>
              <div className="export-card-icon">
                <FileCode size={32} />
              </div>
              <h5>HTML Report</h5>
              <p>Download as HTML file - can be opened in any browser</p>
              <button className="export-btn" disabled={!onpage} onClick={(e) => { e.stopPropagation(); handleDownloadHTML(); }}>
                <Download size={16} />
                {isPro ? "Download HTML" : "Pro Feature"}
              </button>
            </div>
          </div>

          <div className="export-info">
            <div className="export-info-item">
              <span className="info-label">Target URL:</span>
              <span className="info-value">{url || `https://${domain}`}</span>
            </div>
            <div className="export-info-item">
              <span className="info-label">Agency:</span>
              <span className="info-value">{agency}</span>
            </div>
            <div className="export-info-item">
              <span className="info-label">Client:</span>
              <span className="info-value">{client}</span>
            </div>
          </div>
        </div>
      )}

      <UpgradeModal open={showUpgrade} onClose={() => setShowUpgrade(false)} feature="report exports" />
    </div>
  );
}
