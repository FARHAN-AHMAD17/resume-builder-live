// ==============================================================================
// INSTRUCTIONS: This is the complete code for frontend/src/App.js
// ==============================================================================

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import AuthPage from './components/AuthPage';
import Dashboard from './components/Dashboard';
import LandingPage from './components/LandingPage';
import OAuthCallback from './components/OAuthCallback';
import Sidebar from './components/Sidebar';
import TemplatesPage from './components/TemplatesPage';
import { getStatus, logout } from './api';
import './App.css';
import AboutPage from './components/AboutPage';

function App() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const [pdfData, setPdfData] = useState(null);

  useEffect(() => {
    const checkUserStatus = async () => {
      try {
        const res = await getStatus();
        if (res.data.logged_in) setUser(res.data.username);
        else setUser(null);
      } catch {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    checkUserStatus();
  }, []);

  const handleLogin = (username) => setUser(username);
  const handleLogout = async () => { 
    await logout(); 
    setUser(null); 
  };

  if (isLoading) return <div>Loading Application...</div>;

  return (
    <Router>
      {user ? (
        <div className="app-container">
          <Sidebar />
          <main className="main-content-area">
            <Navbar user={user} onLogout={handleLogout} />
            <Routes>
              <Route path="/dashboard" element={<Dashboard setPdfData={setPdfData} />} />
              <Route path="/templates" element={<TemplatesPage pdfData={pdfData} />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="*" element={<Navigate to="/dashboard" />} />
            </Routes>
          </main>
        </div>
      ) : (
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth" element={<AuthPage onLogin={handleLogin} />} />
          <Route path="/oauth-callback" element={<OAuthCallback onLogin={handleLogin} />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      )}
    </Router>
  );
}

export default App;