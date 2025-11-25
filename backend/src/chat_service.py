import logging
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    metrics,
    tokenize,
    RunContext,
    MetricsCollectedEvent
)
from livekit.plugins import murf, deepgram, google, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("chat_service")

class GeneralChatAgent(Agent):
    """Day 1 - General conversation agent"""
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly, helpful AI assistant. You can chat about anything the user wants to discuss.

IMPORTANT: When the user first connects, greet them warmly with something like "Hi! I'm your AI assistant. What would you like to chat about today?"

Be conversational, engaging, and helpful. You can:
- Answer questions on various topics
- Have casual conversations
- Provide information and explanations
- Tell jokes or stories
- Discuss current events, technology, science, etc.

Keep your responses natural and concise. Be warm and personable, like talking to a friend.""",
        )
    
    async def on_user_transcript(self, transcript: str):
        logger.info(f"User transcript received: {transcript}")
        
    async def on_agent_speech(self, speech: str):
        logger.info(f"Agent speech generated: {speech}")

async def entrypoint(ctx: JobContext):
    logger.info("Starting Chat Service")
    
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
        agent=GeneralChatAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
