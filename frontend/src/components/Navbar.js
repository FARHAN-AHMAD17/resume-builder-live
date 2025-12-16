// ==============================================================================
// INSTRUCTIONS: Replace the entire content of Navbar.js
// This version removes the "Home (Optimizer)" breadcrumb.
// ==============================================================================

import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Navbar.css';

const Navbar = ({ user, onLogout }) => {
  const navigate = useNavigate();

  const handleLogoutClick = async () => {
    await onLogout();
    navigate('/auth');
  };

  return (
    <header className="top-navbar">
      {/* The breadcrumb div has been removed from here */}

      <div className="user-info">
        <span>Welcome, <span className="username">{user}</span></span>
        <button onClick={handleLogoutClick} className="logout-button">
          Logout
        </button>
      </div>
    </header>
  );
};

export default Navbar;