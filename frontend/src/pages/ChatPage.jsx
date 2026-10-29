import React, { useState, useEffect } from 'react';
import {
  Plus, MessageSquare, Trash2, Menu, X, Sparkles, FilePlus, AlertCircle,
  Settings, User, Crown, ShieldAlert, Download
} from 'lucide-react';
import ChatWindow from '../components/ChatWindow';
import ChatInput from '../components/ChatInput';
import Background3D from '../components/Background3D';
import ProfileModal from '../components/ProfileModal';
import SettingsModal from '../components/SettingsModal';
import { api } from '../services/api';

export default function ChatPage() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [attachments, setAttachments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [errorBanner, setErrorBanner] = useState(null);
  const [showDocModal, setShowDocModal] = useState(false);
  const [newDocTitle, setNewDocTitle] = useState('');
  const [newDocFormat, setNewDocFormat] = useState('docx');
  const [newDocContent, setNewDocContent] = useState('');

  // 3D & Modals states
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showClearConfirmModal, setShowClearConfirmModal] = useState(false);
  const [goldTheme, setGoldTheme] = useState(
    localStorage.getItem('mm_gold_theme') || 'royal-gold'
  );

  // Initial load: fetch conversations
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const data = await api.getConversations();
      setConversations(data);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  const handleSelectConversation = async (id) => {
    try {
      setIsLoading(true);
      setErrorBanner(null);
      const data = await api.getConversation(id);
      setActiveConversationId(data.id);
      setMessages(data.messages || []);
      setAttachments([]);
    } catch (err) {
      setErrorBanner('Failed to load conversation history.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
    setAttachments([]);
    setErrorBanner(null);
  };

  const handleDeleteConversation = async (e, id) => {
    e.stopPropagation();
    try {
      await api.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) {
        handleNewChat();
      }
    } catch (err) {
      setErrorBanner('Failed to delete conversation.');
    }
  };

  const handleClearAllHistory = async () => {
    try {
      setIsLoading(true);
      await api.clearAllConversations();
      setConversations([]);
      handleNewChat();
      setShowClearConfirmModal(false);
    } catch (err) {
      setErrorBanner('Failed to clear conversation history.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAttachFile = async (file, category) => {
    try {
      setIsUploading(true);
      setErrorBanner(null);
      const uploadedDoc = await api.uploadFile(file, activeConversationId);
      setAttachments((prev) => [...prev, uploadedDoc]);
    } catch (err) {
      const msg = err.response?.data?.detail || 'File upload failed. Check format and size.';
      setErrorBanner(msg);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveAttachment = (id) => {
    setAttachments((prev) => prev.filter((a) => a.id !== id));
  };

  const handleSendMessage = async ({ message, enable_web_search, speak_response }) => {
    try {
      setIsLoading(true);
      setErrorBanner(null);

      // Determine input type
      let input_type = 'text';
      if (attachments.some((a) => a.file_type === 'image')) input_type = 'image';
      else if (attachments.some((a) => a.file_type === 'audio')) input_type = 'audio';
      else if (attachments.length > 0) input_type = 'document';

      // Temporary optimistic user message
      const tempUserMsg = {
        id: `temp_${Date.now()}`,
        role: 'user',
        content: message,
        created_at: new Date().toISOString(),
        metadata_json: {
          attachments: attachments.map((a) => a.id),
          attached_files: attachments.map((a) => ({
            id: a.id,
            filename: a.filename,
            file_type: a.file_type,
            file_url: a.file_url || (a.file_path ? `/uploads/${a.file_path.split(/[\\/]/).pop()}` : null),
          })),
        },
      };
      setMessages((prev) => [...prev, tempUserMsg]);

      const payload = {
        conversation_id: activeConversationId,
        message,
        input_type,
        attachment_ids: attachments.map((a) => a.id),
        enable_web_search,
        speak_response,
      };

      const res = await api.sendMessage(payload);

      // Set active conversation ID and update messages
      setActiveConversationId(res.conversation_id);
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== tempUserMsg.id);
        return [...filtered, res.user_message, res.assistant_message];
      });

      // Clear draft attachments
      setAttachments([]);

      // Refresh conversations list in background
      loadConversations();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to send message. Please try again.';
      setErrorBanner(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateDocumentSubmit = async (e) => {
    e.preventDefault();
    if (!newDocTitle.trim() || !newDocContent.trim()) return;

    try {
      setIsLoading(true);
      const res = await api.createDocument(newDocTitle, newDocFormat, newDocContent);
      setShowDocModal(false);
      setNewDocTitle('');
      setNewDocContent('');

      // Add a virtual assistant message with the download card
      const docMsg = {
        id: `doc_${Date.now()}`,
        role: 'assistant',
        content: `I have generated your **${newDocTitle}** document in \`.${newDocFormat}\` format. You can download it below.`,
        created_at: new Date().toISOString(),
        metadata_json: {
          generated_document: {
            filename: res.filename,
            download_url: res.download_url,
            summary: `Created ${res.filename} based on your template.`,
          },
        },
      };
      setMessages((prev) => [...prev, docMsg]);
    } catch (err) {
      setErrorBanner('Failed to generate document.');
    } finally {
      setIsLoading(false);
    }
  };

  const storedUserName = localStorage.getItem('mm_display_name') || 'Rahul (User)';

  return (
    <div className={`app-layout theme-${goldTheme}`}>
      {/* 3D Floating Interactive Canvas Background */}
      <Background3D />

      {/* Sidebar with 3D Glass Layer */}
      <aside className={`sidebar sidebar-3d ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="app-brand" onClick={() => setShowProfileModal(true)} style={{ cursor: 'pointer' }}>
            <div className="brand-icon gold-brand-icon">
              <Crown size={20} className="text-gold" />
            </div>
            <div className="brand-text-group">
              <span className="brand-name gold-gradient-text">Multimodal 3D</span>
              <span className="brand-badge-vip">PRO MVP</span>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setSidebarOpen(false)}
            className="sidebar-close-btn lg-hidden"
          >
            <X size={18} />
          </button>
        </div>

        {/* 3D Golden Action Buttons */}
        <button type="button" onClick={handleNewChat} className="new-chat-btn gold-btn-3d">
          <Plus size={18} />
          <span>New Chat</span>
        </button>

        <button 
          type="button" 
          onClick={() => setShowDocModal(true)} 
          className="create-doc-menu-btn gold-doc-btn-3d"
        >
          <FilePlus size={16} />
          <span>Generate New Document</span>
        </button>

        {/* Conversation History with Clear All Option */}
        <div className="sidebar-history-section">
          <div className="history-heading-row">
            <span className="history-heading">Conversations ({conversations.length})</span>
            {conversations.length > 0 && (
              <button
                type="button"
                onClick={() => setShowClearConfirmModal(true)}
                className="clear-all-link-btn"
                title="Clear all chat history"
              >
                <Trash2 size={13} />
                <span>Clear All</span>
              </button>
            )}
          </div>

          <div className="history-list">
            {conversations.length === 0 ? (
              <div className="history-empty">No conversations yet.</div>
            ) : (
              conversations.map((c) => (
                <div
                  key={c.id}
                  onClick={() => handleSelectConversation(c.id)}
                  className={`history-item history-item-3d ${activeConversationId === c.id ? 'active' : ''}`}
                >
                  <MessageSquare size={15} className="history-icon" />
                  <span className="history-title" title={c.title}>
                    {c.title}
                  </span>
                  <button
                    type="button"
                    onClick={(e) => handleDeleteConversation(e, c.id)}
                    className="history-delete-btn"
                    title="Delete conversation"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Sidebar Footer: Profile & Settings Dock */}
        <div className="sidebar-user-footer">
          <div 
            className="user-profile-card-3d" 
            onClick={() => setShowProfileModal(true)}
            title="Open Profile"
          >
            <div className="user-avatar-gold-3d">
              <User size={16} />
            </div>
            <div className="user-info-text">
              <span className="user-name-text">{storedUserName}</span>
              <span className="user-tier-badge">👑 Royal Gold</span>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setShowSettingsModal(true)}
            className="sidebar-settings-icon-btn"
            title="Open Application Settings"
          >
            <Settings size={18} />
          </button>
        </div>
      </aside>

      {/* Main Chat Area with 3D Depth */}
      <main className="main-content main-content-3d">
        {/* Top Navbar */}
        <header className="chat-header chat-header-3d">
          <div className="header-left">
            <button
              type="button"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="toggle-sidebar-btn"
              title="Toggle sidebar"
            >
              <Menu size={20} />
            </button>
            <div className="header-brand-title">
              <h1 className="header-title gold-gradient-text">Multimodal 3D Assistant</h1>
              <span className="header-model-badge gold-model-badge">Gemini 3.1 Flash Lite</span>
            </div>
          </div>

          <div className="header-right">
            <span className="gold-status-indicator" title="Gemini 3.1 Flash Lite Vision & RAG Engine Ready">
              <span className="gold-status-dot"></span>
              <span>Online</span>
            </span>

            <a
              href="http://127.0.0.1:8000/api/download-zip"
              download="multimodal-ai-chatbot.zip"
              className="download-zip-top-btn"
              title="Download Complete Chatbot ZIP (6.4 MB)"
            >
              <Download size={14} />
              <span>Download ZIP</span>
            </a>

            <button
              type="button"
              onClick={() => setShowSettingsModal(true)}
              className="header-icon-circle-btn"
              title="Settings"
            >
              <Settings size={16} />
            </button>

            <button
              type="button"
              onClick={() => setShowProfileModal(true)}
              className="header-icon-circle-btn"
              title="Profile"
            >
              <User size={16} />
            </button>
          </div>
        </header>

        {/* Error notification banner */}
        {errorBanner && (
          <div className="error-alert-banner">
            <AlertCircle size={16} />
            <span>{errorBanner}</span>
            <button type="button" onClick={() => setErrorBanner(null)} className="error-close-btn">
              <X size={14} />
            </button>
          </div>
        )}

        {/* Chat Stream */}
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          onPromptSelect={(prompt) => handleSendMessage({ message: prompt })}
        />

        {/* Input Bar with Unified 3D Tool Deck */}
        <ChatInput
          onSendMessage={handleSendMessage}
          onAttachFile={handleAttachFile}
          attachments={attachments}
          onRemoveAttachment={handleRemoveAttachment}
          isUploading={isUploading}
          isLoading={isLoading}
          onOpenDocModal={() => setShowDocModal(true)}
        />
      </main>

      {/* Profile Modal */}
      <ProfileModal
        isOpen={showProfileModal}
        onClose={() => setShowProfileModal(false)}
        conversationCount={conversations.length}
      />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={showSettingsModal}
        onClose={() => setShowSettingsModal(false)}
        onClearHistory={handleClearAllHistory}
        theme={goldTheme}
        setTheme={setGoldTheme}
      />

      {/* Clear All History Confirmation Modal */}
      {showClearConfirmModal && (
        <div className="modal-overlay modal-3d-overlay" onClick={() => setShowClearConfirmModal(false)}>
          <div className="modal-card modal-3d-card gold-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header gold-modal-header">
              <div className="modal-title danger-modal-title">
                <ShieldAlert size={20} className="text-rose-500" />
                <span>Clear All Chat History?</span>
              </div>
              <button
                type="button"
                onClick={() => setShowClearConfirmModal(false)}
                className="modal-close-btn"
              >
                <X size={18} />
              </button>
            </div>

            <div className="clear-confirm-body">
              <p className="confirm-warn-text">
                Are you sure you want to permanently clear all <strong>{conversations.length}</strong> conversations, indexed chunks, and uploads?
              </p>
              <p className="confirm-sub-text">
                This action cannot be undone. Your active conversation and history will be cleared.
              </p>
            </div>

            <div className="modal-actions">
              <button
                type="button"
                onClick={() => setShowClearConfirmModal(false)}
                className="modal-cancel-btn"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleClearAllHistory}
                className="delete-permanently-btn"
              >
                Yes, Clear All History
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Document Modal */}
      {showDocModal && (
        <div className="modal-overlay modal-3d-overlay" onClick={() => setShowDocModal(false)}>
          <div className="modal-card modal-3d-card gold-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header gold-modal-header">
              <div className="modal-title gold-title">
                <FilePlus size={18} className="text-gold" />
                <span>Create New Document</span>
              </div>
              <button
                type="button"
                onClick={() => setShowDocModal(false)}
                className="modal-close-btn"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateDocumentSubmit} className="modal-form">
              <div className="form-group">
                <label className="gold-label">Document Title</label>
                <input
                  type="text"
                  placeholder="e.g., Marketing Strategy 2026"
                  value={newDocTitle}
                  onChange={(e) => setNewDocTitle(e.target.value)}
                  className="gold-input"
                  required
                />
              </div>

              <div className="form-group">
                <label className="gold-label">Format</label>
                <select
                  value={newDocFormat}
                  onChange={(e) => setNewDocFormat(e.target.value)}
                  className="gold-input"
                >
                  <option value="docx">Microsoft Word (.docx)</option>
                  <option value="pdf">PDF Document (.pdf)</option>
                  <option value="md">Markdown (.md)</option>
                  <option value="txt">Plain Text (.txt)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="gold-label">Content / Structure</label>
                <textarea
                  placeholder="Enter initial content, outline, or markdown text..."
                  rows={6}
                  value={newDocContent}
                  onChange={(e) => setNewDocContent(e.target.value)}
                  className="gold-input"
                  required
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  onClick={() => setShowDocModal(false)}
                  className="modal-cancel-btn"
                >
                  Cancel
                </button>
                <button type="submit" className="modal-submit-btn gold-btn-3d">
                  Generate Document
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
