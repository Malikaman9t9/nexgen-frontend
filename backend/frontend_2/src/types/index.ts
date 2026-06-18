// ============================================================
// ON-PAGE SEO DATA (mirrors backend/modules/onpage_scraper.py)
// ============================================================
export interface OnPageData {
  title: string;
  title_count: number;
  description: string;
  desc_count: number;
  h1: string[];
  h2_count: number;
  h3_count: number;
  total_images: number;
  missing_alt: number;
  internal_links: number;
  external_links: number;
  canonical: string;
  meta_robots: string;
  has_noindex: boolean;
  lang: string;
  og_title: string;
  word_count: number;
  schema: string;
  is_https: "Yes" | "No";
  response_time: number;
  html_size_kb: number;
  unminified_css: number;
  unminified_js: number;
  dir_listing_secured: "Yes" | "No" | "Unknown";
}

// ============================================================
// SPEED DATA (mirrors backend/modules/speed_checker.py)
// ============================================================
export interface MetricValue {
  value: string;
  score: number;
}

export interface SpeedMetrics {
  fcp: MetricValue;
  lcp: MetricValue;
  tbt: MetricValue;
  cls: MetricValue;
  si: MetricValue;
}

export interface DeviceResult {
  performance: number;
  accessibility: number;
  "best-practices": number;
  seo: number;
  metrics: SpeedMetrics;
}

export interface SpeedData {
  mobile: DeviceResult;
  desktop: DeviceResult;
}

// ============================================================
// TRAFFIC DATA (mirrors backend/modules/traffic_checker.py)
// ============================================================
export interface TrafficData {
  status: string;
  global_rank: string;
  monthly_visits: string;
  bounce_rate: string;
  pages_per_visit: string;
  avg_duration: string;
  search_traffic: string;
  direct_traffic: string;
  social_traffic: string;
  referral_traffic: string;
  email_traffic: string;
  monthly_visits_list: { month: string; visits: number }[];
  top_countries: { country: string; visits: number; share: string }[];
  top_referrals: { source: string; visits: number }[];
  top_keywords: { keyword: string; visits: number; position: number }[];
  raw_data: Record<string, unknown>;
}

// ============================================================
// AI RECOMMENDATIONS (mirrors backend/modules/ai_analyzer.py)
// ============================================================
export interface AIRecommendation {
  title: string;
  text: string;
  icon?: string;
}

export interface AIResult {
  status: "success" | "error" | "no_api_key" | "";
  recommendations: AIRecommendation[];
}

export interface AIParagraphsResult {
  status: "success" | "error" | "no_api_key";
  paragraphs: {
    executive_summary: string;
    onpage_analysis: string;
    speed_analysis: string;
    traffic_analysis: string;
  };
}

// ============================================================
// AUDIT STATUS (mirrors backend app.py audit_status)
// ============================================================
export type AuditSeverity = "success" | "warning" | "danger" | "info";

export interface AuditStatus {
  message: string;
  severity: AuditSeverity;
  tip: string;
  actual: string;
}

// ============================================================
// SCORES (mirrors backend app.py calculate_scores)
// ============================================================
export interface AuditScores {
  overall: number;
  critical: number;
  warnings: number;
  passed: number;
}

// ============================================================
// USER (mirrors backend app.py user & plan)
// ============================================================
export type UserTier = "free" | "pro";

export interface UserMetadata {
  tier: UserTier;
}

export interface AppUser {
  email: string;
  user_metadata: UserMetadata;
  is_demo?: boolean;
}

// ============================================================
// AUDIT STATE
// ============================================================
export type AuditTab = "onpage" | "speed" | "ai" | "export";

export interface AuditState {
  url: string;
  domain: string;
  loading: boolean;
  progress: number;
  progressText: string;
  onpage: OnPageData | null;
  speed: SpeedData | null;
  traffic: TrafficData | null;
  ai: AIResult | null;
  error: string | null;
}

// ============================================================
// BULK ANALYSIS
// ============================================================
export interface BulkResult {
  url: string;
  onpage: OnPageData | null;
  speed: SpeedData | null;
  ai_recommendations: AIRecommendation[];
  ai_status: string;
}

// ============================================================
// RAPID API SUITE (backend/services/rapidapi_suite.py)
// ============================================================

export interface RapidAPIBase {
  status: "ok" | "error";
  error?: string;
}

export interface MozMetrics extends RapidAPIBase {
  data?: Record<string, { da: number; pa: number; [key: string]: unknown }>;
}

export interface FastAuditCheck extends RapidAPIBase {
  data?: { status?: string; ssl_valid?: boolean; has_robots?: boolean; has_sitemap?: boolean; xss_vulnerable?: boolean; [key: string]: unknown };
}

export interface KeywordInsight extends RapidAPIBase {
  data?: { related_keywords?: string[]; questions?: string[]; volume?: number; difficulty?: number; cpc?: number; [key: string]: unknown };
}

export interface SemrushVolume extends RapidAPIBase {
  data?: { volume?: number; cpc?: number; competition?: string; [key: string]: unknown };
}
