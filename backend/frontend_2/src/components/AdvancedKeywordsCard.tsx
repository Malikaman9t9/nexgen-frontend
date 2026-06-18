import type { KeywordInsight, SemrushVolume } from "../types";
import { Search, TrendingUp, DollarSign, BarChart3, Lightbulb, Loader2, AlertCircle, MessageCircle } from "lucide-react";

interface Props {
  keywordResearch: KeywordInsight | null;
  semrushVolume: SemrushVolume | null;
  loading: boolean;
}

export default function AdvancedKeywordsCard({ keywordResearch, semrushVolume, loading }: Props) {
  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Search size={18} className="text-purple-500" />
          <h4 className="text-lg font-semibold text-slate-800">Advanced Keyword Insights</h4>
        </div>
        <div className="flex items-center justify-center py-8">
          <Loader2 size={24} className="animate-spin text-purple-500" />
        </div>
      </div>
    );
  }

  const krError = keywordResearch?.status === "error";
  const svError = semrushVolume?.status === "error";

  const relatedKeywords: string[] = keywordResearch?.data?.related_keywords ?? [];
  const questions: string[] = keywordResearch?.data?.questions ?? [];
  const volume = semrushVolume?.data?.volume;
  const cpc = keywordResearch?.data?.cpc ?? semrushVolume?.data?.cpc;
  const difficulty = keywordResearch?.data?.difficulty;

  if (krError && svError) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Search size={18} className="text-purple-500" />
          <h4 className="text-lg font-semibold text-slate-800">Advanced Keyword Insights</h4>
        </div>
        <div className="flex items-center gap-3 text-amber-600 bg-amber-50 rounded-lg p-4">
          <AlertCircle size={20} />
          <span className="text-sm">Keyword data unavailable. Enter a keyword to analyze.</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
      <div className="flex items-center gap-2 mb-5">
        <Search size={18} className="text-purple-500" />
        <h4 className="text-lg font-semibold text-slate-800">Advanced Keyword Insights</h4>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-5">
        {volume !== undefined && (
          <div className="bg-slate-50 rounded-lg p-3 text-center">
            <TrendingUp size={16} className="text-purple-500 mx-auto mb-1" />
            <div className="text-xs text-slate-500 mb-0.5">Search Volume</div>
            <div className="text-lg font-bold text-slate-800">
              {volume >= 1000 ? `${(volume / 1000).toFixed(1)}K` : volume}
            </div>
          </div>
        )}
        {cpc !== undefined && (
          <div className="bg-slate-50 rounded-lg p-3 text-center">
            <DollarSign size={16} className="text-green-500 mx-auto mb-1" />
            <div className="text-xs text-slate-500 mb-0.5">CPC</div>
            <div className="text-lg font-bold text-slate-800">${typeof cpc === "number" ? cpc.toFixed(2) : cpc}</div>
          </div>
        )}
        {difficulty !== undefined && (
          <div className="bg-slate-50 rounded-lg p-3 text-center">
            <BarChart3 size={16} className={difficulty < 30 ? "text-green-500" : difficulty < 60 ? "text-orange-500" : "text-red-500"} />
            <div className="text-xs text-slate-500 mb-0.5">Difficulty</div>
            <div className="text-lg font-bold text-slate-800">
              <span className={difficulty < 30 ? "text-green-600" : difficulty < 60 ? "text-orange-600" : "text-red-600"}>
                {difficulty}%
              </span>
            </div>
          </div>
        )}
        {volume === undefined && cpc === undefined && difficulty === undefined && (
          <div className="col-span-3 text-sm text-slate-400 text-center py-2">No metrics available</div>
        )}
      </div>

      {relatedKeywords.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-1.5 text-sm font-medium text-slate-700 mb-2">
            <Lightbulb size={14} className="text-amber-500" />
            Related Keywords
          </div>
          <div className="flex flex-wrap gap-1.5">
            {relatedKeywords.map((kw, i) => (
              <span key={i} className="px-2.5 py-1 bg-purple-50 text-purple-700 rounded-full text-xs font-medium">
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {questions.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 text-sm font-medium text-slate-700 mb-2">
            <MessageCircle size={14} className="text-blue-500" />
            People Also Ask
          </div>
          <div className="space-y-1.5">
            {questions.slice(0, 5).map((q, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-slate-600 bg-slate-50 rounded-lg p-2.5">
                <span className="text-blue-400 mt-0.5 shrink-0">Q:</span>
                <span>{q}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
