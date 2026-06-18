import { useState } from "react";
import { Search, Loader2 } from "lucide-react";

interface Props {
  onSubmit: (url: string) => void;
  loading: boolean;
}

export default function UrlInputBar({ onSubmit, loading }: Props) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    let url = input.trim();
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      url = `https://${url}`;
    }
    onSubmit(url);
  };

  return (
    <div className="url-bar-wrapper">
      <form onSubmit={handleSubmit} className="url-bar-form">
        <div className="url-prefix">https://</div>
        <input
          type="text"
          className="url-input"
          placeholder="yourdomain.com"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="btn-analyze" disabled={loading}>
          {loading ? <Loader2 size={20} className="spin" /> : <Search size={20} />}
          {loading ? "Analyzing..." : "Analyze Now"}
        </button>
      </form>
    </div>
  );
}
