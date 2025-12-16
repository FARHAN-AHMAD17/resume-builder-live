// ==============================================================================
// INSTRUCTIONS: This is the complete, updated code for AboutPage.js
// The Contact & Feedback form has been removed.
// ==============================================================================

import React from 'react';
import './AboutPage.css';
// The 'sendFeedback' import and related 'useState' hooks are no longer needed.

const AboutPage = () => {
  return (
    <div className="about-container">
      <h2 className="about-title">About SR Builder</h2>
      
      <div className="about-card">
        <h3>Project Overview</h3>
        <p>
          The <strong>Smart Resume Builder & Optimizer (SR Builder)</strong> is an AI-driven platform designed to automate and enhance the creation of professional resumes. 
          By leveraging Large Language Models and real-time job market analysis, it helps users tailor their resumes to specific job descriptions, 
          optimize them for Applicant Tracking Systems (ATS), and increase their chances of securing an interview.
        </p>
      </div>

      <div className="about-card developer-info">
        <h3>Developer Contact</h3>
        <p>
          For any questions, suggestions, or feedback, please feel free to reach out directly.
        </p>
        <p><strong>Name:</strong> Farhan Ahmad</p>
        <p>
          <strong>Email:</strong> <a href="mailto:frhanahmd665@gmail.com">frhanahmd665@gmail.com</a>
        </p>
        <p>
          <strong>LinkedIn:</strong> <a href="https://www.linkedin.com/in/farhan-ahmad-0141a728b?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=ios_app" target="_blank" rel="noopener noreferrer">View Profile</a>
        </p>
      </div>
      
      {/* The entire "Contact & Feedback" card and form has been removed from here. */}
      
    </div>
  );
};

export default AboutPage;