import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Shield,
  Eye,
  EyeOff,
  Mail,
  Lock,
  ArrowRight,
  Cpu,
  Users,
} from "lucide-react";
import "./Auth.css";
import heroImage from "../assets/images/hero.jpg";

const GoogleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
  </svg>
);

const AppleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.32c.62-.75 1.04-1.8 0.92-2.85-.9.04-2 .61-2.64 1.35-.57.66-.97 1.74-.84 2.76 1.01.08 2.04-.51 2.56-1.26z"/>
  </svg>
);

function Login() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    identifier: "",
    password: "",
    rememberMe: true,
  });

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (!formData.identifier || !formData.password) {
      setError("Please fill in all required fields.");
      return;
    }

    localStorage.setItem("isLoggedIn", "true");
    window.dispatchEvent(new Event("auth-change"));
    navigate("/");
  };

  return (
    <div className="auth-page">
      <div className="auth-split-card">
        {/* LEFT PANEL */}
        <div
          className="auth-left-panel"
          style={{
            backgroundImage: `linear-gradient(
              180deg,
              rgba(10, 20, 35, 0.75) 0%,
              rgba(10, 20, 35, 0.88) 100%
            ), url(${heroImage})`,
          }}
        >
          <div className="left-panel-content">
            <Link to="/" className="auth-brand-logo">
              <span className="brand-icon-box">
                <Shield size={24} strokeWidth={2.8} />
              </span>
              <span className="brand-logo-text">
                SENTINEL<span className="brand-red">SOS</span>
              </span>
            </Link>

            <div className="left-hero-text">
              <h1>
                Your Safety.
                <br />
                Our Priority.
                <br />
                <span className="brand-red">Always.</span>
              </h1>
              <p className="hero-subtext">
                Stay protected with AI-powered emergency assistance, real-time
                location tracking and smarter response.
              </p>
            </div>

            <div className="left-features-grid">
              <div className="left-feature-item">
                <div className="feature-circle-icon">
                  <Shield size={18} />
                </div>
                <span>Real-time Location</span>
              </div>
              <div className="left-feature-item">
                <div className="feature-circle-icon">
                  <Cpu size={18} />
                </div>
                <span>AI-Powered Detection</span>
              </div>
              <div className="left-feature-item">
                <div className="feature-circle-icon">
                  <Users size={18} />
                </div>
                <span>Trusted Responders</span>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT FORM CARD */}
        <div className="auth-right-card">
          <div className="auth-card-inner">
            <div className="auth-form-header">
              <h2>Welcome Back</h2>
              <p>Sign in to your SentinelSOS account.</p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="identifier">
                  <Mail size={15} /> Email Address / Phone Number
                </label>
                <div className="input-field-box">
                  <Mail size={18} className="field-icon" />
                  <input
                    id="identifier"
                    type="text"
                    name="identifier"
                    placeholder="Enter your email or phone number"
                    value={formData.identifier}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="password">
                  <Lock size={15} /> Password
                </label>
                <div className="input-field-box">
                  <Lock size={18} className="field-icon" />
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    name="password"
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                  />
                  <button
                    type="button"
                    className="password-toggle-btn"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <div className="form-options-row">
                <label className="checkbox-container">
                  <input
                    type="checkbox"
                    name="rememberMe"
                    checked={formData.rememberMe}
                    onChange={handleChange}
                  />
                  <span className="checkbox-custom"></span>
                  <span className="checkbox-text">Remember me</span>
                </label>

                <a href="#forgot" className="forgot-password-link">
                  Forgot password?
                </a>
              </div>

              {error && <p className="auth-error-msg">{error}</p>}

              <button type="submit" className="auth-primary-btn">
                Log In <ArrowRight size={18} />
              </button>
            </form>

            <div className="auth-divider">
              <span>Or continue with</span>
            </div>

            <div className="social-buttons-stack">
              <button type="button" className="social-btn">
                <GoogleIcon /> Continue with Google
              </button>
              <button type="button" className="social-btn">
                <AppleIcon /> Continue with Apple
              </button>
            </div>

            <p className="auth-switch-text">
              Don't have an account?{" "}
              <Link to="/register" className="auth-switch-link">
                Sign Up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
