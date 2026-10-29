import React, { useState, useRef, useEffect } from 'react';
import {
  Send, Plus, Globe, Loader2, Sparkles, FileText, Image as ImageIcon,
  Camera, Paperclip, X, Check
} from 'lucide-react';
import VoiceInput from './VoiceInput';
import CameraCapture from './CameraCapture';

export default function ChatInput({
  onSendMessage,
  onAttachFile,
  attachments,
  onRemoveAttachment,
  isUploading,
  isLoading,
  onOpenDocModal,
}) {
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [forceWebSearch, setForceWebSearch] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [isPlusMenuOpen, setIsPlusMenuOpen] = useState(false);

  const textareaRef = useRef(null);
  const menuRef = useRef(null);
  const docInputRef = useRef(null);
  const imgInputRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      if (!inputText) {
        textareaRef.current.style.height = '32px';
      } else {
        textareaRef.current.style.height = '32px';
        const scrollH = textareaRef.current.scrollHeight;
        textareaRef.current.style.height = `${Math.min(Math.max(scrollH, 32), 140)}px`;
      }
    }
  }, [inputText]);

  // Click outside to close plus menu
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setIsPlusMenuOpen(false);
      }
    };
    if (isPlusMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isPlusMenuOpen]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    const trimmed = inputText.trim();
    if ((!trimmed && attachments.length === 0) || isLoading) return;

    onSendMessage({
      message: trimmed || 'Please analyze the attached file.',
      enable_web_search: forceWebSearch ? true : null,
      speak_response: false,
    });

    setInputText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = '32px';
    }
    setIsPlusMenuOpen(false);
  };

  const handleVoiceTranscript = (text) => {
    if (!text || !text.trim()) return;
    setInputText((prev) => (prev.trim() ? `${prev.trim()} ${text.trim()}` : text.trim()));
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 50);
  };

  const handleFileChange = (e, fileCategory = null) => {
    const file = e.target.files?.[0];
    if (file) {
      onAttachFile(file, fileCategory);
    }
    e.target.value = '';
    setIsPlusMenuOpen(false);
  };

  // Drag and drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      onAttachFile(files[0]);
    }
  };

  const getFileBadge = (type) => {
    if (type === 'image') return { emoji: '🖼️', label: 'Image' };
    if (type === 'pdf') return { emoji: '📕', label: 'PDF' };
    if (type === 'docx') return { emoji: '📘', label: 'Word' };
    if (type === 'audio') return { emoji: '🎵', label: 'Audio' };
    return { emoji: '📄', label: 'Doc' };
  };

  return (
    <div
      className={`chat-input-container ${isDragOver ? 'drag-over-active' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Hidden file inputs */}
      <input
        type="file"
        ref={docInputRef}
        onChange={(e) => handleFileChange(e)}
        accept=".pdf,.docx,.doc,.txt,.md,.mp3,.wav,.ogg"
        style={{ display: 'none' }}
      />
      <input
        type="file"
        ref={imgInputRef}
        onChange={(e) => handleFileChange(e, 'image')}
        accept="image/*"
        style={{ display: 'none' }}
      />

      {/* Live Webcam Modal */}
      <CameraCapture
        isOpen={isCameraOpen}
        onClose={() => setIsCameraOpen(false)}
        onCapture={(file) => onAttachFile(file, 'image')}
      />

      {/* ChatGPT-Style Modern Unified Input Card */}
      <div className="chatgpt-input-card">
        {/* Active badges tray (Attached files, Web search status) */}
        {(attachments.length > 0 || forceWebSearch || isUploading) && (
          <div className="chat-card-top-tray">
            {forceWebSearch && (
              <span className="active-pill-badge web-badge-active">
                <Globe size={12} />
                <span>Web Search ON</span>
                <button
                  type="button"
                  onClick={() => setForceWebSearch(false)}
                  className="pill-close-btn"
                  title="Turn off web search"
                >
                  <X size={11} />
                </button>
              </span>
            )}

            {isUploading && (
              <span className="active-pill-badge uploading-badge">
                <Loader2 size={12} className="spin-icon" />
                <span>Indexing attachment...</span>
              </span>
            )}

            {attachments.map((att) => {
              const badge = getFileBadge(att.file_type);
              return (
                <span key={att.id} className="active-pill-badge file-badge">
                  <span>{badge.emoji}</span>
                  <span className="file-pill-name" title={att.filename}>
                    {att.filename}
                  </span>
                  <button
                    type="button"
                    onClick={() => onRemoveAttachment(att.id)}
                    className="pill-close-btn"
                    title="Remove attachment"
                  >
                    <X size={11} />
                  </button>
                </span>
              );
            })}
          </div>
        )}

        {/* The main input row */}
        <div className="chat-input-row">
          {/* ChatGPT Plus (+) Button and Popover Menu */}
          <div className="plus-menu-anchor" ref={menuRef}>
            <button
              type="button"
              onClick={() => setIsPlusMenuOpen(!isPlusMenuOpen)}
              className={`chatgpt-plus-btn ${isPlusMenuOpen ? 'active' : ''}`}
              title="Add tools and attachments"
            >
              <Plus size={19} className={`plus-icon ${isPlusMenuOpen ? 'rotated' : ''}`} />
            </button>

            {/* ChatGPT-Style Floating Tool Menu */}
            {isPlusMenuOpen && (
              <div className="chatgpt-tools-popover">
                <div className="popover-heading">Add to prompt</div>

                <button
                  type="button"
                  onClick={() => {
                    setIsPlusMenuOpen(false);
                    setIsCameraOpen(true);
                  }}
                  className="popover-item"
                >
                  <div className="popover-icon-box gold-icon-box">
                    <Camera size={16} />
                  </div>
                  <div className="popover-item-text">
                    <span className="popover-title">Take Photo</span>
                    <span className="popover-desc">Use webcam for live vision</span>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setIsPlusMenuOpen(false);
                    setInputText('Generate an image of ');
                    setTimeout(() => textareaRef.current?.focus(), 50);
                  }}
                  className="popover-item"
                >
                  <div className="popover-icon-box gold-icon-box">
                    <Sparkles size={16} />
                  </div>
                  <div className="popover-item-text">
                    <span className="popover-title">Generate Image</span>
                    <span className="popover-desc">AI Text-to-Image creation</span>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setIsPlusMenuOpen(false);
                    imgInputRef.current?.click();
                  }}
                  className="popover-item"
                >
                  <div className="popover-icon-box gold-icon-box">
                    <ImageIcon size={16} />
                  </div>
                  <div className="popover-item-text">
                    <span className="popover-title">Photos & Images</span>
                    <span className="popover-desc">Upload from device</span>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setIsPlusMenuOpen(false);
                    docInputRef.current?.click();
                  }}
                  className="popover-item"
                >
                  <div className="popover-icon-box gold-icon-box">
                    <Paperclip size={16} />
                  </div>
                  <div className="popover-item-text">
                    <span className="popover-title">Upload Document</span>
                    <span className="popover-desc">PDF, Word DOCX, TXT for RAG</span>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setForceWebSearch(!forceWebSearch);
                    setIsPlusMenuOpen(false);
                  }}
                  className={`popover-item ${forceWebSearch ? 'selected-item' : ''}`}
                >
                  <div className="popover-icon-box gold-icon-box">
                    <Globe size={16} />
                  </div>
                  <div className="popover-item-text">
                    <span className="popover-title">
                      Web Search {forceWebSearch ? '(Active)' : '(Auto)'}
                    </span>
                    <span className="popover-desc">
                      {forceWebSearch ? 'Always query DuckDuckGo' : 'Search only when needed'}
                    </span>
                  </div>
                  {forceWebSearch && <Check size={16} className="text-emerald-400" />}
                </button>

                {onOpenDocModal && (
                  <button
                    type="button"
                    onClick={() => {
                      setIsPlusMenuOpen(false);
                      onOpenDocModal();
                    }}
                    className="popover-item"
                  >
                    <div className="popover-icon-box gold-icon-box">
                      <FileText size={16} />
                    </div>
                    <div className="popover-item-text">
                      <span className="popover-title">Create Document</span>
                      <span className="popover-desc">Generate new doc from template</span>
                    </div>
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Text Input Area */}
          <textarea
            ref={textareaRef}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything..."
            rows={1}
            disabled={isLoading}
            className="chat-textarea"
          />

          {/* Voice & Send Controls */}
          <div className="chat-input-controls">
            <VoiceInput
              onTranscript={handleVoiceTranscript}
              isRecording={isRecording}
              setIsRecording={setIsRecording}
            />

            <button
              type="button"
              onClick={handleSend}
              disabled={(!inputText.trim() && attachments.length === 0) || isLoading}
              className="send-message-btn"
              title="Send Message"
            >
              {isLoading ? <Loader2 size={17} className="spin-icon" /> : <Send size={17} />}
            </button>
          </div>
        </div>
      </div>

      {isDragOver && (
        <div className="chat-input-hints">
          <span className="drag-drop-text">📁 Drop file to attach</span>
        </div>
      )}
    </div>
  );
}
