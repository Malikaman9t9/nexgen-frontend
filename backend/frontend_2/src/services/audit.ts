// Audit helper functions mirroring backend app.py audit_status() & calculate_scores()

import type { OnPageData, SpeedData, AuditStatus, AuditSeverity, AuditScores } from "../types";

const TIPS: Record<string, string> = {
  title: "Keep title between 30-60 characters.",
  meta: "Meta description should be 150-160 characters.",
  h1: "Each page must have exactly one H1 tag.",
  images: "Add descriptive ALT attributes to all images.",
  word_count: "Aim for 300+ words per page.",
  schema: "Implement JSON-LD structured data markup.",
  https: "Ensure SSL certificate is active and valid.",
  html_size: "Keep HTML under 100KB for optimal performance.",
  response_time: "Server response time should be under 0.2s.",
  minified_css: "Minify all CSS files to reduce load time.",
  minified_js: "Minify all JavaScript files.",
  canonical: "Set a self-referencing canonical URL.",
  meta_robots: "Configure proper meta robots directives.",
  lang: "Declare the language attribute on the HTML tag.",
  og: "Set Open Graph meta tags for social sharing.",
  dir_listing: "Disable directory listing on your server.",
  internal_links: "Ensure a strong internal linking structure.",
  external_links: "Link to authoritative external sources.",
};

export function getAuditStatus(data: OnPageData, checkType: string): AuditStatus {
  try {
    switch (checkType) {
      case "title": {
        if (data.title && !data.title.includes("Missing")) {
          return {
            message: `Title Tag (${data.title_count} chars)`,
            severity: "success",
            tip: TIPS.title,
            actual: data.title,
          };
        }
        return { message: "Missing Title Tag", severity: "danger", tip: TIPS.title, actual: "N/A" };
      }
      case "meta": {
        if (data.description && !data.description.includes("Missing")) {
          return {
            message: `Meta Description (${data.desc_count} chars)`,
            severity: "success",
            tip: TIPS.meta,
            actual: data.description,
          };
        }
        return { message: "Missing Meta Description", severity: "danger", tip: TIPS.meta, actual: "N/A" };
      }
      case "h1": {
        if (data.h1 && data.h1.length > 0 && !data.h1.includes("Missing")) {
          return { message: "H1 Tag Present", severity: "success", tip: TIPS.h1, actual: data.h1.slice(0, 3).join(", ") };
        }
        return { message: "Missing H1 Heading", severity: "danger", tip: TIPS.h1, actual: "N/A" };
      }
      case "images": {
        const n = data.missing_alt || 0;
        if (n > 0) {
          return { message: `${n} image(s) missing ALT`, severity: "warning", tip: TIPS.images, actual: `${n} images without ALT` };
        }
        return { message: "All images have ALT attributes", severity: "success", tip: TIPS.images, actual: "Optimized" };
      }
      case "word_count": {
        const wc = data.word_count || 0;
        if (wc < 300) {
          return { message: `Low content (${wc} words)`, severity: "warning", tip: TIPS.word_count, actual: `${wc} words` };
        }
        return { message: `Good content (${wc} words)`, severity: "success", tip: TIPS.word_count, actual: `${wc} words` };
      }
      case "schema": {
        if (data.schema && !data.schema.includes("Missing")) {
          return { message: "Schema Markup Found", severity: "success", tip: TIPS.schema, actual: data.schema };
        }
        return { message: "Missing Schema Markup", severity: "danger", tip: TIPS.schema, actual: "N/A" };
      }
      case "https": {
        if (data.is_https === "Yes") {
          return { message: "HTTPS Secure", severity: "success", tip: TIPS.https, actual: "SSL active" };
        }
        return { message: "Not Secure (HTTP)", severity: "danger", tip: TIPS.https, actual: "No SSL" };
      }
      case "response_time": {
        const t = data.response_time || 0;
        if (t > 0.5) {
          return { message: `Slow response (${t.toFixed(2)}s)`, severity: "warning", tip: TIPS.response_time, actual: `${t.toFixed(2)}s` };
        }
        return { message: `Fast response (${t.toFixed(2)}s)`, severity: "success", tip: TIPS.response_time, actual: `${t.toFixed(2)}s` };
      }
      case "html_size": {
        const s = data.html_size_kb || 0;
        if (s > 100) {
          return { message: `Large HTML (${s.toFixed(1)} KB)`, severity: "warning", tip: TIPS.html_size, actual: `${s.toFixed(1)} KB` };
        }
        return { message: `Optimal HTML (${s.toFixed(1)} KB)`, severity: "success", tip: TIPS.html_size, actual: `${s.toFixed(1)} KB` };
      }
      case "minified_css": {
        const nc = data.unminified_css || 0;
        if (nc > 0) {
          return { message: `${nc} unminified CSS file(s)`, severity: "warning", tip: TIPS.minified_css, actual: `${nc} files` };
        }
        return { message: "CSS minified", severity: "success", tip: TIPS.minified_css, actual: "Optimized" };
      }
      case "minified_js": {
        const nj = data.unminified_js || 0;
        if (nj > 0) {
          return { message: `${nj} unminified JS file(s)`, severity: "warning", tip: TIPS.minified_js, actual: `${nj} files` };
        }
        return { message: "JS minified", severity: "success", tip: TIPS.minified_js, actual: "Optimized" };
      }
      case "dir_listing": {
        if (data.dir_listing_secured === "Yes") {
          return { message: "Directory listing secured", severity: "success", tip: TIPS.dir_listing, actual: "Secured" };
        }
        return { message: "Directory listing exposed", severity: "danger", tip: TIPS.dir_listing, actual: "Exposed!" };
      }
      default: {
        const labels: Record<string, string> = {
          canonical: "Canonical URL",
          meta_robots: "Meta Robots",
          lang: "HTML Language",
          og: "Open Graph Tags",
          internal_links: "Internal Links",
          external_links: "External Links",
        };
        const label = labels[checkType] || "SEO Factor";
        const val = String((data as unknown as Record<string, unknown>)[checkType] ?? "N/A");
        return { message: label, severity: "info", tip: TIPS[checkType] || "N/A", actual: val };
      }
    }
  } catch {
    return { message: "Error", severity: "danger", tip: "N/A", actual: "N/A" };
  }
}

