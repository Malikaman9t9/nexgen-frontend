import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import SiteAuditor from "./SiteAuditor";
import BulkAnalysis from "./BulkAnalysis";
import DemoBanner from "./DemoBanner";
import UpgradeModal from "./UpgradeModal";
import { Search, FileSpreadsheet, LogOut, Bolt, Crown, User, Menu, X, Lock, ArrowLeft } from "lucide-react";

export default function Layout() {
  const { user, isPro, planLabel, signOut, loading } = useAuth();
  const [menu, setMenu] = useState<"auditor" | "bulk">("auditor");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [auditKey, setAuditKey] = useState(0);
  const [showUpgrade, setShowUpgrade] = useState(false);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
      </div>
    );
  }

  const closeSidebar = () => setSidebarOpen(false);

  const handleBulkClick = () => {
    if (!isPro) {
      setShowUpgrade(true);
    } else {
      setMenu("bulk");
      closeSidebar();
    }
  };

  return (
    <div className="app-layout">
      <DemoBanner />

      <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
        {sidebarOpen ? <X size={22} /> : <Menu size={22} />}
      </button>

      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="sidebar-logo">
          <img src="/logo.png" alt="NexGenWebLab" className="logo-img" />
        </div>

        {user && (
          <div className="user-card">
            <div className="user-avatar">{user.email[0].toUpperCase()}</div>
            <div className="user-info">
              <div className="user-email">{user.email}</div>
              <div className={`user-plan ${isPro ? "plan-pro" : "plan-free"}`}>
                {isPro ? <Crown size={12} /> : <User size={12} />}
                {planLabel}
              </div>
            </div>
          </div>
        )}

        {!isPro && (
          <a href="https://nexgenweblab.com/upgrade" className="upgrade-banner">
            <Bolt size={14} />
            Upgrade to Pro
          </a>
        )}

        <button className="btn-logout" onClick={signOut}>
          <LogOut size={16} />
          Log Out
        </button>

        <hr className="sidebar-divider" />

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${menu === "auditor" ? "nav-active" : ""}`}
            onClick={() => { setMenu("auditor"); closeSidebar(); }}
          >
            <Search size={18} />
            Site Auditor
          </button>
          <button
            className={`nav-item ${menu === "bulk" ? "nav-active" : ""}`}
            onClick={handleBulkClick}
          >
            {isPro ? <FileSpreadsheet size={18} /> : <Lock size={18} />}
            Bulk Analysis
            {!isPro && <span className="nav-pro-badge">Pro</span>}
          </button>
        </nav>

        <hr className="sidebar-divider" />

        <button className="btn-new-audit" onClick={() => { setMenu("auditor"); setAuditKey((k) => k + 1); closeSidebar(); }}>
          Start New Audit
        </button>

        <a href="https://nexgenweblab.com" className="back-to-site">
          <ArrowLeft size={14} />
          Back to nexgenweblab.com
        </a>

        <div className="sidebar-footer">
          <span>NexGenWebLab v2.0</span>
        </div>
      </aside>

      {sidebarOpen && <div className="sidebar-overlay" onClick={closeSidebar} />}

      <main className="main-content">
        {menu === "auditor" ? <SiteAuditor key={auditKey} /> : <BulkAnalysis />}
      </main>

      <UpgradeModal open={showUpgrade} onClose={() => setShowUpgrade(false)} feature="Bulk Analysis" />
    </div>
  );
}
