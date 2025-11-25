import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    metrics,
    tokenize,
    RunContext,
    function_tool,
    MetricsCollectedEvent
)
from livekit.plugins import murf, deepgram, google, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("wellness_service")

class WellnessState:
    """Manages the state of a wellness check-in session"""
    
    def __init__(self):
        self.mood: Optional[str] = None
        self.energy_level: Optional[str] = None
        self.stress_factors: Optional[str] = None
        self.objectives: List[str] = []
        self.self_care_intentions: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert wellness state to dictionary"""
        return {
            "mood": self.mood,
            "energy_level": self.energy_level,
            "stress_factors": self.stress_factors,
            "objectives": self.objectives,
            "self_care_intentions": self.self_care_intentions
        }
    
    def is_complete(self) -> bool:
        """Check if minimum required fields are filled"""
        return all([
            self.mood,
            self.energy_level,
            len(self.objectives) > 0
        ])
    
    def get_missing_fields(self) -> List[str]:
        """Return list of missing required fields"""
        missing = []
        if not self.mood:
            missing.append("mood")
        if not self.energy_level:
            missing.append("energy level")
        if len(self.objectives) == 0:
            missing.append("daily objectives")
        return missing


def load_wellness_history(log_file: str = "wellness_log.json") -> List[Dict]:
    """
    Load previous wellness check-in history from JSON file.
    Returns empty list if file doesn't exist.
    """
    log_path = Path(log_file)
    
    if not log_path.exists():
        logger.info(f"No existing wellness log found at {log_file}")
        return []
    
    try:
        with open(log_path, "r") as f:
            history = json.load(f)
            logger.info(f"Loaded {len(history)} previous check-ins from {log_file}")
            return history
    except json.JSONDecodeError:
        logger.error(f"Error reading wellness log from {log_file}")
        return []


def save_wellness_checkin(
    wellness_state: WellnessState,
    agent_summary: Optional[str] = None,
    log_file: str = "wellness_log.json"
) -> str:
    """
    Save the completed wellness check-in to a JSON file.
    Appends to existing history.
    Returns the path to the saved file.
    """
    # Load existing history
    history = load_wellness_history(log_file)
    
    # Create new entry
    checkin_data = wellness_state.to_dict()
    checkin_data["timestamp"] = datetime.now().isoformat()
    checkin_data["date"] = datetime.now().strftime("%Y-%m-%d")
    
    if agent_summary:
        checkin_data["agent_summary"] = agent_summary
    
    # Append to history
    history.append(checkin_data)
    
    # Save back to file
    log_path = Path(log_file)
    with open(log_path, "w") as f:
        json.dump(history, f, indent=2)
    
    logger.info(f"Wellness check-in saved to {log_file}")
    return str(log_path)


def get_last_checkin(log_file: str = "wellness_log.json") -> Optional[Dict]:
    """Get the most recent wellness check-in"""
    history = load_wellness_history(log_file)
    
    if len(history) == 0:
        return None
    
    return history[-1]


def format_wellness_summary(wellness_state: WellnessState) -> str:
    """Generate a human-readable summary of the wellness check-in"""
    summary_parts = []
    
    if wellness_state.mood:
        summary_parts.append(f"Mood: {wellness_state.mood}")
    
    if wellness_state.energy_level:
        summary_parts.append(f"Energy: {wellness_state.energy_level}")
    
    if wellness_state.stress_factors:
        summary_parts.append(f"Stress: {wellness_state.stress_factors}")
    
    if wellness_state.objectives:
        objectives_str = ", ".join(wellness_state.objectives)
        summary_parts.append(f"Objectives: {objectives_str}")
    
    if wellness_state.self_care_intentions:
        summary_parts.append(f"Self-care: {wellness_state.self_care_intentions}")
    
    return " | ".join(summary_parts)


def generate_context_from_history(log_file: str = "wellness_log.json") -> str:
    """
    Generate context string from previous check-ins to inform the agent.
    This helps the agent reference past sessions.
    """
    history = load_wellness_history(log_file)
    
    if len(history) == 0:
        return "This is the user's first check-in. Welcome them warmly."
    
    last_checkin = history[-1]
    
    context_parts = [
        f"The user has completed {len(history)} previous check-in(s).",
        f"Last check-in was on {last_checkin.get('date', 'unknown date')}."
    ]
    
    if last_checkin.get("mood"):
        context_parts.append(f"Last mood: {last_checkin['mood']}")
    
    if last_checkin.get("energy_level"):
        context_parts.append(f"Last energy level: {last_checkin['energy_level']}")
    
    if last_checkin.get("objectives"):
        objectives = last_checkin["objectives"]
        if len(objectives) > 0:
            context_parts.append(f"Last objectives: {', '.join(objectives[:3])}")
    
    context = " ".join(context_parts)
    context += "\n\nReference the previous check-in naturally in your conversation to show continuity and care."
    
    return context

class WellnessAgent(Agent):
    """Day 3 - Wellness companion agent"""
    
    def __init__(self) -> None:
        history_context = generate_context_from_history()
        
        super().__init__(
            instructions=f"""You are a warm, supportive health and wellness companion. You conduct daily check-ins with users to help them reflect on their wellbeing and set intentions for the day.

