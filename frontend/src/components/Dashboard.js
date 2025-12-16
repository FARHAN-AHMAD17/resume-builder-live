// src/components/Dashboard.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import "./Dashboard.css";
import { FaFileUpload, FaBrain } from "react-icons/fa";
import { optimizeResume } from "../api";

// Accept setPdfData as a prop
const Dashboard = ({ setPdfData }) => {
  const navigate = useNavigate(); // Initialize navigate
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [matchScore, setMatchScore] = useState(null);
  const [optimizedScore, setOptimizedScore] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState("");

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setResumeFile(file);
      setFileName(file.name);
    }
  };

  const handleAnalyzeOptimize = async () => {
    if (!resumeFile || !jobDescription) {
      alert("Please upload a resume and enter a job description.");
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append("resumeFile", resumeFile);
    formData.append("jobDescription", jobDescription);
    try {
      const response = await optimizeResume(formData);
      const data = response.data;
      setMatchScore(data.match_score);
      setOptimizedScore(data.optimized_score);
      setShowResults(true);

      // Save all necessary data for the PDF to the shared state in App.js
      setPdfData({
        resumeFile,
        jobDescription,
        suggestions: data.optimized_resume.split("\n").filter((s) => s.trim() !== "")
      });

    } catch (error) {
      alert(`Optimization failed: ${error.response?.data?.error || "An unexpected error occurred."}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-container">
      <h2 className="dashboard-title">AI-Powered Resume Optimizer</h2>
      <div className="optimizer-main-grid">
        <div className="input-column">
          <div className="card input-card">
            <h3>Upload Your Current Resume (PDF/DOCX)</h3>
            <div className="upload-area">
              <FaFileUpload className="upload-icon" />
              <p>Accepted formats: .pdf, .docx</p>
              <label htmlFor="file-upload" className="browse-button">Browse Files</label>
              <input id="file-upload" type="file" accept=".pdf,.docx" onChange={handleFileChange} />
              {fileName && <p className="file-name-display">{fileName}</p>}
            </div>
          </div>
          <div className="card input-card">
            <h3>Paste Job Description Here</h3>
            <textarea
              placeholder="Paste the job description you are targeting..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            ></textarea>
          </div>
        </div>
        <div className="results-column">
          <div className="card status-card">
            <h3>Optimization Status</h3>
            <div className="status-circle">
              <svg viewBox="0 0 36 36" className="circular-chart">
                <path className="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                <path className="circle" strokeDasharray={`${optimizedScore ? optimizedScore.replace("%", "") : 0}, 100`} d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              </svg>
              <div className="status-text">
                <span>{optimizedScore || "0%"}</span>
                <small>Before: {matchScore || "0%"}</small>
              </div>
            </div>
          </div>
          
          {/* NEW: This section appears after optimization */}
          {showResults && (
            <div className="card cta-card">
              <h3>Your Resume is Optimized!</h3>
              <p>Now, choose a professional template to download your new resume.</p>
              <button onClick={() => navigate('/templates')} className="select-template-button">
                Select a Template
              </button>
            </div>
          )}
        </div>
      </div>
      <div className="analyze-button-container">
        <button onClick={handleAnalyzeOptimize} className="analyze-button" disabled={loading}>
          <FaBrain /> {loading ? "Optimizing..." : "Analyze & Optimize"}
        </button>
      </div>
    </div>
  );
};

export default Dashboard;