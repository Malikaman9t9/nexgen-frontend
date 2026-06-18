import type {
  OnPageData,
  SpeedData,
  TrafficData,
  AIResult,
  AIParagraphsResult,
  MozMetrics,
  FastAuditCheck,
  KeywordInsight,
  SemrushVolume,
} from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "";
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || "";
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || "";

export { SUPABASE_URL, SUPABASE_ANON_KEY };

async function fetchJSON<T>(url: string, body: Record<string, unknown>): Promise<T> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchHTMLPreview(
  url: string,
  onpage_data: OnPageData,
  speed_data: SpeedData | null,
  traffic_data: TrafficData | null,
  ai_suggestions: any[],
  agency_name: string,
  client_name: string,
  author_name: string,
  primaryColor?: string,
  secondaryColor?: string,
  whiteLabel?: boolean,
  language?: string,
  ai_paragraphs?: Record<string, string> | null,
): Promise<string> {
  const res = await fetch(`${API_BASE}/export/html/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      url,
      onpage_data,
      speed_data: speed_data || {},
      traffic_data: traffic_data || {},
      ai_suggestions,
      ai_paragraphs: ai_paragraphs || null,
      agency_name,
      client_name,
      author_name,
      primary_color: primaryColor || "#6D28D9",
      secondary_color: secondaryColor || "#DB2777",
      white_label: whiteLabel || false,
      language: language || "en",
    }),
  });
  if (!res.ok) throw new Error(`Preview error: ${res.status}`);
  return await res.text();
}

export async function fetchAIParagraphs(
  onpage_data: OnPageData,
  mobile_speed: number,
  desktop_speed: number
): Promise<AIParagraphsResult> {
  try {
    return await fetchJSON<AIParagraphsResult>(`${API_BASE}/ai/paragraphs`, {
      onpage_data: onpage_data as unknown as Record<string, unknown>,
      mobile_speed,
      desktop_speed,
    });
  } catch {
    return {
      status: "error",
      paragraphs: {
        executive_summary: "",
        onpage_analysis: "",
        speed_analysis: "",
        traffic_analysis: "",
      },
    };
  }
}

export async function fetchOnPage(url: string): Promise<OnPageData | null> {
  try {
    console.log("Fetching onpage from:", `${API_BASE}/onpage`, "with url:", url);
    const result = await fetchJSON<OnPageData | null>(`${API_BASE}/onpage`, { url });
    console.log("Onpage result:", result);
    return result;
  } catch (err) {
    console.error("Onpage fetch error:", err);
    return null;
  }
}

export async function fetchSpeed(url: string): Promise<SpeedData | null> {
  try {
    return await fetchJSON<SpeedData>(`${API_BASE}/speed`, { url });
  } catch {
    return null;
  }
}

export async function fetchTraffic(url: string): Promise<TrafficData> {
  try {
    return await fetchJSON<TrafficData>(`${API_BASE}/traffic`, { url });
  } catch {
    return {
      status: "Error",
      global_rank: "N/A",
      monthly_visits: "N/A",
      bounce_rate: "N/A",
      pages_per_visit: "N/A",
      avg_duration: "N/A",
      search_traffic: "N/A",
      direct_traffic: "N/A",
      social_traffic: "N/A",
      referral_traffic: "N/A",
      email_traffic: "N/A",
      monthly_visits_list: [],
      top_referrals: [],
      top_countries: [],
      top_keywords: [],
      raw_data: {},
    };
  }
}

export async function fetchAIRecommendations(
  onpage_data: OnPageData,
  mobile_speed: number,
  desktop_speed: number
): Promise<AIResult> {
  try {
    return await fetchJSON<AIResult>(`${API_BASE}/ai`, {
      onpage_data: onpage_data as unknown as Record<string, unknown>,
      mobile_speed,
      desktop_speed,
    });
  } catch {
    return { status: "error", recommendations: [] };
  }
}

export async function fetchExport(
  url: string,
  onpage_data: OnPageData,
  speed_data: SpeedData,
  traffic_data: TrafficData | null,
  ai_suggestions: Record<string, unknown>[],
  agency_name: string,
  client_name: string,
  author_name: string
): Promise<Blob | null> {
  try {
    const res = await fetch(`${API_BASE}/export`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, onpage_data, speed_data, traffic_data: traffic_data || {}, ai_suggestions, agency_name, client_name, author_name }),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Export failed (${res.status}): ${text}`);
    }
    return await res.blob();
  } catch (err) {
    console.error("fetchExport error:", err);
    return null;
  }
}

export async function fetchBulkExport(reports: {
  url: string;
  onpage_data: OnPageData;
  speed_data: SpeedData;
  traffic_data?: TrafficData;
  ai_suggestions: any[];
  client_name?: string;
}[]): Promise<Blob | null> {
  try {
    const res = await fetch(`${API_BASE}/export/bulk/html`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reports, agency_name: "NexGenWebLab" }),
    });
    if (!res.ok) throw new Error(`Bulk export error: ${res.status}`);
    return await res.blob();
  } catch {
    return null;
  }
}

// ── RapidAPI Suite ──

export async function fetchMozMetrics(domain: string): Promise<MozMetrics> {
  try {
    return await fetchJSON<MozMetrics>(`${API_BASE}/v2/moz-metrics`, { domains: [domain] });
  } catch {
    return { status: "error", error: "Failed to fetch Moz metrics" };
  }
}

export async function fetchFastAudit(url: string): Promise<{
  ssl: FastAuditCheck;
  robots: FastAuditCheck;
  sitemap: FastAuditCheck;
  webShield: FastAuditCheck;
}> {
  const [ssl, robots, sitemap, webShield] = await Promise.all([
    fetchJSON<FastAuditCheck>(`${API_BASE}/v2/fast/ssl-verify`, { url }).catch(() => ({ status: "error" as const, error: "SSL check failed" })),
    fetchJSON<FastAuditCheck>(`${API_BASE}/v2/fast/robots-txt`, { url }).catch(() => ({ status: "error" as const, error: "Robots.txt check failed" })),
    fetchJSON<FastAuditCheck>(`${API_BASE}/v2/fast/sitemap-detect`, { url }).catch(() => ({ status: "error" as const, error: "Sitemap detection failed" })),
    fetchJSON<FastAuditCheck>(`${API_BASE}/v2/fast/web-shield`, { url }).catch(() => ({ status: "error" as const, error: "Web shield scan failed" })),
  ]);
  return { ssl, robots, sitemap, webShield };
}

export async function fetchKeywordResearch(keyword: string, countryCode = "us"): Promise<KeywordInsight> {
  try {
    return await fetchJSON<KeywordInsight>(`${API_BASE}/v2/keyword-research`, { keyword, country_code: countryCode });
  } catch {
    return { status: "error", error: "Keyword research failed" };
  }
}

export async function fetchSemrushVolume(keyword: string, database = "us"): Promise<SemrushVolume> {
  try {
    return await fetchJSON<SemrushVolume>(`${API_BASE}/v2/semrush/global-volume`, { keyword, database });
  } catch {
    return { status: "error", error: "Semrush volume fetch failed" };
  }
}
