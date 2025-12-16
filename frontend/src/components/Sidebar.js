// src/components/Sidebar.js
import React from 'react';
import { NavLink } from 'react-router-dom';
// ✅ ADD FaInfoCircle TO THE IMPORT
import { FaPenAlt, FaFileAlt, FaInfoCircle } from 'react-icons/fa';
import './Sidebar.css';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">SR Builder</h1>
      </div>
      <nav className="sidebar-nav">
        <ul>
          <li>
            <NavLink to="/dashboard" className="nav-link">
              <FaPenAlt />
              <span>Optimizer</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/templates" className="nav-link">
              <FaFileAlt />
              <span>Templates</span>
            </NavLink>
          </li>
          {/* ✅ ADD THE NEW "ABOUT" LINK */}
          <li>
            <NavLink to="/about" className="nav-link">
              <FaInfoCircle />
              <span>About</span>
            </NavLink>
          </li>
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;