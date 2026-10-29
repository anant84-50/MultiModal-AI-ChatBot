import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Volume2, VolumeX, User, Bot, AlertTriangle, HeartHandshake, Copy, Check, Sparkles, Download } from 'lucide-react';
import SourceList from './SourceList';
import DocumentPreview from './DocumentPreview';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const meta = message.metadata_json || {};
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [copied, setCopied] = useState(false);
  const audioUrl = meta.audio_url || null;

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSpeak = () => {
    // If speaking, stop immediately
    if (isSpeaking) {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
      setIsSpeaking(false);
      return;
    }

    // Instant browser speech synthesis (0ms latency, clear natural audio)
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel(); // stop any prior speech
      const cleanText = message.content.replace(/[*#_`~>]/g, '').slice(0, 500);
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = 1.0;
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
    } else if (audioUrl) {
      const audio = new Audio(audioUrl);
      setIsSpeaking(true);
      audio.onended = () => setIsSpeaking(false);
      audio.play();
    }
  };

  return (
    <div className={`message-row ${isUser ? 'user-row' : 'assistant-row'}`}>
      <div className="message-avatar">
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      <div className="message-bubble-body">
        {/* Special status banners */}
        {meta.is_crisis_alert && (
          <div className="crisis-banner">
            <AlertTriangle size={16} />
            <span>Crisis & Safety Assistance</span>
          </div>
        )}

        {meta.is_emotional_support && !meta.is_crisis_alert && (
          <div className="emotion-banner">
            <HeartHandshake size={15} />
            <span>Emotional Support Mode</span>
          </div>
        )}

        {/* Attached files preview (Images, Camera photos, Documents) */}
        {meta.attached_files && meta.attached_files.length > 0 && (
          <div className="message-attachments-preview">
            {meta.attached_files.map((file, idx) => {
              if (file.file_type === 'image' && file.file_url) {
                return (
                  <div key={idx} className="msg-thumb-container">
                    <img
                      src={file.file_url}
                      alt={file.filename || 'Attached image'}
                      className="message-image-thumb"
                      onClick={() => window.open(file.file_url, '_blank')}
                      title="Click to view full image"
                    />
                  </div>
                );
              }
              return (
                <div key={idx} className="message-file-chip">
                  <span className="file-chip-icon">
                    {file.file_type === 'pdf' ? '📕' : file.file_type === 'docx' ? '📘' : file.file_type === 'audio' ? '🎵' : '📄'}
                  </span>
                  <span className="file-chip-name">{file.filename}</span>
                </div>
              );
            })}
          </div>
        )}

        {/* Message content */}
        <div className="message-text">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {/* AI Generated Image Card */}
        {meta.generated_image && meta.generated_image.file_url && (
          <div className="generated-image-card">
            <div className="generated-image-header">
              <span className="gen-badge">
                <Sparkles size={13} className="text-amber-400" />
                <span>AI Generated Artwork</span>
              </span>
              <a
                href={meta.generated_image.file_url}
                download={meta.generated_image.filename || 'ai_generated_image.jpg'}
                className="gen-image-download-btn"
                title="Download full resolution image"
              >
                <Download size={13} />
                <span>Download</span>
              </a>
            </div>
            <div className="generated-image-frame">
              <img
                src={meta.generated_image.file_url}
                alt={meta.generated_image.prompt || 'AI Generated Image'}
                className="generated-image-img"
                onClick={() => window.open(meta.generated_image.file_url, '_blank')}
                title="Click to view full image in new tab"
              />
            </div>
            {meta.generated_image.prompt && (
              <div className="generated-image-caption">
                <span className="caption-label">Prompt:</span>
                <span className="caption-text">{meta.generated_image.prompt}</span>
              </div>
            )}
          </div>
        )}

        {/* Downloadable generated document */}
        {meta.generated_document && (
          <DocumentPreview documentMeta={meta.generated_document} />
        )}

        {/* Sources citations */}
        {meta.sources && meta.sources.length > 0 && (
          <SourceList sources={meta.sources} />
        )}

        {/* Footer actions */}
        <div className="message-bubble-footer">
          <span className="message-time">
            {message.created_at ? new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
          </span>

          <div className="message-actions-bar">
            {/* 1-Click Copy */}
            <button
              type="button"
              onClick={handleCopy}
              className="bubble-action-btn"
              title="Copy response text"
            >
              {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>

            {/* Instant Text-To-Speech */}
            {!isUser && (
              <button
                type="button"
                onClick={handleSpeak}
                className={`bubble-action-btn ${isSpeaking ? 'playing' : ''}`}
                title={isSpeaking ? 'Stop speaking' : 'Listen to response'}
              >
                {isSpeaking ? <VolumeX size={14} /> : <Volume2 size={14} />}
                <span>{isSpeaking ? 'Stop' : 'Listen'}</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
