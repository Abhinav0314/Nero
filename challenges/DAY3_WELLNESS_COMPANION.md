# Day 3 - Health & Wellness Voice Companion

## Overview

This is the implementation of **Day 3** of the Murf AI Voice Agents Challenge - a Health & Wellness Voice Companion that conducts daily check-ins with users.

## Features

### Primary Goal (Completed) ✅

The wellness companion:

1. **Conducts Daily Check-ins** via voice conversation
   - Asks about mood and energy levels
   - Inquires about stress factors
   - Helps identify 1-3 daily objectives/intentions
   - Asks about self-care activities

2. **Offers Supportive Advice**
   - Provides simple, realistic, and grounded suggestions
   - Non-medical, non-diagnostic guidance
   - Examples: "Take a 5-minute walk", "Break tasks into smaller steps"

3. **Persists Data to JSON**
   - Saves each check-in to `wellness_log.json`
   - Stores: date/time, mood, energy level, objectives, stress factors, self-care intentions

4. **References Past Check-ins**
   - Loads previous check-in history
   - Naturally references the last session in conversation
   - Shows continuity and care across sessions

5. **Confirms with Recap**
   - Provides a brief summary of what was shared
   - Asks for confirmation before saving

## File Structure

```
backend/src/
├── wellness_agent.py    # Main wellness companion agent
├── wellness.py          # Wellness state management and JSON persistence
├── agent.py            # Original barista agent (Day 2)
└── barista.py          # Barista state management (Day 2)
```

## How to Run

### 1. Download Required Models (First Time Only)

```bash
cd backend
uv run python src/wellness_agent.py download-files
```

### 2. Run in Console Mode (Talk directly in terminal)

```bash
uv run python src/wellness_agent.py console
```

### 3. Run in Dev Mode (For use with frontend)

```bash
uv run python src/wellness_agent.py dev
```

Then open your frontend application and connect to the agent.

## Data Persistence

All wellness check-ins are saved to `wellness_log.json` in the backend directory.

### Example Entry:

```json
{
  "mood": "good but a bit tired",
  "energy_level": "medium",
  "stress_factors": "upcoming deadline at work",
  "objectives": [
    "finish the project report",
    "go for a 20-minute walk",
    "call mom"
  ],
  "self_care_intentions": "take a short walk and read before bed",
  "timestamp": "2025-11-24T00:15:30.123456",
  "date": "2025-11-24",
  "agent_summary": "User feeling good but a bit tired with medium energy. Stressed about: upcoming deadline at work."
}
```

## Agent Behavior

The wellness companion:

- **Greets warmly** and asks how you're feeling
- **Listens empathetically** without being pushy
- **Remembers** your previous check-in and references it naturally
- **Offers practical advice** that's small and actionable
- **Never diagnoses** or provides medical advice
- **Confirms** your check-in details before saving

## Example Conversation

```
Agent: "Hi! It's great to connect with you again. Last time we talked, 
       you mentioned feeling a bit low on energy. How are you feeling today?"

User: "I'm feeling better today, more energized."

Agent: "That's wonderful to hear! What's your energy level like on a scale - 
       would you say it's high, medium, or low?"

User: "I'd say it's pretty high today."

Agent: "Great! Is there anything stressing you out right now?"

User: "Just the usual work deadlines, nothing major."

Agent: "I understand. What are 1-3 things you'd like to accomplish today?"

User: "I want to finish my project report, go for a walk, and maybe read a book."

Agent: "Those sound like great goals! Is there anything you want to do for 
       yourself today - any self-care activities?"

User: "Yeah, the walk and reading are my self-care for today."

Agent: "Perfect! Let me recap what you shared: You're feeling better with high 
       energy. You mentioned work deadlines are on your mind. Your objectives 
       are to finish your project report, go for a walk, and read a book. 
       And for self-care, you're planning the walk and reading. Does this sound right?"

User: "Yes, that's right!"

Agent: "Check-in saved successfully! Remember, small steps lead to big changes. 
       You've got this!"
```

## Technical Implementation

### Wellness State Management (`wellness.py`)

- `WellnessState`: Manages current check-in state
- `load_wellness_history()`: Loads previous check-ins from JSON
- `save_wellness_checkin()`: Appends new check-in to history
- `get_last_checkin()`: Retrieves most recent check-in
- `generate_context_from_history()`: Creates context for the agent

### Agent Implementation (`wellness_agent.py`)

- `WellnessCompanion`: Main agent class extending `Agent`
- `complete_checkin()`: Function tool to save check-in data
- Dynamic instructions that include previous check-in context
- Uses Murf Falcon TTS for ultra-fast voice synthesis
- Deepgram STT for speech recognition
- Google Gemini 2.5 Flash for LLM processing

## Environment Variables

Make sure your `.env.local` file contains:

```
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
MURF_API_KEY=your_murf_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
GOOGLE_API_KEY=your_google_api_key
```

## Advanced Goals (Optional)

The following advanced goals can be implemented:

1. **MCP Integration for Tasks/Notes**
   - Connect to Notion, Todoist, or Zapier MCP servers
   - Create tasks from objectives
   - Mark objectives as complete in follow-up sessions

2. **Weekly Reflection Using JSON History**
   - Analyze mood trends over the week
   - Track objective completion rates
   - Provide supportive insights

3. **Follow-up Reminders via MCP Tools**
   - Create calendar events for self-care activities
   - Set reminders for important objectives
   - Confirm before creating external reminders

## Challenge Completion

To complete Day 3:

1. ✅ Build the wellness companion agent
2. ✅ Implement JSON persistence
3. ✅ Add history context to conversations
4. 🎥 Record a video showing the agent in action
5. 📱 Post on LinkedIn with hashtags #MurfAIVoiceAgentsChallenge and #10DaysofAIVoiceAgents

## License

MIT License - See LICENSE file for details
