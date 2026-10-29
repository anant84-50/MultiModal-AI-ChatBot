import axios from 'axios';

const API_BASE = '/api';

export const api = {
  // Health
  checkHealth: async () => {
    const res = await axios.get(`${API_BASE}/health`);
    return res.data;
  },

  // Conversations
  getConversations: async () => {
    const res = await axios.get(`${API_BASE}/conversations`);
    return res.data;
  },

  getConversation: async (id) => {
    const res = await axios.get(`${API_BASE}/conversations/${id}`);
    return res.data;
  },

  deleteConversation: async (id) => {
    const res = await axios.delete(`${API_BASE}/conversations/${id}`);
    return res.data;
  },

  clearAllConversations: async () => {
    const res = await axios.delete(`${API_BASE}/conversations`);
    return res.data;
  },

  // Chat
  sendMessage: async (chatPayload) => {
    const res = await axios.post(`${API_BASE}/chat`, chatPayload);
    return res.data;
  },

  // File Upload (Multimodal: images, PDF, DOCX, audio)
  uploadFile: async (file, conversationId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (conversationId) {
      formData.append('conversation_id', conversationId);
    }
    const res = await axios.post(`${API_BASE}/documents/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  // Document Creation & Editing
  createDocument: async (title, format, content) => {
    const res = await axios.post(`${API_BASE}/documents/create`, {
      title,
      format,
      prompt_or_content: content,
    });
    return res.data;
  },

  editDocument: async (documentId, instructions) => {
    const res = await axios.post(`${API_BASE}/documents/edit`, {
      document_id: documentId,
      instructions,
    });
    return res.data;
  },

  // Audio TTS
  speakText: async (text) => {
    const res = await axios.post(`${API_BASE}/audio/speak`, { text });
    return res.data;
  },

  // Audio Speech-to-Text via Gemini Flash
  transcribeAudio: async (audioBlob) => {
    const formData = new FormData();
    const ext = audioBlob.type && audioBlob.type.includes('mp4') ? 'mp4' : 'webm';
    formData.append('file', audioBlob, `mic_recording.${ext}`);
    const res = await axios.post(`${API_BASE}/chat/transcribe-audio`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
};
