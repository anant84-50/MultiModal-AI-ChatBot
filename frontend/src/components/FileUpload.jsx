import React, { useRef } from 'react';
import { Paperclip, Image as ImageIcon, Camera, Globe, FileText, X, Loader2, Sparkles } from 'lucide-react';

export default function FileUpload({
  attachments,
  onAttach,
  onRemove,
  isUploading,
  onOpenCamera,
  forceWebSearch,
  onToggleWebSearch,
  onOpenDocModal,
}) {
  const fileInputRef = useRef(null);
  const imageInputRef = useRef(null);

  const handleFileChange = (e, fileCategory = null) => {
    const file = e.target.files?.[0];
    if (file) {
      onAttach(file, fileCategory);
    }
    e.target.value = '';
  };

  const getFileBadge = (type) => {
    if (type === 'image') return { emoji: '🖼️', label: 'Image' };
    if (type === 'pdf') return { emoji: '📕', label: 'PDF Doc' };
    if (type === 'docx') return { emoji: '📘', label: 'Word Doc' };
    if (type === 'audio') return { emoji: '🎵', label: 'Audio' };
    return { emoji: '📄', label: 'Document' };
  };

  return (
    <div className="file-upload-wrapper">
      {/* Hidden file inputs */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={(e) => handleFileChange(e)}
        accept=".pdf,.docx,.doc,.txt,.md,.mp3,.wav,.ogg"
        style={{ display: 'none' }}
      />
      <input
        type="file"
        ref={imageInputRef}
        onChange={(e) => handleFileChange(e, 'image')}
        accept="image/*"
        style={{ display: 'none' }}
      />

      {/* 3D Unified Golden Tool Deck */}
      <div className="unified-tool-deck">
        {/* Live Camera Button */}
        <button
          type="button"
          onClick={onOpenCamera}
          disabled={isUploading}
          className="deck-tool-btn deck-camera-btn"
          title="Take a live photo with webcam"
        >
          <Camera size={14} />
          <span>Camera</span>
        </button>

        {/* Gallery Image Button */}
        <button
          type="button"
          onClick={() => imageInputRef.current?.click()}
          disabled={isUploading}
          className="deck-tool-btn"
          title="Attach photo or image"
        >
          <ImageIcon size={14} />
          <span>Photo</span>
        </button>

        {/* Document Button */}
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="deck-tool-btn"
          title="Attach PDF, Word, or Text document for RAG"
        >
          <Paperclip size={14} />
          <span>Document</span>
        </button>

        {/* Web Search Toggle */}
        <button
          type="button"
          onClick={onToggleWebSearch}
          className={`deck-tool-btn ${forceWebSearch ? 'deck-web-active' : ''}`}
          title="Toggle live DuckDuckGo web search"
        >
          <Globe size={14} />
          <span>Web Search: {forceWebSearch ? 'ON' : 'Auto'}</span>
        </button>

        {/* Generate Doc Template */}
        {onOpenDocModal && (
          <button
            type="button"
            onClick={onOpenDocModal}
            className="deck-tool-btn"
            title="Create a new formatted document"
          >
            <FileText size={14} />
            <span>Generate Doc</span>
          </button>
        )}
      </div>

      {/* Uploading progress indicator */}
      {isUploading && (
        <div className="uploading-indicator gold-uploading">
          <Loader2 size={15} className="spin-icon text-gold" />
          <span>Ingesting & indexing file into 3D RAG memory...</span>
        </div>
      )}

      {/* Attached chips tray */}
      {attachments.length > 0 && (
        <div className="attachments-tray">
          {attachments.map((att) => {
            const badge = getFileBadge(att.file_type);
            return (
              <div key={att.id} className="attachment-chip gold-chip">
                <span className="attachment-icon">{badge.emoji}</span>
                <span className="attachment-name" title={att.filename}>
                  {att.filename}
                </span>
                <span className="attachment-type-tag">{badge.label}</span>
                <button
                  type="button"
                  onClick={() => onRemove(att.id)}
                  className="attachment-remove-btn"
                  title="Remove attachment"
                >
                  <X size={13} />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
