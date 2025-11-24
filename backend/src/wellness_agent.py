import logging

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from wellness import (
    WellnessState,
    save_wellness_checkin,
    format_wellness_summary,
    generate_context_from_history,
    get_last_checkin
)

logger = logging.getLogger("wellness_agent")

load_dotenv(".env.local")


class WellnessCompanion(Agent):
    def __init__(self) -> None:
        # Generate context from previous check-ins
        history_context = generate_context_from_history()
        
        super().__init__(
            instructions=f"""You are a warm, supportive health and wellness companion. You conduct daily check-ins with users to help them reflect on their wellbeing and set intentions for the day.

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
        
        # Update wellness state
        self.wellness_state.mood = mood
        self.wellness_state.energy_level = energy_level
        
        if objectives:
            self.wellness_state.objectives = [obj.strip() for obj in objectives.split(",") if obj.strip()]
        
        if stress_factors:
            self.wellness_state.stress_factors = stress_factors
        
        if self_care_intentions:
            self.wellness_state.self_care_intentions = self_care_intentions
        
        # Generate a summary for the agent
        agent_summary = f"User feeling {mood} with {energy_level} energy."
        if stress_factors:
            agent_summary += f" Stressed about: {stress_factors}."
        
        # Save check-in to JSON file
        filepath = save_wellness_checkin(self.wellness_state, agent_summary)
        summary = format_wellness_summary(self.wellness_state)
        
        return f"Check-in saved successfully! Here's what I recorded: {summary}. Your check-in has been saved. Remember, small steps lead to big changes. You've got this!"


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline
    session = AgentSession(
        # Speech-to-text (STT)
        stt=deepgram.STT(model="nova-3"),
        # Large Language Model (LLM)
        llm=google.LLM(
            model="gemini-2.5-flash",
        ),
        # Text-to-speech (TTS)
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        # VAD and turn detection
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # Allow the LLM to generate a response while waiting for the end of turn
        preemptive_generation=True,
    )

    # Metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session
    await session.start(
        agent=WellnessCompanion(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
