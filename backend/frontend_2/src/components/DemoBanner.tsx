import { useAuth } from "../context/AuthContext";
import { ShieldAlert, X } from "lucide-react";
import { useState } from "react";

export default function DemoBanner() {
  const { isDemo } = useAuth();
  const [dismissed, setDismissed] = useState(false);

  if (!isDemo || dismissed) return null;

  return (
    <div className="demo-banner">
      <ShieldAlert size={16} />
      <span>
        <strong>Demo Mode</strong> &mdash; You are viewing a preview.{" "}
        <a href="https://nexgenweblab.com/auth" className="demo-signup-link">
          Sign up free
        </a>{" "}
        to save your data and unlock full features.
      </span>
      <button className="demo-dismiss" onClick={() => setDismissed(true)}>
        <X size={16} />
      </button>
    </div>
  );
}
