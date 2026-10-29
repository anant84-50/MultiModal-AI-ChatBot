import React from 'react';
import { Download, FileText, CheckCircle } from 'lucide-react';

export default function DocumentPreview({ documentMeta }) {
  if (!documentMeta) return null;

  const { filename, download_url, summary } = documentMeta;

  return (
    <div className="doc-preview-card">
      <div className="doc-preview-header">
        <div className="doc-preview-icon">
          <FileText size={22} />
        </div>
        <div className="doc-preview-info">
          <div className="doc-preview-title">{filename}</div>
          <div className="doc-preview-subtitle">
            <CheckCircle size={13} className="text-emerald-500" />
            <span>Updated document ready for download</span>
          </div>
        </div>
        <a 
          href={download_url} 
          download={filename} 
          className="doc-download-btn"
          title="Download Document"
        >
          <Download size={16} />
          <span>Download</span>
        </a>
      </div>
      {summary && (
        <div className="doc-preview-summary">
          {summary}
        </div>
      )}
    </div>
  );
}