export function getSeverityClass(severity: AuditSeverity): string {
  const map: Record<AuditSeverity, string> = {
    danger: "audit-danger",
    warning: "audit-warning",
    success: "audit-success",
    info: "audit-info",
  };
  return map[severity];
}

// mirrors backend app.py calculate_scores()
export function calculateScores(onpage: OnPageData | null, speed: SpeedData | null): AuditScores {
  if (!onpage) return { overall: 0, critical: 0, warnings: 0, passed: 0 };

  let critical = 0;
  let warnings = 0;
  let passed = 0;

  const hAlt = onpage.missing_alt || 0;
  const wCount = onpage.word_count || 0;
  const htmlS = onpage.html_size_kb || 0;
  const respT = onpage.response_time || 0;
  const unCss = onpage.unminified_css || 0;
  const unJs = onpage.unminified_js || 0;

  const checks: boolean[] = [
    onpage.title?.includes("Missing") ?? true,
    onpage.description?.includes("Missing") ?? true,
    !onpage.h1 || onpage.h1.length === 0 || onpage.h1.includes("Blocked"),
    !onpage.schema || onpage.schema === "Missing" || onpage.schema.includes("Blocked"),
    onpage.is_https === "No",
    onpage.dir_listing_secured === "No",
  ];
  for (const c of checks) {
    if (c) critical++;
    else passed++;
  }

  const warnChecks = [hAlt > 0, wCount < 300, htmlS > 100, respT > 0.5, unCss > 0, unJs > 0];
  for (const w of warnChecks) {
    if (w) warnings++;
    else passed++;
  }

  const onpageScore = Math.max(100 - critical * 9 - warnings * 3, 0);
  const mPerf = speed?.mobile?.performance ?? 50;
  const dPerf = speed?.desktop?.performance ?? 50;
  const overall = Math.round((onpageScore + (mPerf + dPerf) / 2) / 2);

  return { overall, critical, warnings, passed };
}

// Score color matching backend
export function getScoreColor(score: number): string {
  if (score < 50) return "var(--red)";
  if (score < 90) return "var(--amber)";
  return "var(--green)";
}
