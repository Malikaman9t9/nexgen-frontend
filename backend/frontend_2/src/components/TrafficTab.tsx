import type { TrafficData } from "../types";
import { XAxis, YAxis, Tooltip, PieChart, Pie, Cell, ResponsiveContainer, CartesianGrid, LineChart, Line } from "recharts";
import { Globe, Users, Clock, Activity, Search, Share2, MousePointer, TrendingUp, MapPin } from "lucide-react";

interface Props {
  data: TrafficData;
}

function MetricCard({ icon, label, value, sub }: { icon: React.ReactNode; label: string; value: string; sub?: string }) {
  return (
    <div className="traffic-metric-card">
      <div className="traffic-metric-icon">{icon}</div>
      <div className="traffic-metric-body">
        <span className="traffic-metric-label">{label}</span>
        <span className="traffic-metric-value">{value}</span>
        {sub && <span className="traffic-metric-sub">{sub}</span>}
      </div>
    </div>
  );
}

const SOURCE_COLORS = ["var(--purple)", "var(--pink)", "var(--amber)", "var(--green)", "var(--blue)"];

export default function TrafficTab({ data }: Props) {
  const monthlyList = data.monthly_visits_list || [];
  const trendData = monthlyList.length > 0 
    ? monthlyList 
    : [];
    
  const sourceData = [
    { name: "Organic Search", value: data.search_traffic !== "N/A" ? parseFloat(data.search_traffic.replace('%', '')) : 0 },
    { name: "Direct", value: data.direct_traffic !== "N/A" ? parseFloat(data.direct_traffic.replace('%', '')) : 0 },
    { name: "Social", value: data.social_traffic !== "N/A" ? parseFloat(data.social_traffic.replace('%', '')) : 0 },
    { name: "Referral", value: data.referral_traffic !== "N/A" ? parseFloat(data.referral_traffic.replace('%', '')) : 0 },
  ];

  const totalSourceValue = sourceData.reduce((sum, s) => sum + s.value, 0);
  const displaySourceData = totalSourceValue > 0 
    ? sourceData.filter(s => s.value > 0)
    : sourceData.map(s => ({ ...s, value: 25 }));

  const topCountries = data.top_countries || [];
  const topKeywords = data.top_keywords || [];

  return (
    <div className="traffic-tab">
      <div className="traffic-grid">
        <MetricCard
          icon={<Globe size={20} />}
          label="Global Rank"
          value={data.global_rank}
        />
        <MetricCard
          icon={<Users size={20} />}
          label="Monthly Visits"
          value={data.monthly_visits}
        />
        <MetricCard
          icon={<Activity size={20} />}
          label="Bounce Rate"
          value={data.bounce_rate}
        />
        <MetricCard
          icon={<MousePointer size={20} />}
          label="Pages / Visit"
          value={data.pages_per_visit}
        />
        <MetricCard
          icon={<Clock size={20} />}
          label="Avg. Duration"
          value={data.avg_duration}
        />
        <MetricCard
          icon={<Search size={20} />}
          label="Organic Traffic"
          value={data.search_traffic}
        />
      </div>

      <div className="traffic-charts-row">
        <div className="traffic-chart-card">
          <div className="traffic-chart-header">
            <h5><Activity size={16} /> Monthly Visit Trend</h5>
          </div>
          <div className="traffic-chart-body">
            {trendData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={trendData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--slate-100)" />
                  <XAxis dataKey="month" tick={{ fontSize: 11, fill: "var(--slate-400)" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "var(--slate-400)" }} axisLine={false} tickLine={false} tickFormatter={(v) => v >= 1000 ? `${(v/1000).toFixed(0)}K` : v} />
                  <Tooltip formatter={(v) => [typeof v === 'number' ? v.toLocaleString() : v, 'Visits']} />
                  <Line type="monotone" dataKey="visits" stroke="var(--purple)" strokeWidth={3} dot={{ fill: "var(--purple)", r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="traffic-empty">
                <TrendingUp size={32} />
                <p>Monthly trend data unavailable</p>
              </div>
            )}
          </div>
        </div>

        <div className="traffic-chart-card">
          <div className="traffic-chart-header">
            <h5><Search size={16} /> Traffic Sources</h5>
          </div>
          <div className="traffic-chart-body">
            {displaySourceData.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie
                      data={displaySourceData}
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={80}
                      dataKey="value"
                      stroke="none"
                    >
                      {displaySourceData.map((_, i) => (
                        <Cell key={i} fill={SOURCE_COLORS[i % SOURCE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v) => (typeof v === "number" ? `${v.toFixed(1)}%` : v)} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="traffic-legend">
                  {displaySourceData.map((s, i) => (
                    <div key={s.name} className="traffic-legend-item">
                      <span className="legend-dot" style={{ background: SOURCE_COLORS[i] }} />
                      <span className="legend-label">{s.name}</span>
                      <span className="legend-value">{s.value.toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="traffic-empty">No source data available</div>
            )}
          </div>
        </div>
      </div>

      {topCountries.length > 0 && (
        <div className="traffic-section">
          <h5><MapPin size={16} /> Top Countries</h5>
          <div className="countries-grid">
            {topCountries.map((c, i) => (
              <div key={i} className="country-item">
                <span className="country-name">{c.country}</span>
                <span className="country-visits">{c.visits.toLocaleString()}</span>
                <span className="country-share">{c.share}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {topKeywords.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 mt-6">
          <div className="flex items-center gap-2 text-lg font-semibold text-slate-800 mb-4">
            <Search size={18} className="text-purple-500" />
            <span>Top Organic Keywords</span>
          </div>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr>
                <th className="text-sm font-medium text-slate-500 pb-3 border-b border-slate-100">Keyword</th>
                <th className="text-sm font-medium text-slate-500 pb-3 border-b border-slate-100">Monthly Visits</th>
                <th className="text-sm font-medium text-slate-500 pb-3 border-b border-slate-100">Position</th>
              </tr>
            </thead>
            <tbody>
              {topKeywords.slice(0, 10).map((kw, i) => (
                <tr key={i}>
                  <td className="py-3 text-sm text-slate-700 border-b border-slate-50 last:border-0">{kw.keyword}</td>
                  <td className="py-3 text-sm text-slate-700 border-b border-slate-50 last:border-0">{kw.visits.toLocaleString()}</td>
                  <td className="py-3 text-sm text-slate-700 border-b border-slate-50 last:border-0">
                    <span className="bg-purple-50 text-purple-700 px-2.5 py-1 rounded-full text-xs font-semibold">#{kw.position}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="traffic-insights">
        <h5><Share2 size={16} /> Traffic Distribution</h5>
        <div className="traffic-insights-grid">
          <div className="insight-item">
            <span className="insight-label">Search Traffic</span>
            <div className="insight-bar-track">
              <div className="insight-bar-fill" style={{ width: data.search_traffic !== "N/A" ? data.search_traffic : "0%", background: "var(--purple)" }} />
            </div>
            <span className="insight-value">{data.search_traffic}</span>
          </div>
          <div className="insight-item">
            <span className="insight-label">Direct Traffic</span>
            <div className="insight-bar-track">
              <div className="insight-bar-fill" style={{ width: data.direct_traffic !== "N/A" ? data.direct_traffic : "0%", background: "var(--pink)" }} />
            </div>
            <span className="insight-value">{data.direct_traffic}</span>
          </div>
          <div className="insight-item">
            <span className="insight-label">Social Traffic</span>
            <div className="insight-bar-track">
              <div className="insight-bar-fill" style={{ width: data.social_traffic !== "N/A" ? data.social_traffic : "0%", background: "var(--amber)" }} />
            </div>
            <span className="insight-value">{data.social_traffic}</span>
          </div>
        </div>
      </div>

      <div className="traffic-meta">
        <span>Social: {data.social_traffic}</span>
        <span>Global Rank: {data.global_rank}</span>
        <span>Status: {data.status}</span>
      </div>
    </div>
  );
}