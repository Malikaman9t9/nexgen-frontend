import { useAuth } from "../context/AuthContext";
import UpgradeModal from "./UpgradeModal";
import type { AIRecommendation } from "../types";
import { Lightbulb, AlertCircle, Cpu, Sparkles, ArrowRight, Lock, Crown } from "lucide-react";
import { useState } from "react";

interface Props {
  recommendations: AIRecommendation[];
  status: string;
}

export default function AiStrategy({ recommendations, status }: Props) {
  const { isPro } = useAuth();
  const [showUpgrade, setShowUpgrade] = useState(false);

  return (
    <div className="ai-strategy">
      <div className="ai-header">
        <div>
          <h4>
            <Sparkles size={20} />
            AI Action Plan
          </h4>
          <span className="ai-subtitle">Strategic recommendations powered by Google Gemini</span>
        </div>
      </div>

      <div className={`ai-content ${!isPro ? "ai-blurred" : ""}`}>
        {recommendations.length > 0 && (
          <div className="ai-cards">
            {recommendations.map((rec, i) => (
              <div key={i} className="ai-card">
                <div className="ai-card-number">{String(i + 1).padStart(2, "0")}</div>
                <div className="ai-card-body">
                  <h5>{rec.title}</h5>
                  <p>{rec.text}</p>
                </div>
                <ArrowRight size={18} className="ai-card-arrow" />
              </div>
            ))}
            {status === "no_api_key" && (
              <div className="ai-fallback-notice">
                Gemini API key not configured — showing sample recommendations. Set GEMINI_API_KEY in backend .env for AI-powered suggestions.
              </div>
            )}
          </div>
        )}

        {!recommendations.length && status === "no_api_key" && (
          <div className="ai-info">
            <AlertCircle size={20} />
            <span>AI recommendations are not available because GEMINI_API_KEY is not configured.</span>
          </div>
        )}

        {!recommendations.length && status === "error" && (
          <div className="ai-info ai-error">
            <AlertCircle size={20} />
            <span>Failed to generate AI recommendations. Please try again later.</span>
          </div>
        )}

        {!recommendations.length && !status && (
          <div className="ai-info">
            <Lightbulb size={20} />
            <span>Run an audit to generate AI recommendations.</span>
          </div>
        )}
      </div>

      {!isPro && (
        <div className="ai-pro-overlay">
          <div className="ai-pro-overlay-content">
            <Lock size={32} />
            <h3>AI Strategy is a Pro Feature</h3>
            <p>Get detailed AI-powered recommendations to improve your SEO performance.</p>
            <button className="btn-primary" onClick={() => setShowUpgrade(true)}>
              <Crown size={16} />
              Upgrade to Pro
            </button>
          </div>
        </div>
      )}

      <div className="ai-footer">
        <Cpu size={14} />
        <span>Powered by Google Gemini 2.0 Flash</span>
      </div>

      <UpgradeModal open={showUpgrade} onClose={() => setShowUpgrade(false)} feature="AI Strategy" />
    </div>
  );
}