IMPORTANT: When the user first connects, greet them warmly with something like "Hi! Welcome to your daily wellness check-in. How are you feeling today?"

IMPORTANT CONTEXT FROM PREVIOUS CHECK-INS:
{history_context}

Your role is to:
1. Greet the user warmly and ask how they're feeling today
2. Ask about their mood and energy levels in a conversational way
3. Gently inquire if anything is stressing them out
4. Help them identify 1-3 practical objectives or intentions for the day
5. Ask if there's anything they want to do for themselves (rest, exercise, hobbies, self-care)
6. Offer simple, realistic, and grounded advice or reflections
7. Provide a brief recap of what they shared and confirm it sounds right
8. Use the complete_checkin tool when you have gathered their mood, energy level, and at least one objective

IMPORTANT GUIDELINES:
- Be conversational, empathetic, and supportive
- NEVER provide medical advice or diagnose conditions
- Keep suggestions small, actionable, and realistic
- Examples of good advice: "Take a 5-minute walk", "Break that task into smaller steps", "Remember to take short breaks"
- Reference their previous check-in naturally (if available) to show continuity
- Keep responses concise and natural - avoid complex formatting
- Don't be pushy - if they don't want to share something, that's okay
- Focus on practical wellbeing, not clinical health

Your responses should feel like talking to a caring friend who remembers your previous conversations.""",
        )
        self.wellness_state = WellnessState()

    @function_tool
    async def complete_checkin(
        self, 
        context: RunContext,
        mood: str,
        energy_level: str,
        objectives: str,
        stress_factors: str = "",
        self_care_intentions: str = ""
    ):
        """Use this tool when you have gathered the user's wellness check-in information to save it.
        
        Args:
            mood: The user's current mood or how they're feeling (e.g., "good", "tired", "anxious but hopeful")
            energy_level: The user's energy level (e.g., "high", "medium", "low", "drained")
            objectives: Comma-separated list of 1-3 things the user wants to accomplish today
            stress_factors: Optional description of what's stressing them out
            self_care_intentions: Optional self-care activities they want to do (exercise, rest, hobbies)
        """
        logger.info(f"Completing wellness check-in: mood={mood}, energy={energy_level}")
        
        self.wellness_state.mood = mood
        self.wellness_state.energy_level = energy_level
        
        if objectives:
            self.wellness_state.objectives = [obj.strip() for obj in objectives.split(",") if obj.strip()]
        
        if stress_factors:
            self.wellness_state.stress_factors = stress_factors
        
        if self_care_intentions:
            self.wellness_state.self_care_intentions = self_care_intentions
        
        agent_summary = f"User feeling {mood} with {energy_level} energy."
        if stress_factors:
            agent_summary += f" Stressed about: {stress_factors}."
        
        filepath = save_wellness_checkin(self.wellness_state, agent_summary)
        summary = format_wellness_summary(self.wellness_state)
        
        return f"Check-in saved successfully! Here's what I recorded: {summary}. Your check-in has been saved. Remember, small steps lead to big changes. You've got this!"

async def entrypoint(ctx: JobContext):
    logger.info("Starting Wellness Service")
    
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=False,  # Disabled for reliable greeting delivery
    )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    await session.start(
        agent=WellnessAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
