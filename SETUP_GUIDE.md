# Coffee Shop Barista Voice Agent - Setup Guide

This project is a complete implementation of the **10 Days of Voice Agents Challenge** (Days 1 & 2) by murf.ai, featuring an AI Coffee Shop Barista powered by Murf Falcon TTS.

## 🎯 What This Does

- **Day 1**: Basic voice agent setup with Murf Falcon TTS for ultra-fast voice synthesis
- **Day 2**: Coffee Shop Barista that:
  - Takes voice orders for coffee
  - Collects: drink type, size, milk preference, extras, and customer name
  - Asks clarifying questions until order is complete
  - Saves completed orders to JSON files
  - Shows a beautiful HTML visualization of the order

## 🚀 Quick Start

### Prerequisites

Before you begin, make sure you have:

- **Python 3.9+** with [uv](https://docs.astral.sh/uv/) package manager
- **Node.js 18+** with pnpm
- **LiveKit Server** (install with `brew install livekit` on Mac or follow [installation guide](https://docs.livekit.io/home/self-hosting/local/))

### Step 1: Get Your API Keys

You'll need to obtain the following API keys:

1. **Murf Falcon API Key**: Get it from [https://murf.ai/api](https://murf.ai/api)
2. **Google Gemini API Key**: Get it from [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
3. **Deepgram API Key**: Get it from [https://console.deepgram.com/](https://console.deepgram.com/)

### Step 2: Configure Backend

```powershell
cd backend

# Install dependencies
uv sync

# The .env.local file is already created with placeholders
# Edit it and add your real API keys:
notepad .env.local

# Download required models (Silero VAD, turn detector)
uv run python src/agent.py download-files
```

**Edit `backend\.env.local`** and replace the placeholder values:
```env
MURF_API_KEY=your_actual_murf_api_key
GOOGLE_API_KEY=your_actual_google_api_key
DEEPGRAM_API_KEY=your_actual_deepgram_api_key
```

### Step 3: Configure Frontend

```powershell
cd frontend

# Install dependencies
pnpm install

# The .env.local is already created - no changes needed for local dev
```

### Step 4: Run Everything

You have two options:

#### Option A: Run with the convenience script (Linux/Mac)

```bash
chmod +x start_app.sh
./start_app.sh
```

#### Option B: Run services individually (Windows/all platforms)

Open 3 separate terminal windows:

**Terminal 1 - LiveKit Server:**
```powershell
livekit-server --dev
```

**Terminal 2 - Backend Agent:**
```powershell
cd backend
uv run python src/agent.py dev
```

**Terminal 3 - Frontend:**
```powershell
cd frontend
pnpm dev
```

### Step 5: Test the Barista!

1. Open **http://localhost:3000** in your browser
2. Click **"Start ordering"**
3. Talk to the AI barista and place your coffee order
4. The agent will ask clarifying questions to complete your order
5. Once done, check `backend/orders/` for your saved order JSON file
6. View the order visualization at **http://localhost:3000/order-visualization.html**

## 📁 Project Structure

```
MURF/
├── backend/
│   ├── src/
│   │   ├── agent.py           # Main agent with Murf Falcon integration
│   │   └── barista.py         # Order state management & JSON saving
│   ├── orders/                # Saved order JSON files
│   ├── .env.local             # Backend config (with your API keys)
│   └── pyproject.toml
├── frontend/
│   ├── app-config.ts          # UI customization (Coffee Shop theme)
│   ├── public/
│   │   └── order-visualization.html  # Order display page
│   ├── .env.local             # Frontend config
│   └── package.json
└── README.md
```

## 🎨 Features Implemented

### Day 1 ✅
- ✅ LiveKit voice agent setup
- ✅ Murf Falcon TTS integration
- ✅ Google Gemini LLM integration
- ✅ Deepgram STT integration
- ✅ Frontend with voice interaction

### Day 2 ✅
- ✅ Coffee Shop Barista persona
- ✅ Order state management (drink, size, milk, extras, name)
- ✅ Clarifying questions until order complete
- ✅ JSON order file saving with timestamps
- ✅ HTML beverage visualization (Advanced Challenge)
- ✅ Coffee shop themed UI (brown color scheme)

## 🧪 Testing

Test the backend agent directly in your terminal:

```powershell
cd backend
uv run python src/agent.py console
```

Run the test suite:

```powershell
cd backend
uv run pytest
```

## 📝 Example Order JSON

After placing an order, you'll find files like this in `backend/orders/`:

```json
{
  "drinkType": "Latte",
  "size": "medium",
  "milk": "oat milk",
  "extras": ["vanilla syrup", "whipped cream"],
  "name": "Alex",
  "timestamp": "2025-11-23T10:30:00.123456"
}
```

## 📊 Order Visualization

The project includes a beautiful HTML visualization (`frontend/public/order-visualization.html`) that:
- Shows a visual coffee cup that changes size based on order
- Displays whipped cream on the cup if ordered
- Lists all order details in a clean card layout
- Features a modern gradient background and smooth animations

## 🔧 Troubleshooting

### "Module not found" errors
```powershell
cd backend
uv sync
```

### "Cannot connect to LiveKit"
Make sure LiveKit server is running:
```powershell
livekit-server --dev
```

### Frontend won't start
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules
pnpm install
```

### Agent not responding
Check that all API keys are correctly set in `backend\.env.local`

## 🌐 Sharing Your Work (LinkedIn Post)

Once everything works, record a short video and post on LinkedIn with:

**Post Template:**
```
🎙️ Just completed Day 2 of the #MurfAIVoiceAgentsChallenge!

Built an AI Coffee Shop Barista using:
✅ Murf Falcon TTS (fastest TTS API)
✅ LiveKit for real-time voice
✅ Google Gemini for intelligent conversations
✅ Automated order management with JSON persistence

The agent takes complete coffee orders via voice, asks clarifying questions, and saves them to structured files. Also created a beautiful HTML visualization!

Building 10 voice agents in 10 days with @Murf AI

#10DaysofAIVoiceAgents #VoiceAI #AI #MurfFalcon #LiveKit
```

## 📚 Resources

- [Murf Falcon TTS Docs](https://murf.ai/api/docs/text-to-speech/streaming)
- [LiveKit Agents Docs](https://docs.livekit.io/agents)
- [Challenge Repository](https://github.com/murf-ai/ten-days-of-voice-agents-2025)
- [Day 1 Task](https://github.com/murf-ai/ten-days-of-voice-agents-2025/blob/main/challenges/Day%201%20Task.md)
- [Day 2 Task](https://github.com/murf-ai/ten-days-of-voice-agents-2025/blob/main/challenges/Day%202%20Task.md)

## 🏆 Next Steps

- [ ] Get your API keys and add them to `.env.local`
- [ ] Run the agent and test it
- [ ] Record a demo video showing voice ordering
- [ ] Post on LinkedIn with the hashtags
- [ ] Move on to Day 3 challenges!

## 📄 License

MIT License - see LICENSE file for details.

---

Built for the **AI Voice Agents Challenge** by [murf.ai](https://murf.ai)
