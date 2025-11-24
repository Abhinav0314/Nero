# Day 3 Quick Start Guide - Health & Wellness Companion

## What You've Built

A supportive AI wellness companion that:
- Conducts daily check-ins about mood and energy
- Helps set daily objectives
- Offers realistic, grounded advice
- Remembers previous conversations
- Saves all check-ins to JSON

## How to Run

### Option 1: Using the Script (Easiest)

**Windows:**
```powershell
.\run_wellness_agent.ps1
```

**Linux/Mac:**
```bash
chmod +x run_wellness_agent.sh
./run_wellness_agent.sh
```

### Option 2: Manual Commands

**First time only - Download models:**
```powershell
cd backend
uv run python src/wellness_agent.py download-files
```

**Run in console mode (talk in terminal):**
```powershell
cd backend
uv run python src/wellness_agent.py console
```

**Run in dev mode (for frontend):**
```powershell
cd backend
uv run python src/wellness_agent.py dev
```

## Example Conversation

```
Agent: "Hi! It's great to connect with you. This is your first check-in. 
        Welcome! How are you feeling today?"

You: "I'm feeling pretty good, a bit tired though."

Agent: "I'm glad you're feeling good overall. What's your energy level like - 
        would you say it's high, medium, or low?"

You: "I'd say medium energy."

Agent: "That sounds reasonable. Is there anything stressing you out right now?"

You: "Just work deadlines, nothing major."

Agent: "I understand work deadlines can be on your mind. What are 1-3 things 
        you'd like to accomplish today?"

You: "I want to finish my report, go for a walk, and call my mom."

Agent: "Those sound like great goals! Is there anything you want to do for 
        yourself today - any self-care activities?"

You: "The walk is my self-care, and maybe reading before bed."

Agent: "Perfect! Let me recap: You're feeling good but a bit tired with medium 
        energy. Work deadlines are on your mind. Your objectives are to finish 
        your report, go for a walk, and call your mom. For self-care, you're 
        planning the walk and reading before bed. Does this sound right?"

You: "Yes, that's perfect!"

Agent: "Check-in saved successfully! Remember, small steps lead to big changes. 
        You've got this!"
```

## Next Day

When you run the agent again, it will reference your previous check-in:

```
Agent: "Hi! It's great to connect with you again. Last time we talked on 
        2025-11-24, you mentioned feeling good but a bit tired with medium 
        energy. You had objectives to finish your report, go for a walk, 
        and call your mom. How are you feeling today?"
```

## Where Data is Saved

All check-ins are saved to: `backend/wellness_log.json`

Example entry:
```json
{
  "mood": "good but a bit tired",
  "energy_level": "medium",
  "stress_factors": "work deadlines",
  "objectives": [
    "finish my report",
    "go for a walk",
    "call my mom"
  ],
  "self_care_intentions": "walk and reading before bed",
  "timestamp": "2025-11-24T00:15:30.123456",
  "date": "2025-11-24",
  "agent_summary": "User feeling good but a bit tired with medium energy. Stressed about: work deadlines."
}
```

## Completing the Challenge

To complete Day 3:

1. ✅ **Run the wellness agent** - Use console or dev mode
2. 🎥 **Record a video** - Show the agent in action and the `wellness_log.json` file
3. 📱 **Post on LinkedIn** with:
   - Description of what you built
   - Mention: "Building with Murf Falcon - the fastest TTS API"
   - Tag: @Murf AI (official handle)
   - Hashtags: `#MurfAIVoiceAgentsChallenge` `#10DaysofAIVoiceAgents`

### LinkedIn Post Template

```
🧘 Day 3 of the #MurfAIVoiceAgentsChallenge complete!

Built a Health & Wellness Voice Companion that:
✅ Conducts daily check-ins about mood and energy
✅ Helps set realistic daily objectives
✅ Remembers previous conversations
✅ Offers supportive, grounded advice
✅ Saves all check-ins to structured JSON

The agent references past check-ins to show continuity and care - 
it actually remembers what we talked about!

Tech stack:
• Murf Falcon for ultra-fast TTS
• LiveKit for real-time voice streaming
• Google Gemini for empathetic conversation
• Deepgram for speech recognition

Building 10 voice agents in 10 days with @Murf AI 🚀

#10DaysofAIVoiceAgents #VoiceAI #AI #MurfFalcon #WellnessTech

[Attach your demo video]
```

## Troubleshooting

**Agent not starting:**
- Make sure you've run `uv sync` in the backend directory
- Check that `.env.local` has all required API keys

**No previous check-in context:**
- This is normal on first run
- After your first check-in, the next session will reference it

**Models not downloading:**
- Make sure you have internet connection
- Run: `uv run python src/wellness_agent.py download-files`

## Advanced Goals (Optional)

Want to go further? Try implementing:

1. **MCP Integration** - Connect to Notion or Todoist to create tasks from objectives
2. **Weekly Reflection** - Analyze mood trends over the week
3. **Follow-up Reminders** - Create calendar events for self-care activities

See [DAY3_WELLNESS_COMPANION.md](DAY3_WELLNESS_COMPANION.md) for details.

## Need Help?

- Check the main [README.md](../README.md)
- Review [SETUP_GUIDE.md](../SETUP_GUIDE.md)
- Join [LiveKit Community Slack](https://livekit.io/join-slack)

---

**You've built something meaningful! 🎉**

This wellness companion can genuinely help people reflect on their day and set intentions. 
Keep building! 🚀
