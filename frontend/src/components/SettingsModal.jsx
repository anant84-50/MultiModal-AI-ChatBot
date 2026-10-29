import React, { useState } from 'react';
import { Settings, Sliders, Volume2, Globe, Trash2, X, Check, AlertTriangle, Shield } from 'lucide-react';

export default function SettingsModal({
  isOpen,
  onClose,
  onClearHistory,
  theme,
  setTheme,
}) {
  const [speechRate, setSpeechRate] = useState(
    parseFloat(localStorage.getItem('mm_speech_rate') || '1.0')
  );
  const [defaultWebSearch, setDefaultWebSearch] = useState(
    localStorage.getItem('mm_default_search') || 'auto'
  );
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [savedNotif, setSavedNotif] = useState(false);

  if (!isOpen) return null;

  const handleSaveSettings = () => {
    localStorage.setItem('mm_speech_rate', speechRate.toString());
    localStorage.setItem('mm_default_search', defaultWebSearch);
    if (theme && setTheme) {
      localStorage.setItem('mm_gold_theme', theme);
    }
    setSavedNotif(true);
    setTimeout(() => {
      setSavedNotif(false);
      onClose();
    }, 1200);
  };

  const handleConfirmClear = () => {
    onClearHistory();
    setShowClearConfirm(false);
    onClose();
  };

  return (
    <div className="modal-overlay modal-3d-overlay" onClick={onClose}>
      <div className="modal-card modal-3d-card gold-modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header gold-modal-header">
          <div className="modal-title gold-title">
            <Settings size={20} className="text-gold spin-hover" />
            <span>Application Settings</span>
          </div>
          <button type="button" onClick={onClose} className="modal-close-btn" title="Close">
            <X size={18} />
          </button>
        </div>

        <div className="settings-modal-body">
          {/* Theme Palette */}
          <div className="settings-section">
            <label className="gold-label">
              <Sliders size={14} className="text-gold" />
              <span>3D Golden Theme Accent</span>
            </label>
            <div className="theme-options-grid">
              {[
                { id: 'royal-gold', name: 'Royal Gold', color: '#D4AF37' },
                { id: 'imperial-gold', name: 'Imperial Amber', color: '#F59E0B' },
                { id: 'champagne', name: 'Champagne Glow', color: '#FDE68A' },
              ].map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setTheme && setTheme(t.id)}
                  className={`theme-chip-btn ${theme === t.id ? 'active' : ''}`}
                >
                  <span className="color-swatch" style={{ backgroundColor: t.color }} />
                  <span>{t.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Voice Speech Speed */}
          <div className="settings-section">
            <div className="label-with-value">
              <label className="gold-label">
                <Volume2 size={14} className="text-gold" />
                <span>Audio Voice Speed</span>
              </label>
              <span className="setting-val-badge">{speechRate}x</span>
            </div>
            <input
              type="range"
              min="0.75"
              max="1.5"
              step="0.25"
              value={speechRate}
              onChange={(e) => setSpeechRate(parseFloat(e.target.value))}
              className="gold-range-slider"
            />
            <div className="range-labels">
              <span>0.75x (Slower)</span>
              <span>1.0x (Normal)</span>
              <span>1.5x (Faster)</span>
            </div>
          </div>

          {/* Web Search Default */}
          <div className="settings-section">
            <label className="gold-label">
              <Globe size={14} className="text-gold" />
              <span>Web Search Behavior</span>
            </label>
            <div className="segmented-control">
              <button
                type="button"
                onClick={() => setDefaultWebSearch('auto')}
                className={`segmented-btn ${defaultWebSearch === 'auto' ? 'active' : ''}`}
              >
                Auto (Smart)
              </button>
              <button
                type="button"
                onClick={() => setDefaultWebSearch('always')}
                className={`segmented-btn ${defaultWebSearch === 'always' ? 'active' : ''}`}
              >
                Always Search
              </button>
              <button
                type="button"
                onClick={() => setDefaultWebSearch('never')}
                className={`segmented-btn ${defaultWebSearch === 'never' ? 'active' : ''}`}
              >
                Off (Internal only)
              </button>
            </div>
          </div>

          {/* Danger Zone: Clear History */}
          <div className="settings-section danger-section">
            <label className="danger-label">
              <AlertTriangle size={15} />
              <span>Data & Conversation History</span>
            </label>

            {!showClearConfirm ? (
              <button
                type="button"
                onClick={() => setShowClearConfirm(true)}
                className="clear-all-danger-btn"
              >
                <Trash2 size={15} />
                <span>Clear All Chat History</span>
              </button>
            ) : (
              <div className="clear-confirm-box">
                <p className="confirm-warn-text">
                  ⚠️ This will permanently delete all conversation logs, indexed chunks, and uploads.
                </p>
                <div className="confirm-buttons-row">
                  <button
                    type="button"
                    onClick={() => setShowClearConfirm(false)}
                    className="cancel-confirm-btn"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleConfirmClear}
                    className="delete-permanently-btn"
                  >
                    Yes, Delete Everything
                  </button>
                </div>
              </div>
            )}
          </div>

          {savedNotif && (
            <div className="settings-saved-banner">
              <Check size={16} />
              <span>Preferences saved!</span>
            </div>
          )}

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="modal-cancel-btn">
              Cancel
            </button>
            <button type="button" onClick={handleSaveSettings} className="modal-submit-btn gold-btn-3d">
              Save Preferences
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
