// src/components/AuthPage.js
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import './AuthPage.css';
import './LandingPage.css';
import { register as apiRegister, login as apiLogin } from '../api';

const AuthPage = ({ onLogin }) => {
  const navigate = useNavigate();
  const [isFlipped, setIsFlipped] = useState(false);
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [registerData, setRegisterData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab === 'register') {
      setIsFlipped(true);
    }
  }, [searchParams]);

  const handleFlip = () => {
    setError('');
    setIsFlipped(!isFlipped);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      const res = await apiLogin(loginData.username, loginData.password);
      if (res.status === 200) {
        onLogin(res.data.username);
        navigate('/dashboard');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Login failed. Please try again.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    if (!registerData.username || !registerData.password) {
      setError('Please fill out all fields.');
      setIsLoading(false);
      return;
    }
    try {
      const res = await apiRegister(registerData.username, registerData.password);
      if (res.status === 201) {
        alert('Registration Successful! Please log in.');
        setRegisterData({ username: '', password: '' });
        setIsFlipped(false);
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Registration failed. Please try again.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // ✅ STEP 1: ADD THIS NAVIGATION FUNCTION
  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <>
      <header className="landing-header">
        {/* ✅ STEP 2: MAKE THE BRAND CLICKABLE */}
        <div className="navbar-brand" onClick={() => handleNavigation('/')} style={{ cursor: 'pointer' }}>
          <img src="/SRB.jpg" alt="Smart Resume Builder Logo" className="logo" />
          <span className="brand-name">
            Smart Resume Builder & <span className="highlight">Optimizer</span>
          </span>
        </div>
        <div className="nav-links">
          <button onClick={() => handleNavigation('/auth')} className="nav-btn">
            Login
          </button>
          <button onClick={() => handleNavigation('/auth?tab=register')} className="signup-btn">
            Sign Up
          </button>
        </div>
      </header>

      <div className="auth-container">
        <div className={`auth-card ${isFlipped ? 'flipped' : ''}`}>
          {/* ... rest of the component is unchanged ... */}
          <div className="auth-face front">
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
              <input
                type="text"
                placeholder="Username"
                value={loginData.username}
                onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
                required
                disabled={isLoading}
              />
              <input
                type="password"
                placeholder="Password"
                value={loginData.password}
                onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                required
                disabled={isLoading}
              />
              <button type="submit" className="auth-btn" disabled={isLoading}>
                {isLoading ? 'Logging In...' : 'Login'}
              </button>
              {error && <p className="error">{error}</p>}
            </form>
            <p className="switch-text">
              Don’t have an account? <span onClick={handleFlip}>Register now!</span>
            </p>
          </div>
          <div className="auth-face back">
            <h2>Register</h2>
            <form onSubmit={handleRegister}>
              <input
                type="text"
                placeholder="Username"
                value={registerData.username}
                onChange={(e) => setRegisterData({ ...registerData, username: e.target.value })}
                required
                disabled={isLoading}
              />
              <input
                type="password"
                placeholder="Password"
                value={registerData.password}
                onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                required
                disabled={isLoading}
              />
              <button type="submit" className="auth-btn" disabled={isLoading}>
                {isLoading ? 'Registering...' : 'Register'}
              </button>
              {error && <p className="error">{error}</p>}
            </form>
            <p className="switch-text">
              Already have an account? <span onClick={handleFlip}>Login here!</span>
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default AuthPage;