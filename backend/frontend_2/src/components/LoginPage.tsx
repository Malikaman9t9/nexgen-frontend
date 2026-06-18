import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Mail, Lock, Eye, EyeOff, Loader2 } from "lucide-react";

type FormMode = "signin" | "signup";

interface FieldErrors {
  email?: string;
  password?: string;
}

export default function LoginPage() {
  const { signIn, signUp, resetPassword, signInWithGoogle, supabase } = useAuth();
  const [mode, setMode] = useState<FormMode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [submitError, setSubmitError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resetSent, setResetSent] = useState(false);

  const validate = (): boolean => {
    const errs: FieldErrors = {};
    if (!email.trim()) errs.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(email)) errs.email = "Please enter a valid email";
    if (!password) errs.password = "Password is required";
    else if (mode === "signup" && password.length < 6) errs.password = "Password must be at least 6 characters";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError("");
    if (!validate()) return;
    setLoading(true);

    const err = mode === "signin" ? await signIn(email, password) : await signUp(email, password);
    setLoading(false);
    if (err) setSubmitError(err);
  };

  const handleForgotPassword = async () => {
    if (!email.trim()) {
      setErrors({ email: "Enter your email address first" });
      return;
    }
    setSubmitError("");
    setLoading(true);
    const err = await resetPassword(email);
    setLoading(false);
    if (err) setSubmitError(err);
    else setResetSent(true);
  };

  const toggleMode = () => {
    setMode(mode === "signin" ? "signup" : "signin");
    setErrors({});
    setSubmitError("");
    setResetSent(false);
  };

  const hasGoogleOAuth = !!supabase;

  return (
    <div className="login-split">
      <div className="login-brand-panel">
        <div className="login-brand-top">
          <img src="/logo.png" alt="NexGenWebLab" className="login-brand-logo-img" />
        </div>
        <div className="login-brand-center">
          <h1 className="login-brand-title">
            Professional SEO<br />
            <span>Audit Platform</span>
          </h1>
          <ul className="login-brand-features">
            <li>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              Trusted by 2,400+ SEO professionals
            </li>
            <li>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              Deep audits with 117+ checkpoints
            </li>
            <li>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              AI-powered growth recommendations
            </li>
          </ul>
        </div>
        <div className="login-brand-bottom">
          <div className="login-brand-testimonial">
            <div className="testimonial-avatars">
              <div className="tav" style={{ background: "var(--purple)" }}>SK</div>
              <div className="tav" style={{ background: "var(--pink)" }}>MJ</div>
              <div className="tav" style={{ background: "var(--green)" }}>AP</div>
            </div>
            <p className="testimonial-text">Join 2,400+ SEO professionals growing their agencies</p>
          </div>
        </div>
      </div>

      <div className="login-form-panel">
        <div className="login-form-container">
          <p className="login-welcome">Welcome back</p>
          <p className="login-welcome-sub">
            {mode === "signin" ? "Sign in to your account." : "Create your free account."}
          </p>

          <div className="login-tabs" role="tablist">
            <button
              className={`login-tab ${mode === "signin" ? "active" : ""}`}
              role="tab"
              aria-selected={mode === "signin"}
              onClick={() => mode !== "signin" && toggleMode()}
            >
              Sign In
            </button>
            <button
              className={`login-tab ${mode === "signup" ? "active" : ""}`}
              role="tab"
              aria-selected={mode === "signup"}
              onClick={() => mode !== "signup" && toggleMode()}
            >
              Create Account
            </button>
          </div>

          <form onSubmit={handleSubmit} className="login-form-body" noValidate>
            {submitError && <div className="login-submit-error">{submitError}</div>}
            {resetSent && (
              <div className="login-reset-sent">
                Password reset email sent. Check your inbox.
              </div>
            )}

            <div className="login-field">
              <label>Email Address</label>
              <div className={`input-wrapper ${errors.email ? "input-error" : ""}`}>
                <Mail size={18} className="input-icon" />
                <input
                  type="email"
                  placeholder="you@agency.com"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setErrors((p) => ({ ...p, email: undefined })); }}
                  autoFocus={mode === "signin"}
                />
              </div>
              {errors.email && <span className="field-error">{errors.email}</span>}
            </div>

            <div className="login-field">
              <label>Password</label>
              <div className={`input-wrapper ${errors.password ? "input-error" : ""}`}>
                <Lock size={18} className="input-icon" />
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder={mode === "signup" ? "At least 6 characters" : "Enter password"}
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setErrors((p) => ({ ...p, password: undefined })); }}
                />
                <button
                  type="button"
                  className="input-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.password && <span className="field-error">{errors.password}</span>}
            </div>

            {mode === "signin" && (
              <div className="forgot-row">
                <button
                  type="button"
                  className="forgot-link"
                  onClick={handleForgotPassword}
                  disabled={loading}
                >
                  Forgot password?
                </button>
              </div>
            )}

            <button type="submit" className="btn-primary btn-full login-cta" disabled={loading}>
              {loading ? <Loader2 size={20} className="spin" /> : null}
              {loading
                ? (mode === "signin" ? "Signing in..." : "Creating account...")
                : (mode === "signin" ? "Sign In" : "Create Free Account")}
            </button>

            {mode === "signup" && (
              <p className="login-terms">
                By creating an account, you agree to our{" "}
                <a href="https://nexgenweblab.com/terms" target="_blank" rel="noreferrer">Terms</a>{" "}
                and <a href="https://nexgenweblab.com/privacy" target="_blank" rel="noreferrer">Privacy Policy</a>.
              </p>
            )}

            {hasGoogleOAuth && (
              <div className="login-divider">
                <span>or continue with</span>
              </div>
            )}

            {hasGoogleOAuth && (
              <button
                type="button"
                className="btn-google"
                onClick={signInWithGoogle}
                disabled={loading}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                Google
              </button>
            )}

            <p className="login-switch">
              {mode === "signin" ? "Don't have an account?" : "Already have an account?"}{" "}
              <button type="button" className="switch-link" onClick={toggleMode}>
                {mode === "signin" ? "Create one" : "Sign in"}
              </button>
            </p>

            <p className="login-social-proof">Join 2,400+ SEO professionals</p>
          </form>
        </div>
      </div>
    </div>
  );
}
