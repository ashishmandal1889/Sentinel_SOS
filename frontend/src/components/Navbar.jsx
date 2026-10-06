import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Shield, Menu, X } from "lucide-react";
import "./Navbar.css";

function Navbar() {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(
    localStorage.getItem("isLoggedIn") === "true"
  );
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const updateAuth = () => {
      setIsLoggedIn(localStorage.getItem("isLoggedIn") === "true");
    };

    window.addEventListener("auth-change", updateAuth);
    window.addEventListener("storage", updateAuth);

    return () => {
      window.removeEventListener("auth-change", updateAuth);
      window.removeEventListener("storage", updateAuth);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("token");

    setIsLoggedIn(false);
    setMenuOpen(false);

    window.dispatchEvent(new Event("auth-change"));
    navigate("/login");
  };

  const closeMenu = () => setMenuOpen(false);

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-logo" onClick={closeMenu}>
        <Shield size={28} />
        <span>SentinelSOS</span>
      </Link>

      <button
        className="menu-toggle"
        onClick={() => setMenuOpen(!menuOpen)}
        aria-label={menuOpen ? "Close menu" : "Open menu"}
      >
        {menuOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      <div className={`navbar-links ${menuOpen ? "active" : ""}`}>
        <a href="/#home" onClick={closeMenu}>Home</a>
        <a href="/#features" onClick={closeMenu}>Features</a>
        <a href="/#about" onClick={closeMenu}>About</a>
        <a href="/#contact" onClick={closeMenu}>Contact</a>

        {isLoggedIn ? (
          <button className="navbar-cta" onClick={handleLogout}>
            Log Out
          </button>
        ) : (
          <Link
            to="/login"
            className="navbar-cta"
            onClick={closeMenu}
          >
            Sign In
          </Link>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
