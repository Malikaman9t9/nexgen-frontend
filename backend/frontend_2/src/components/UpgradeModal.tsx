import { Crown, X, CheckCircle, ArrowUpRight } from "lucide-react";

interface Props {
  open: boolean;
  onClose: () => void;
  feature?: string;
}

export default function UpgradeModal({ open, onClose, feature }: Props) {
  if (!open) return null;

  return (
    <div className="upgrade-overlay" onClick={onClose}>
      <div className="upgrade-modal" onClick={(e) => e.stopPropagation()}>
        <button className="upgrade-close" onClick={onClose}>
          <X size={20} />
        </button>

        <div className="upgrade-icon">
          <Crown size={36} />
        </div>

        <h2 className="upgrade-title">Upgrade to Pro</h2>

        {feature && (
          <p className="upgrade-feature-name">
            Unlock <strong>{feature}</strong>
          </p>
        )}

        <ul className="upgrade-benefits">
          <li>
            <CheckCircle size={18} />
            Unlimited daily audits
          </li>
          <li>
            <CheckCircle size={18} />
            Bulk analysis for 100+ URLs
          </li>
          <li>
            <CheckCircle size={18} />
            White label DOCX &amp; HTML exports
          </li>
        </ul>

        <a
          href="https://nexgenweblab.com/pricing"
          className="btn-primary btn-full upgrade-cta"
        >
          <ArrowUpRight size={18} />
          Upgrade Now
        </a>

        <button className="upgrade-later" onClick={onClose}>
          Maybe later
        </button>
      </div>
    </div>
  );
}
