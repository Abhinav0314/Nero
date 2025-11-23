# 🎙️ Coffee Shop Barista Voice Agent

> Built for the **10 Days of Voice Agents Challenge** by [murf.ai](https://murf.ai)

An AI-powered coffee shop barista that takes voice orders using **Murf Falcon TTS** (the fastest TTS API), LiveKit for real-time voice streaming, and Google Gemini for intelligent conversations.

## ✨ Features

### Day 1 Implementation ✅
- ✅ Real-time voice interaction with LiveKit
- ✅ Murf Falcon TTS integration for ultra-fast voice synthesis
- ✅ Google Gemini LLM for natural conversations
- ✅ Deepgram STT for speech recognition
- ✅ Modern React frontend with voice controls
- ✅ Background noise cancellation

### Day 2 Implementation ✅
- ✅ **Coffee Shop Barista Persona**: Friendly, conversational barista
- ✅ **Order State Management**: Tracks drink type, size, milk, extras, and customer name
- ✅ **Clarifying Questions**: Agent asks follow-up questions until order is complete
- ✅ **JSON Order Persistence**: Saves completed orders with timestamps
- ✅ **HTML Order Visualization** (Advanced Challenge): Beautiful animated coffee cup display
- ✅ **Custom UI**: Coffee shop themed interface with brown color scheme

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ with [uv](https://docs.astral.sh/uv/) package manager
- Node.js 18+ with pnpm
- LiveKit Server (install: `brew install livekit` or [download](https://github.com/livekit/livekit/releases))

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
# Backend
cd backend
uv sync
uv run python src/agent.py download-files

# Frontend
cd frontend
pnpm install
```

### 4. Start Everything

**Windows:**
```powershell
.\start_app.ps1
```

**Linux/Mac:**
```bash
chmod +x start_app.sh
./start_app.sh
```

**Or manually in 3 separate terminals:**

```powershell
# Terminal 1: LiveKit Server
livekit-server --dev

# Terminal 2: Backend
cd backend
uv run python src/agent.py dev

# Terminal 3: Frontend
cd frontend
pnpm dev
```

### 5. Place Your Order! ☕

1. Open **http://localhost:3000**
2. Click **"Start ordering"**
3. Speak your order: "I'd like a medium latte with oat milk"
4. Answer any clarifying questions
5. Provide your name when asked
6. Check `backend/orders/` for your saved order!

## 📂 Project Structure

```
MURF/
├── backend/
│   ├── src/
│   │   ├── agent.py          # Main agent with barista persona
│   │   └── barista.py        # Order state & JSON management
│   ├── orders/               # Saved order JSON files
│   └── .env.local            # Backend config with API keys
├── frontend/
│   ├── app-config.ts         # Coffee shop UI customization
│   ├── public/
│   │   └── order-visualization.html  # Animated order display
│   └── .env.local            # Frontend config
├── start_app.ps1             # Windows startup script
├── start_app.sh              # Linux/Mac startup script
├── SETUP_GUIDE.md            # Detailed setup instructions
└── API_KEYS_SETUP.md         # API key configuration guide
```

## 🎨 Example Order JSON

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

## 🖼️ Order Visualization

Access the HTML order visualization at:
**http://localhost:3000/order-visualization.html**

Features:
- Animated coffee cup that changes size
- Whipped cream visualization
- Clean order details card
- Responsive design

## 🎯 Available Options

### Drinks
Latte, Cappuccino, Espresso, Americano, Mocha, Macchiato, Flat White

### Sizes
Small, Medium, Large

### Milk Options
Whole milk, Skim milk, Oat milk, Almond milk, Soy milk, Coconut milk, No milk

### Popular Extras
Whipped cream, Extra shot, Vanilla syrup, Caramel syrup, Hazelnut syrup, Sugar, Honey

## 📊 Testing

Test the agent in console mode (voice directly in terminal):

```powershell
cd backend
uv run python src/agent.py console
```

Run the test suite:

```powershell
cd backend
uv run pytest
```

## 🔧 Troubleshooting

### Common Issues

**"Cannot connect to LiveKit"**
- Make sure `livekit-server --dev` is running

**"Invalid API Key"**
- Check that all three keys are in `backend\.env.local`
- Verify keys have no extra spaces or quotes

**Frontend won't start**
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules
pnpm install
```

**Backend module errors**
```powershell
cd backend
uv sync
```

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for more troubleshooting tips.

## 📱 Sharing on LinkedIn

Once you've tested the agent, share your progress! 🎉

### Post Template

```
🎙️ Day 2 of the #MurfAIVoiceAgentsChallenge complete! ☕

Built an AI Coffee Shop Barista that:
✅ Takes voice orders in real-time
✅ Uses Murf Falcon TTS (fastest TTS API!)
✅ Asks clarifying questions intelligently
✅ Saves orders to structured JSON files
✅ Shows beautiful order visualizations

Tech stack:
• Murf Falcon for ultra-fast TTS
• LiveKit for real-time voice streaming
• Google Gemini for natural conversation
• Deepgram for speech recognition

Building 10 voice agents in 10 days with @Murf AI 🚀

#10DaysofAIVoiceAgents #VoiceAI #AI #MurfFalcon #LiveKit

[Include video/screenshot of your agent in action]
```

**Don't forget:**
- Tag @Murf AI (official handle)
- Use hashtags: #MurfAIVoiceAgentsChallenge #10DaysofAIVoiceAgents
- Record a short demo video showing voice ordering

## 🔗 Important Links

- **Challenge Repo**: https://github.com/murf-ai/ten-days-of-voice-agents-2025
- **Day 1 Task**: https://github.com/murf-ai/ten-days-of-voice-agents-2025/blob/main/challenges/Day%201%20Task.md
- **Day 2 Task**: https://github.com/murf-ai/ten-days-of-voice-agents-2025/blob/main/challenges/Day%202%20Task.md
- **Murf Falcon Docs**: https://murf.ai/api/docs/text-to-speech/streaming
- **LiveKit Agents Docs**: https://docs.livekit.io/agents
- **LiveKit Community**: https://livekit.io/join-slack

## 🚢 Deployment Options

### Option 1: Deploy to LiveKit Cloud

```powershell
cd backend
lk cloud deploy
```

### Option 2: Docker

```powershell
cd backend
docker build -t coffee-barista-agent .
docker run coffee-barista-agent
```

### Option 3: Manual VPS Deployment

See [deployment guide](https://docs.livekit.io/agents/ops/deployment/) for production setup.

## 🏆 Challenge Progress

- [x] Day 1: Get starter agent running
- [x] Day 2: Coffee Shop Barista
- [ ] Day 3: TBD
- [ ] Day 4: TBD
- [ ] Day 5: TBD
- [ ] Day 6: TBD
- [ ] Day 7: TBD
- [ ] Day 8: TBD
- [ ] Day 9: TBD
- [ ] Day 10: TBD

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a challenge project, but contributions and improvements are welcome!

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 💡 Tips & Best Practices

- **Keep API keys secure**: Never commit `.env.local` to git
- **Test incrementally**: Use console mode to test agent logic
- **Monitor usage**: Check your API usage dashboards
- **Customize the persona**: Edit instructions in `agent.py`
- **Extend functionality**: Add more tools using `@function_tool`

## 🆘 Support

- Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
- Review [API_KEYS_SETUP.md](API_KEYS_SETUP.md) for key configuration
- Join [LiveKit Community Slack](https://livekit.io/join-slack)
- Open an issue on GitHub

---

**Built with ❤️ for the AI Voice Agents Challenge by murf.ai**

Ready to build the future of voice AI? Let's go! 🚀☕
