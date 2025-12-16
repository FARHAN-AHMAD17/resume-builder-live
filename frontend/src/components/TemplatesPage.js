// src/components/TemplatesPage.js
import React, { useState } from 'react';
import { generatePdf } from '../api';
import './TemplatesPage.css';

const TemplatesPage = ({ pdfData }) => {
  const [loadingTemplate, setLoadingTemplate] = useState(null);

  const templates = [
    // ✅ CORRECTED LINE: The id now matches the backend filename 'template1.py'
    { id: 'template1', name: 'Template 01', imageUrl: '/templates/template1.png' },
    
    // ✅ CORRECTED LINE: The id now matches the backend filename 'template2.py' (for the future)
   
    { id: 'template3', name: 'Template 02', imageUrl: '/templates/template3.png' },
    // ✅ CORRECTED LINE: The id now matches the backend filename 'template2.py' (for the future)
    { id: 'template4', name: 'Template 03', imageUrl: '/templates/template4.png' },
  ];

  const handleDownload = async (templateId) => {
    if (!pdfData) {
      alert("Please optimize a resume on the Optimizer page first!");
      return;
    }

    setLoadingTemplate(templateId);
    try {
      const formData = new FormData();
      formData.append('resumeFile', pdfData.resumeFile);
      formData.append('jobDescription', pdfData.jobDescription);
      formData.append('aiSuggestions', pdfData.suggestions.join('\n'));
      formData.append('templateId', templateId); // This will now send 'template1'

      const response = await generatePdf(formData);
      const file = new Blob([response.data], { type: 'application/pdf' });
      const fileURL = URL.createObjectURL(file);
      const link = document.createElement('a');
      link.href = fileURL;
      link.setAttribute('download', `Optimized_Resume_${templateId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      URL.revokeObjectURL(fileURL);
    } catch (error) {
      alert("Failed to generate PDF. Please try again.");
    } finally {
      setLoadingTemplate(null);
    }
  };

  return (
    <div className="templates-container">
      <h2 className="templates-title">Choose Your Resume Template</h2>
      <p className="templates-subtitle">Click on a template to download your optimized resume in that format.</p>
      <div className="templates-gallery">
        {templates.map((template) => (
          <div 
            key={template.id} 
            className={`template-card ${loadingTemplate === template.id ? 'loading' : ''}`}
            onClick={() => !loadingTemplate && handleDownload(template.id)}
          >
            <img src={template.imageUrl} alt={template.name} />
            <h3>
              {loadingTemplate === template.id ? 'Generating...' : template.name}
            </h3>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TemplatesPage;