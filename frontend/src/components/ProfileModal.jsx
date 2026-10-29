import React, { useState } from 'react';
import { User, Crown, X, Check, ShieldCheck, Cpu, HardDrive, Sparkles } from 'lucide-react';

export default function ProfileModal({ isOpen, onClose, conversationCount = 0 }) {
  const [displayName, setDisplayName] = useState(
    localStorage.getItem('mm_display_name') || 'Rahul (User)'
  );
  const [savedSuccess, setSavedSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSave = (e) => {
    e.preventDefault();
    localStorage.setItem('mm_display_name', displayName.trim());
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2000);
  };

  return (
    <div className="modal-overlay modal-3d-overlay" onClick={onClose}>
      <div className="modal-card modal-3d-card gold-modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header gold-modal-header">
          <div className="modal-title gold-title">
            <div className="avatar-gold-ring">
              <Crown size={18} className="text-gold" />
            </div>
            <span>User Profile & Credentials</span>
          </div>
          <button type="button" onClick={onClose} className="modal-close-btn" title="Close">
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSave} className="profile-modal-body">
          {/* User Hero Banner */}
          <div className="profile-hero-badge">
            <div className="profile-avatar-3d">
              <User size={36} />
              <div className="crown-badge">
                <Crown size={14} />
              </div>
            </div>
            <div className="profile-hero-info">
              <h3 className="profile-user-title">{displayName}</h3>
              <span className="profile-tier-tag">
                <Sparkles size={12} />
                <span>Multimodal Pro MVP</span>
              </span>
            </div>
          </div>

          {/* Form edit display name */}
          <div className="form-group">
            <label className="gold-label">Display Name</label>
            <div className="input-with-button">
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Enter your name"
                className="gold-input"
                required
              />
              <button type="submit" className="gold-save-btn">
                {savedSuccess ? <Check size={16} /> : 'Save'}
              </button>
            </div>
            {savedSuccess && <span className="save-indicator-text">✓ Name saved successfully!</span>}
          </div>

          {/* System & AI Specs */}
          <div className="profile-stats-grid">
            <div className="profile-stat-item">
              <div className="stat-icon-wrapper">
                <Cpu size={16} className="text-gold" />
              </div>
              <div className="stat-info">
                <span className="stat-label">AI Engine</span>
                <span className="stat-value">Gemini 3.1 Flash Lite</span>
              </div>
            </div>

            <div className="profile-stat-item">
              <div className="stat-icon-wrapper">
                <HardDrive size={16} className="text-gold" />
              </div>
              <div className="stat-info">
                <span className="stat-label">Conversations</span>
                <span className="stat-value">{conversationCount} Active</span>
              </div>
            </div>

            <div className="profile-stat-item">
              <div className="stat-icon-wrapper">
                <ShieldCheck size={16} className="text-gold" />
              </div>
              <div className="stat-info">
                <span className="stat-label">Guardrails</span>
                <span className="stat-value">Crisis & Safety 988</span>
              </div>
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="modal-gold-dismiss-btn">
              Done
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
