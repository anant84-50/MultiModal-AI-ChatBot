import React, { useState } from 'react';
import { BookOpen, Globe, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';

export default function SourceList({ sources }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!sources || sources.length === 0) return null;

  const docSources = sources.filter((s) => s.type === 'document');
  const webSources = sources.filter((s) => s.type === 'web');

  return (
    <div className="source-list-container">
      <button 
        type="button" 
        onClick={() => setIsOpen(!isOpen)} 
        className="source-list-toggle"
      >
        <span className="source-toggle-title">
          <BookOpen size={15} />
          <span>{sources.length} {sources.length === 1 ? 'Source' : 'Sources'} Cited</span>
          {docSources.length > 0 && <span className="source-badge doc-badge">{docSources.length} Doc</span>}
          {webSources.length > 0 && <span className="source-badge web-badge">{webSources.length} Web</span>}
        </span>
        {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {isOpen && (
        <div className="source-list-content">
          {docSources.length > 0 && (
            <div className="source-section">
              <div className="source-section-header">
                <BookOpen size={14} />
                <span>Document References (RAG)</span>
              </div>
              <div className="source-items-grid">
                {docSources.map((s, idx) => (
                  <div key={idx} className="source-item-card">
                    <div className="source-item-title">
                      📄 {s.title} {s.page ? `(Page ${s.page})` : ''}
                    </div>
                    <div className="source-item-snippet">"{s.snippet}"</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {webSources.length > 0 && (
            <div className="source-section">
              <div className="source-section-header">
                <Globe size={14} />
                <span>Web Search Citations</span>
              </div>
              <div className="source-items-grid">
                {webSources.map((s, idx) => (
                  <div key={idx} className="source-item-card">
                    <div className="source-item-title">
                      <a href={s.url} target="_blank" rel="noopener noreferrer" className="source-link">
                        🌐 {s.title} <ExternalLink size={12} />
                      </a>
                    </div>
                    <div className="source-item-snippet">{s.snippet}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
