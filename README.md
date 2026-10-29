# 🌟 Multimodal AI Chatbot MVP (3D Royal Golden Edition)

An advanced, beginner-friendly, and multimodal AI Chatbot built with **FastAPI**, **React (Vite)**, and **Google Gemini 3.1 Flash Lite**.

---

## ✨ Features & Capabilities

1. **Multimodal Vision & Camera**:
   - Live Webcam Snapshot Capture directly from browser.
   - Image upload analysis (JPEG, PNG, WEBP).
   - High-speed multimodal visual reasoning via Gemini Flash.

2. **AI Voice & Speech (STT & TTS)**:
   - Live Voice Recording with animated soundwave equalizers and timer.
   - Dual-engine speech-to-text (Browser Web Speech API + Gemini AI audio transcription).
   - Instant Text-To-Speech (TTS) listening with 1-click audio playback.

3. **AI Image Generation (Text-to-Image)**:
   - Generate 1024×1024 high-definition realistic images directly from chat.
   - Bilingual support: Accepts English (*"generate an image of a sports car"*) and Hindi/Hinglish (*"ek pyare golden puppy ki photo banao"*).
   - Gemini prompt enrichment (8K, cinematic lighting, photorealism).
   - 3D Golden image showcase card with 1-click Download button.

4. **Document RAG & Non-Destructive Editing**:
   - Ingest PDF, Word DOCX, TXT files for grounded Question & Answering.
   - Document modification that creates new timestamped files without overwriting originals.
   - Generate new Word DOCX, PDF, and Markdown documents on demand.

5. **Live Web Search**:
   - Integrated DuckDuckGo web search intent detection and automatic citation synthesis.

6. **ChatGPT-Style Unified Tool Deck**:
   - All tools consolidated into a single round **Plus `(+)`** menu inside the input bar:
     - 📸 **Take Photo** (Live Camera Capture)
     - 🎨 **Generate Image** (AI Text-to-Image)
     - 🖼️ **Photos & Images** (Upload from device)
     - 📎 **Upload Document** (RAG Knowledge Base)
     - 🌐 **Web Search** (Toggle DuckDuckGo search)
     - 📄 **Create Document** (Generate new files)

7. **3D Interactive Golden UI**:
   - Obsidian Onyx background with Royal Gold accents.
   - Interactive 3D particle constellation canvas with mouse parallax.
   - Conversation history management (Single delete & Clear All History).
   - Profile & Theme Settings modals.

---

## 🚀 Quick Start (1-Click on Windows)

Simply double-click **`run_chatbot.bat`** in the root folder!
It will:
1. Automatically set up Python virtual environment and install backend dependencies.
2. Automatically install frontend npm dependencies.
3. Start the FastAPI backend on port 8000 and Vite frontend on port 5173.
4. Open the chatbot in your default browser at `http://127.0.0.1:5173`.

---

## 🛠️ Manual Installation & Running

### 1. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create or verify `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-3.1-flash-lite
EMBEDDING_MODEL=gemini-embedding-001
ENVIRONMENT=development
PORT=8000
```

Start backend:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Backend will be live at: `http://127.0.0.1:8000` (API docs at `http://127.0.0.1:8000/docs`).

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will be live at: `http://127.0.0.1:5173`.

---

## 📁 Project Architecture

```
multimodal-ai-chatbot/
├── backend/
│   ├── app/
│   │   ├── api/                # Chat, Document, Audio endpoints
│   │   ├── database/           # SQLite / PostgreSQL models & session
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # LLM, RAG, Search, Audio, ImageGen services
│   │   └── utils/              # Security and helpers
│   ├── generated/              # Generated documents and audio TTS files
│   ├── uploads/                # Uploaded and generated image files
│   ├── requirements.txt        # Backend dependencies
│   └── .env                    # Preconfigured API keys & settings
├── frontend/
│   ├── src/
│   │   ├── components/         # ChatInput, MessageBubble, Background3D, Modals
│   │   ├── pages/              # ChatPage
│   │   ├── services/           # API client axios bindings
│   │   └── index.css           # 3D Royal Golden Theme styles
│   ├── package.json
│   └── vite.config.js
├── run_chatbot.bat             # 1-Click launcher
├── start_backend.bat           # Backend launcher
├── start_frontend.bat          # Frontend launcher
└── README.md
```

---

## 🔒 Security & Privacy
- Zero cloud telemetry.
- Uploads and generated files are stored locally in `backend/uploads/`.
- Non-destructive document editing guarantees original files are preserved.
