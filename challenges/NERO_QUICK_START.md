# Nero - Quick Start Guide

## What is Nero?

**Nero** is your all-in-one AI voice assistant that combines three services:
- 💬 **General Chat** - Friendly conversation about anything
- ☕ **Coffee Barista** - Place coffee orders
- 🧘 **Wellness Companion** - Daily check-ins

When you connect, Nero asks which service you want and switches to that mode!

## How to Run

### Windows
```powershell
.\run_nero.ps1
```

### Linux/Mac
```bash
chmod +x run_nero.sh
./run_nero.sh
```

### First Time Setup

1. **Install dependencies:**
   ```powershell
   cd backend
   uv sync
   ```

2. **Download models:**
   ```powershell
   uv run python src/main_agent.py download-files
   ```

3. **Configure API keys** in `backend\.env.local`:
   ```env
   MURF_API_KEY=your_key
   GOOGLE_API_KEY=your_key
   DEEPGRAM_API_KEY=your_key
   ```

## Example Conversation

```
Nero: "Hi! Welcome to Nero AI Services! I can help you with:
       1. General Chat - Have a friendly conversation about anything
       2. Coffee Ordering - Place an order at our virtual coffee shop
       3. Wellness Check-in - Daily reflection on mood, energy, and goals
       
       Which service would you like today?"

You: "I'd like to order coffee"

Nero: "Perfect! Connecting you to our coffee shop barista. Get ready to order!"
      "Hi! Welcome to our coffee shop. What can I get for you today?"

You: "I'd like a medium latte with oat milk"

Nero: "Great choice! Would you like any extras like whipped cream or syrups?"

You: "Add vanilla syrup please"

Nero: "Got it! And what name should I put on the order?"

You: "Alex"

Nero: "Let me confirm: Medium Latte with oat milk and vanilla syrup for Alex. 
       Is that correct?"

You: "Yes"

Nero: "Order saved successfully! Your Medium Latte with oat milk and vanilla syrup 
       for Alex has been saved. Thank you and have a great day!"
```

## Service Details

### 1. General Chat
Just have a conversation! Ask questions, discuss topics, get information.

**Example:**
- "Tell me about quantum computing"
- "What's the weather like in Paris?"
- "Tell me a joke"

### 2. Coffee Barista
Place coffee orders with full customization.

**What you can order:**
- Drinks: Latte, Cappuccino, Espresso, Americano, Mocha, Macchiato, Flat White
- Sizes: Small, Medium, Large
- Milk: Whole, Skim, Oat, Almond, Soy, Coconut
- Extras: Whipped cream, Extra shot, Vanilla/Caramel/Hazelnut syrup

**Orders saved to:** `backend/orders/order_TIMESTAMP.json`

### 3. Wellness Companion
Daily check-ins for your mental and physical wellbeing.

**What it asks:**
- How you're feeling (mood)
- Your energy level
- What's stressing you
- Your daily objectives (1-3 things)
- Self-care intentions

**Check-ins saved to:** `backend/wellness_log.json`

**Special feature:** Nero remembers your previous check-ins and references them!

## Switching Services

You can switch services mid-conversation by saying:
- "I want to switch to coffee ordering"
- "Let's do a wellness check-in instead"
- "Can we just chat?"

## Running in Different Modes

### Console Mode (Talk in Terminal)
```powershell
cd backend
uv run python src/main_agent.py console
```

### Dev Mode (For Frontend)
```powershell
cd backend
uv run python src/main_agent.py dev
```

Then open your frontend at `http://localhost:3000`

## Troubleshooting

**"Module not found"**
```powershell
cd backend
uv sync
```

**"Invalid API key"**
- Check `backend\.env.local` has all three keys
- No extra spaces or quotes

**"Models not found"**
```powershell
cd backend
uv run python src/main_agent.py download-files
```

## What Makes Nero Special?

1. **One Agent, Multiple Services** - No need to run separate agents
2. **Intelligent Routing** - Nero knows which mode to switch to
3. **Context Preservation** - Wellness mode remembers your history
4. **Natural Conversations** - Powered by Google Gemini
5. **Ultra-Fast Voice** - Murf Falcon TTS (fastest in the industry)

## Next Steps

1. ✅ Run Nero and try all three services
2. 🎥 Record a demo video showing service switching
3. 📱 Share on LinkedIn with:
   - Hashtags: `#MurfAIVoiceAgentsChallenge` `#10DaysofAIVoiceAgents`
   - Tag: @Murf AI
   - Mention: "Built with Murf Falcon - the fastest TTS API"

## Learn More

- Full documentation: [README.md](../README.md)
- Day 3 details: [DAY3_WELLNESS_COMPANION.md](DAY3_WELLNESS_COMPANION.md)
- API setup: [API_KEYS_SETUP.md](../API_KEYS_SETUP.md)

---

**Nero** - One agent, infinite possibilities! 🚀
