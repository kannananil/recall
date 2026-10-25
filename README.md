# Recall - Your Local-First AI Reading Assistant

> Build something with open-source AI that rewards laziness

Recall is a local-first personal reading library that automatically organizes your saved articles using open-weight language models. Save interesting content with one click, and let AI generate summaries, categories, and tags—all processed locally on your machine.

## 🎯 Problem & Solution

**The Problem:** Bookmarks are where knowledge goes to die. We save interesting articles but rarely organize or rediscover them.

**The Solution:** One-click capture + local AI processing = automatic organization. No cloud, no API fees, complete privacy.

## 🏗️ Architecture

```
┌─────────────────┐
│  Browser Ext    │──┐
│  (Chrome)       │  │
└─────────────────┘  │
                     ├──► ┌──────────────────┐
┌─────────────────┐  │    │   FastAPI        │
│  Dashboard      │──┤    │   Backend        │
│  (React+Vite)   │  │    └────────┬─────────┘
└─────────────────┘  │             │
                     │     ┌───────▼──────┐
                     │     │   SQLite DB  │
                     │     └───────▲──────┘
                     │             │
                     └────►  ┌─────┴─────────┐
                            │  Worker        │
                            │  (Ollama+Gemma)│
                            └────────────────┘
```

## ✨ Features

- **One-Click Capture**: Browser extension saves articles instantly
- **Local AI Processing**: Ollama + Gemma 2B generates metadata locally
- **Automatic Organization**: Summaries, key points, categories, and tags
- **Smart Search**: Find articles by title, content, summary, or tags
- **Privacy-First**: All processing happens on your machine
- **No API Costs**: Run as much as you want, forever free

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (3.13 recommended)
- **Node.js 18+**
- **Ollama** ([install](https://ollama.ai/download))
- **Chrome/Chromium browser**

### Setup

1. **Clone and navigate to project:**
   ```bash
   git clone <repository-url>
   cd recall
   ```

2. **Install Ollama and pull the model:**
   ```bash
   # Install Ollama from https://ollama.ai/download
   # Then pull Gemma 2B
   ollama pull gemma:2b
   ```

3. **Set up the backend:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Set up the dashboard:**
   ```bash
   cd ../dashboard
   npm install
   ```

5. **Install the browser extension:**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (top right)
   - Click "Load unpacked"
   - Select the `extension` directory

### Run the Application

You'll need **three terminal windows**:

**Terminal 1 - Backend API:**
```bash
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload
# Runs on http://127.0.0.1:8000
```

**Terminal 2 - Background Worker:**
```bash
cd backend
source venv/bin/activate
python worker.py
```

**Terminal 3 - Dashboard:**
```bash
cd dashboard
npm run dev
# Runs on http://localhost:5173
```

## 📖 Usage

1. **Save an article**: Click the Recall extension icon while viewing any article
2. **Processing**: The worker picks up the job and calls Ollama to generate metadata
3. **View & Search**: Open the dashboard to browse, search, and rediscover your saved articles

## 🛠️ Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: SQLite with FTS5 for search
- **AI**: Ollama with Gemma 2B (open-weight model)
- **Dashboard**: React 18, TypeScript, Vite
- **Extension**: Chrome Manifest V3, TypeScript
- **Testing**: pytest, pytest-asyncio

## 🏆 Hacktoberfest 2026 - Week 3

This project was built for the [DEV Hacktoberfest Week 3 Challenge](https://dev.to/challenges/hacktoberfest-week3-2026-10-19): **Slow and Steady**

### Why Open-Source AI Matters for Recall

1. **Privacy**: Your reading habits, interests, and saved content never leave your machine
2. **Cost**: No API fees, no subscriptions—run unlimited processing for free
3. **Control**: Swap models, customize prompts, fine-tune for your specific interests
4. **Reliability**: Works offline, no rate limits, no service shutdowns
5. **Transparency**: See exactly how your content is being processed

## 📝 Project Status

**Current Phase**: Foundation & Core Implementation  
**Target Completion**: October 25, 2026

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [Ollama](https://ollama.ai/)
- Powered by [Gemma 2B](https://ai.google.dev/gemma) by Google
- Part of [Hacktoberfest 2026](https://hacktoberfest.com/)
