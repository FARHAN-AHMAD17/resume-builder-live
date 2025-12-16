// src/components/LandingPage.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();

  // Handle navigation for all buttons
  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <div className="landing-body">
      {/* ===== Navbar with Logo + Title ===== */}
      <header className="landing-header">
        <div className="navbar-brand">
          <img src="/SRB.jpg" alt="Smart Resume Builder Logo" className="logo" />
          <span className="brand-name">
            Smart Resume Builder & <span className="highlight">Optimizer</span>
          </span>
        </div>

        {/* ===== Navigation Links ===== */}
        <div className="nav-links">
          <button onClick={() => handleNavigation('/auth')} className="nav-btn">
            Login
          </button>
          <button onClick={() => handleNavigation('/auth')} className="signup-btn">
            Sign Up
          </button>
        </div>
      </header>

      {/* ===== Hero Section ===== */}
      <main className="hero-section">
        <div className="hero-content">
          <h1>
            Get More Interviews with <br /> <strong>AI Resume Builder & Optimizer</strong>
          </h1>
          <p>
            Our AI analyzes job descriptions and optimizes your resume according to the job description,
            matches keywords, and impresses recruiters.
          </p>

          <div className="hero-buttons">
            <button onClick={() => handleNavigation('/auth')} className="try-free-btn">
              Try for Free <i className="fas fa-arrow-right"></i>
            </button>
            <button onClick={() => handleNavigation('/auth')} className="log-in-btn">
              Log In
            </button>
          </div>

          <small>No credit card required • Start optimizing your resume today</small>
        </div>

        <div className="hero-image-container">
          <img src="/OIP.webp" alt="Person working on laptop" />
          <div className="overlay-card">
            <div className="icon-circle">
              <i className="fas fa-check-circle"></i>
            </div>
            <div className="text-content">
              <p>Resume Optimized</p>
              <small>+32 score improvement</small>
            </div>
            <div className="score">94</div>
          </div>
        </div>
      </main>

      
    </div>
  );
};

export default LandingPage;
