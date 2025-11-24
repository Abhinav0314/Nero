# 🎙️ Nero - AI Services Platform

> Built for the **10 Days of Voice Agents Challenge** by [murf.ai](https://murf.ai)

**Nero** is a unified AI voice agent platform that combines multiple AI services in one intelligent assistant. Using **Murf Falcon TTS** (the fastest TTS API), LiveKit for real-time voice streaming, and Google Gemini for intelligent conversations.

## ✨ What is Nero?

**Nero** is a smart AI receptionist that asks which service you need when you connect, then seamlessly switches to that mode:

1. **General Chat** (Day 1) - Friendly conversation about anything
2. **Coffee Shop Barista** (Day 2) - Place coffee orders with full order management
3. **Wellness Companion** (Day 3) - Daily check-ins for mood, energy, and goal setting

### One Agent, Three Services

Instead of running separate agents, Nero intelligently routes you to the right service based on your needs!

## 🚀 Quick Start with Nero

### Prerequisites

- Python 3.9+ with [uv](https://docs.astral.sh/uv/) package manager
- Node.js 18+ with pnpm (optional, for frontend)
- LiveKit Server (optional, for frontend): `brew install livekit` or [download](https://github.com/livekit/livekit/releases)

### 1. Get API Keys

You need three API keys (all have free tiers):

1. **Murf Falcon**: https://murf.ai/api
2. **Google Gemini**: https://aistudio.google.com/app/apikey
3. **Deepgram**: https://console.deepgram.com/

📖 See [API_KEYS_SETUP.md](API_KEYS_SETUP.md) for detailed instructions.

### 2. Configure Environment

Edit `backend\.env.local` and add your API keys:

```env
MURF_API_KEY=your_murf_api_key
GOOGLE_API_KEY=your_google_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
```

### 3. Install Dependencies

```powershell
cd backend
uv sync
uv run python src/main_agent.py download-files
```

### 4. Run All Services at Once! 🚀

The easiest way to start everything (LiveKit server, backend, and frontend):

**Windows:**
```powershell
.\run.ps1
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

This will start:
- 📡 LiveKit Server on `ws://127.0.0.1:7880`
- 🤖 Backend Agent (listening for connections)
- 🌐 Frontend on `http://localhost:3000`

**Alternative: Run Nero Agent Only (without frontend):**

**Windows:**
```powershell
.\run_nero.ps1
```

**Linux/Mac:**
```bash
chmod +x run_nero.sh
./run_nero.sh
```

### 5. Choose Your Service

**NEW!** 🎨 Visual Service Selection

When you open the frontend (`http://localhost:3000`), you'll see a beautiful page with three service cards:

- 💬 **General Chat** - Have a friendly conversation about anything
- ☕ **Coffee Ordering** - Place an order at our virtual coffee shop
- 🧘 **Wellness Check-in** - Daily reflection on mood, energy, and goals

Just **click** the service you want, then click "Start" to begin your call!

The agent will already be in the right mode - no need to tell it which service you want!

## 🎯 Features by Service

### 1. General Chat (Day 1)
- 💬 Friendly, engaging conversation
- 🤖 Answer questions on various topics
- 🎭 Tell jokes, discuss current events
- 📚 Provide information and explanations

### 2. Coffee Shop Barista (Day 2)
- ☕ **Order Management**: Tracks drink, size, milk, extras, name
- 🗣️ **Natural Conversation**: Asks clarifying questions
- 💾 **JSON Persistence**: Saves orders to `backend/orders/`
- 🎨 **Order Visualization**: Beautiful HTML display

**Available Options:**
- Drinks: Latte, Cappuccino, Espresso, Americano, Mocha, Macchiato, Flat White
- Sizes: Small, Medium, Large
- Milk: Whole, Skim, Oat, Almond, Soy, Coconut, No milk
- Extras: Whipped cream, Extra shot, Vanilla/Caramel/Hazelnut syrup

### 3. Wellness Companion (Day 3)
- 🧘 **Daily Check-ins**: Supportive wellness conversations
- 😊 **Mood & Energy Tracking**: Asks how you're feeling
- 🎯 **Objective Setting**: Helps set 1-3 daily intentions
- 💾 **History Persistence**: Saves to `wellness_log.json`
- 🔄 **Context Memory**: References previous check-ins
- 💡 **Supportive Advice**: Realistic, grounded suggestions (non-medical)

## 📂 Project Structure

```
MURF/
├── backend/
│   ├── src/
│   │   ├── main_agent.py     # 🌟 Unified Nero agent (all services)
│   │   ├── agent.py          # Day 2: Barista agent (standalone)
│   │   ├── barista.py        # Day 2: Order state management
│   │   ├── wellness_agent.py # Day 3: Wellness agent (standalone)
│   │   └── wellness.py       # Day 3: Wellness state management
│   ├── orders/               # Saved coffee orders
│   ├── wellness_log.json     # Wellness check-in history
│   └── .env.local            # API keys configuration
├── frontend/                 # Optional React frontend
├── run_nero.ps1              # 🌟 Run unified Nero agent (Windows)
├── run_nero.sh               # 🌟 Run unified Nero agent (Linux/Mac)
├── start_app.ps1             # Run barista only (Windows)
├── run_wellness_agent.ps1    # Run wellness only (Windows)
└── challenges/               # Challenge documentation
```

## 🎨 Example Interactions

### General Chat
```
You: "Tell me about quantum computing"
Nero: "Quantum computing is a fascinating field that uses quantum mechanics..."
```

### Coffee Ordering
```
You: "I'd like to order a coffee"
Nero: "Great! What kind of drink would you like?"
You: "A medium latte with oat milk"
Nero: "Perfect! Would you like any extras like whipped cream or syrups?"
You: "Add vanilla syrup please"
Nero: "Got it! And what name should I put on the order?"
You: "Alex"
Nero: "Let me confirm: Medium Latte with oat milk and vanilla syrup for Alex. Is that correct?"
```

### Wellness Check-in
```
Nero: "Hi! Last time we talked, you mentioned feeling a bit low on energy. 
       How are you feeling today?"
You: "I'm feeling much better today, more energized"
Nero: "That's wonderful to hear! What's your energy level like - high, medium, or low?"
You: "I'd say high today"
Nero: "Great! What are 1-3 things you'd like to accomplish today?"
```

## 🔄 Running Individual Agents (Optional)

If you prefer to run each agent separately:

**Coffee Barista:**
```powershell
.\start_app.ps1
```

**Wellness Companion:**
```powershell
.\run_wellness_agent.ps1
```

## 📊 Data Persistence

### Coffee Orders
Saved to `backend/orders/order_TIMESTAMP.json`:
```json
{
  "drinkType": "Latte",
  "size": "medium",
  "milk": "oat milk",
  "extras": ["vanilla syrup"],
  "name": "Alex",
  "timestamp": "2025-11-24T00:30:00.123456"
}
```

### Wellness Check-ins
Saved to `backend/wellness_log.json`:
```json
[
  {
    "mood": "energized",
    "energy_level": "high",
    "objectives": ["finish report", "exercise", "call friend"],
    "timestamp": "2025-11-24T00:15:30.123456",
    "date": "2025-11-24"
  }
]
```

## 🧪 Testing

Test Nero in console mode (talk directly in terminal):

```powershell
cd backend
uv run python src/main_agent.py console
```

Run the test suite:

```powershell
cd backend
uv run pytest
```

## 🔧 Troubleshooting

**"Cannot find module"**
```powershell
cd backend
uv sync
```

**"Invalid API Key"**
- Check that all three keys are in `backend\.env.local`
- Verify keys have no extra spaces or quotes

**Models not downloaded**
```powershell
cd backend
uv run python src/main_agent.py download-files
```

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for more troubleshooting tips.

## 🏆 Challenge Progress

- [x] Day 1: General Chat Assistant
- [x] Day 2: Coffee Shop Barista
- [x] Day 3: Health & Wellness Companion
- [x] **Bonus**: Unified Nero Agent with Service Selection
- [ ] Day 4: TBD
- [ ] Day 5: TBD
- [ ] Day 6: TBD
- [ ] Day 7: TBD
- [ ] Day 8: TBD
- [ ] Day 9: TBD
- [ ] Day 10: TBD

## 📱 Sharing on LinkedIn

Share your progress with the community! 🎉

```
🎙️ Built Nero - a unified AI voice agent platform! 🚀

One intelligent agent that handles:
✅ General conversation (Day 1)
✅ Coffee shop orders (Day 2)
✅ Wellness check-ins (Day 3)

When you connect, Nero asks which service you need and seamlessly switches modes!

Tech stack:
• Murf Falcon TTS (fastest TTS API!)
• LiveKit for real-time voice
• Google Gemini for intelligence
• Deepgram for speech recognition

Part of the #MurfAIVoiceAgentsChallenge with @Murf AI

#10DaysofAIVoiceAgents #VoiceAI #AI #MurfFalcon #LiveKit

[Attach your demo video]
```

## 🔗 Important Links

- **Challenge Repo**: https://github.com/murf-ai/ten-days-of-voice-agents-2025
- **Murf Falcon Docs**: https://murf.ai/api/docs/text-to-speech/streaming
- **LiveKit Agents Docs**: https://docs.livekit.io/agents
- **LiveKit Community**: https://livekit.io/join-slack

## 🚢 Deployment

Deploy to LiveKit Cloud:

```powershell
cd backend
lk cloud deploy
```

Or use Docker:

```powershell
cd backend
docker build -t nero-agent .
docker run nero-agent
```

See [deployment guide](https://docs.livekit.io/agents/ops/deployment/) for production setup.

## 💡 Tips & Best Practices

- **Keep API keys secure**: Never commit `.env.local` to git
- **Test incrementally**: Use console mode to test agent logic
- **Monitor usage**: Check your API usage dashboards
- **Customize personas**: Edit instructions in `main_agent.py`
- **Add more services**: Extend Nero with additional modes!

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
- Review [API_KEYS_SETUP.md](API_KEYS_SETUP.md) for key configuration
- See [challenges/](challenges/) for individual challenge docs
- Join [LiveKit Community Slack](https://livekit.io/join-slack)
- Open an issue on GitHub

---

**Built with ❤️ for the AI Voice Agents Challenge by murf.ai**

**Nero** - One agent, infinite possibilities. Ready to build the future of voice AI? Let's go! 🚀
