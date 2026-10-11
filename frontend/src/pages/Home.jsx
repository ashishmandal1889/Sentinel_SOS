
import { useEffect, useState } from "react";
import {
  Shield,
  MapPin,
  Users,
  Network,
  WifiOff,
  Lock,
  Siren,
  Heart,
  ArrowRight,
  Play,
  Menu,
  X,
  CheckCircle,
  Image as ImageIcon,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import "./Home.css";
import heroImage from "../assets/images/hero.jpg";

// Features
const features = [
  {
    icon: Siren,
    title: "Multiple SOS Triggers",
    description: "Manual, voice, gesture, motion, multimodal and more.",
    color: "red",
  },
  {
    icon: MapPin,
    title: "Live Location & Route Safety",
    description: "Real-time tracking, geofencing, route monitoring and more.",
    color: "blue",
  },
  {
    icon: Shield,
    title: "Smart AI & Risk Detection",
    description: "Detect unusual behaviour, route deviation and high-risk situations.",
    color: "green",
  },
  {
    icon: Users,
    title: "Trusted Network",
    description: "Connect with family, friends, responders and verified volunteers.",
    color: "purple",
  },
  {
    icon: ImageIcon,
    title: "Evidence & Incident Management",
    description: "Audio, video, sensor data, timelines and secure reports.",
    color: "orange",
  },
  {
    icon: Network,
    title: "Route Intelligence",
    description: "Explore routes and find safer paths to your destination.",
    color: "cyan",
  },
  {
    icon: WifiOff,
    title: "Offline Support",
    description: "Designed with offline support and local fallback capabilities.",
    color: "pink",
  },
  {
    icon: Lock,
    title: "Security & Privacy",
    description: "Privacy-focused access and secure data handling.",
    color: "lightblue",
  },
];

// How it works
const steps = [
  {
    number: "01",
    title: "Trigger an Alert",
    description: "Activate an emergency alert when you need assistance.",
    color: "red",
  },
  {
    number: "02",
    title: "Assess the Situation",
    description: "Available location and safety information can help assess the situation.",
    color: "blue",
  },
  {
    number: "03",
    title: "Notify Trusted Contacts",
    description: "Connect with your trusted contacts through the alert system.",
    color: "green",
  },
  {
    number: "04",
    title: "Coordinate Help",
    description: "Use available safety tools to coordinate assistance.",
    color: "purple",
  },
];

export default function Home() {
  const navigate = useNavigate();

  const [menuOpen, setMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(
    localStorage.getItem("isLoggedIn") === "true"
  );

  // Keep navbar in sync with login status
  useEffect(() => {
    const updateAuth = () => {
      setIsLoggedIn(
        localStorage.getItem("isLoggedIn") === "true"
      );
    };

    window.addEventListener("auth-change", updateAuth);
    window.addEventListener("storage", updateAuth);

    return () => {
      window.removeEventListener("auth-change", updateAuth);
      window.removeEventListener("storage", updateAuth);
    };
  }, []);

  const closeMenu = () => setMenuOpen(false);

  // Logout
  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("token");

    setIsLoggedIn(false);
    closeMenu();

    window.dispatchEvent(new Event("auth-change"));
    navigate("/login");
  };

  return (
    <main className="sentinel-home">

      {/* HERO SECTION */}
      <section className="hero-section" id="home">
        {/* NAVBAR */}
        <header className="site-header">
          <div className="header-inner">

            <div className="header-brand-wrap">
              <Link
                to="/"
                className="brand"
                onClick={closeMenu}
              >
                <span className="brand-icon">
                  <Shield size={31} strokeWidth={2.8} />
                  <span className="brand-dot" />
                </span>

                <span>
                  SENTINEL<span className="brand-red">SOS</span>
                </span>
              </Link>
            </div>

            {/* Mobile menu button */}
            <button
              className="mobile-menu-button"
              onClick={() => setMenuOpen(!menuOpen)}
              aria-label={menuOpen ? "Close menu" : "Open menu"}
              aria-expanded={menuOpen}
              aria-controls="main-navigation"
            >
              {menuOpen ? <X size={25} /> : <Menu size={25} />}
            </button>

            {/* Navigation links (Centered in top middle) */}
            <nav
              id="main-navigation"
              className={`main-nav ${menuOpen ? "nav-open" : ""}`}
            >
              <a
                className="nav-link active"
                href="#home"
                onClick={closeMenu}
              >
                Home
              </a>

              <a
                className="nav-link"
                href="#features"
                onClick={closeMenu}
              >
                Features
              </a>

              <a
                className="nav-link"
                href="#about"
                onClick={closeMenu}
              >
                About
              </a>

              <a
                className="nav-link"
                href="#contact"
                onClick={closeMenu}
              >
                Contact
              </a>

              <div className="mobile-only-action">
                {isLoggedIn ? (
                  <button
                    type="button"
                    className="header-download"
                    onClick={handleLogout}
                  >
                    Log Out
                  </button>
                ) : (
                  <Link
                    to="/login"
                    className="header-download"
                    onClick={closeMenu}
                  >
                    Sign In
                  </Link>
                )}
              </div>
            </nav>

            {/* Header Right Action Button */}
            <div className="header-right">
              {isLoggedIn ? (
                <button
                  type="button"
                  className="header-download"
                  onClick={handleLogout}
                >
                  Log Out
                </button>
              ) : (
                <Link
                  to="/login"
                  className="header-download"
                  onClick={closeMenu}
                >
                  Sign In
                </Link>
              )}
            </div>

          </div>
        </header>

        {/* HERO CONTENT */}
        <div className="hero-content page-container">
          <div className="hero-copy">

            <p className="hero-eyebrow">
              YOUR PERSONAL SAFETY COMPANION
            </p>

            <h1>
              Your Safety.
              <br />
              Our Priority.
              <br />
              <span>Always.</span>
            </h1>

            <p className="hero-description">
              SentinelSOS is an AI-assisted emergency safety
              platform designed to help you stay connected,
              inform your loved ones, and coordinate assistance
              when it matters most.
            </p>

            <div className="hero-actions">

              <Link
                to={isLoggedIn ? "/dashboard" : "/login"}
                className="primary-button"
              >
                {isLoggedIn ? "Go to Dashboard" : "Get Started"}
                <ArrowRight size={19} />
              </Link>

              <a
                href="#how-it-works"
                className="video-button"
              >
                <span className="play-icon">
                  <Play size={16} fill="currentColor" />
                </span>
                How It Works
              </a>

            </div>
          </div>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section
        className="features-section section-padding"
        id="features"
      >
        <div className="section-heading">

          <h2>
            Complete Protection. Built for Real Life.
          </h2>

          <p>
            Explore the safety features planned for SentinelSOS,
            combining emergency coordination, location awareness,
            and privacy-focused technology.
          </p>

        </div>

        <div className="features-grid page-container">

          {features.map((feature) => {
            const Icon = feature.icon;

            return (
              <article
                className="feature-card"
                key={feature.title}
              >
                <div className={`feature-icon ${feature.color}`}>
                  <Icon size={27} strokeWidth={2.3} />
                </div>

                <h3>{feature.title}</h3>

                <p>{feature.description}</p>
              </article>
            );
          })}

        </div>
      </section>

      {/* HOW IT WORKS SECTION */}
      <section
        className="how-section section-padding"
        id="how-it-works"
      >
        <div className="steps-container page-container">

          <div className="section-heading">

            <p className="hero-eyebrow">
              SIMPLE. SMART. CONNECTED.
            </p>

            <h2>How SentinelSOS Works</h2>

            <p>
              A simple overview of the emergency assistance
              workflow designed for SentinelSOS.
            </p>

          </div>

          <div className="steps-grid">

            {steps.map((step) => (
              <article
                className="step-item"
                key={step.number}
              >
                <div className={`step-number ${step.color}`}>
                  {step.number}
                </div>

                <h3>{step.title}</h3>

                <p>{step.description}</p>
              </article>
            ))}

          </div>
        </div>
      </section>

      {/* CLOSING BANNER */}
      <section
        className="closing-banner"
        id="about"
      >
        <div className="closing-inner page-container">

          <div className="closing-copy">

            <h2>
              Because Safety
              <br />
              Shouldn’t Be a Guess.
            </h2>

            <p>
              SentinelSOS — AI-assisted emergency coordination
              for a safer tomorrow.
            </p>

            <div className="store-buttons">

              <Link
                to={isLoggedIn ? "/dashboard" : "/login"}
                className="store-button"
              >
                <span className="store-symbol">▶</span>

                <span>
                  <small>GET STARTED</small>
                  <strong>SentinelSOS</strong>
                </span>
              </Link>

            </div>
          </div>

          <div className="closing-benefits">

            <div>
              <Shield size={25} />
              Smarter Technology
            </div>

            <div>
              <Users size={25} />
              Stronger Communities
            </div>

            <div>
              <Heart size={25} />
              Safer Journeys
            </div>

          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer
        className="site-footer"
        id="contact"
      >
        <div className="footer-inner page-container">

          <Link
            to="/"
            className="footer-brand"
          >
            <Shield size={27} />

            <span>
              SENTINEL<span>SOS</span>
            </span>
          </Link>

          <p className="footer-tagline">
            Safe People <span>|</span> Safe Places{" "}
            <span>|</span> Smarter Tomorrow
          </p>

          <p className="copyright">
            © {new Date().getFullYear()} SentinelSOS.
            All rights reserved.
          </p>

        </div>
      </footer>

    </main>
  );
}
