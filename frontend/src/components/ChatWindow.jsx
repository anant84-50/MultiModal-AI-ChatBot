import React, { useEffect, useRef } from 'react';
import { Sparkles, Image, FileText, Globe, Heart, Edit3, Camera, Crown } from 'lucide-react';
import MessageBubble from './MessageBubble';

export default function ChatWindow({ messages, isLoading, onPromptSelect }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const starterPrompts = [
    {
      icon: <Camera size={20} className="text-gold" />,
      title: 'Live Camera Capture',
      prompt: 'Snap a live photo of a diagram or notes and ask me to explain it.',
    },
    {
      icon: <FileText size={20} className="text-gold" />,
      title: 'Document Q&A (RAG)',
      prompt: 'Summarize the main points of my uploaded document.',
    },
    {
      icon: <Image size={20} className="text-gold" />,
      title: 'Multimodal Vision',
      prompt: 'Explain what is shown in this diagram and list key observations.',
    },
    {
      icon: <Globe size={20} className="text-gold" />,
      title: 'Live Web Search',
      prompt: 'What are the latest developments in AI and technology this week?',
    },
    {
      icon: <Edit3 size={20} className="text-gold" />,
      title: 'Document Editing',
      prompt: 'Update my resume and add Python, React, and FastAPI to my technical skills.',
    },
    {
      icon: <Heart size={20} className="text-rose-400" />,
      title: 'Emotional Support',
      prompt: 'I have been feeling overwhelmed by work stress lately. Can we talk?',
    },
  ];

  return (
    <div className="chat-window-scroll">
      {messages.length === 0 ? (
        <div className="empty-chat-state">
          <div className="empty-hero">
            <div className="empty-sparkle-badge gold-sparkle-badge">
              <Crown size={16} className="text-gold" />
              <span>Multimodal 3D Intelligence</span>
            </div>
            <h2 className="empty-headline gold-gradient-text">How can I assist you today?</h2>
            <p className="empty-subtext">
              Upload documents with RAG, snap live camera photos, search the live web, or have an intelligent supportive conversation.
            </p>
          </div>

          <div className="starter-prompts-grid">
            {starterPrompts.map((item, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => onPromptSelect(item.prompt)}
                className="starter-card starter-card-3d"
              >
                <div className="starter-icon-gold">{item.icon}</div>
                <div className="starter-card-content">
                  <div className="starter-card-title">{item.title}</div>
                  <div className="starter-card-text">{item.prompt}</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="messages-list">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}

          {isLoading && (
            <div className="message-row assistant-row">
              <div className="message-avatar gold-avatar-3d">
                <Sparkles size={18} className="spin-slow text-gold" />
              </div>
              <div className="message-bubble-body thinking-bubble gold-thinking-bubble">
                <div className="typing-dots gold-typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="thinking-text">AI is processing 3D multimodal context...</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
}
