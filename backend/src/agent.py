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

from barista import OrderState, save_order, format_order_summary

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly barista at a specialty coffee shop. The user is interacting with you via voice to place their coffee order.
            
Your job is to:
1. Greet customers warmly and ask what they'd like to order
2. Collect all required order information: drink type, size, milk preference, and their name
3. Ask about optional extras like whipped cream, syrups, or extra shots
4. Confirm the complete order before finalizing
5. Be conversational, friendly, and helpful - like a real barista would be

Available drinks: Latte, Cappuccino, Espresso, Americano, Mocha, Macchiato, Flat White
Available sizes: Small, Medium, Large
Milk options: Whole milk, Skim milk, Oat milk, Almond milk, Soy milk, Coconut milk, No milk
Popular extras: Whipped cream, Extra shot, Vanilla syrup, Caramel syrup, Hazelnut syrup, Sugar, Honey

Your responses should be concise and natural, without complex formatting or emojis.
When you have all the required information (drink, size, milk, name), use the complete_order tool to save it.""",
        )
        self.order_state = OrderState()

    @function_tool
    async def complete_order(
        self, 
        context: RunContext,
        drink_type: str,
        size: str,
        milk: str,
        name: str,
        extras: str = ""
    ):
        """Use this tool when the customer has provided all required order information to finalize and save their order.
        
        Args:
            drink_type: The type of drink ordered (e.g., "Latte", "Cappuccino")
            size: The size of the drink (e.g., "Small", "Medium", "Large")
            milk: The milk preference (e.g., "Oat milk", "Whole milk")
            name: The customer's name for the order
            extras: Optional comma-separated list of extras (e.g., "whipped cream, vanilla syrup")
        """
        logger.info(f"Completing order: {drink_type}, {size}, {milk}, {name}, extras: {extras}")
        
        # Update order state
        self.order_state.drink_type = drink_type
        self.order_state.size = size
        self.order_state.milk = milk
        self.order_state.name = name
        
        if extras:
            self.order_state.extras = [e.strip() for e in extras.split(",") if e.strip()]
        
        # Save order to JSON file
        filepath = save_order(self.order_state)
        summary = format_order_summary(self.order_state)
        
        return f"Order saved successfully! {summary}. The order has been saved to {filepath}. Thank you and have a great day!"

    # To add tools, use the @function_tool decorator.
    # Here's an example that adds a simple weather tool.
    # You also have to add `from livekit.agents import function_tool, RunContext` to the top of this file
    # @function_tool
    # async def lookup_weather(self, context: RunContext, location: str):
    #     """Use this tool to look up current weather information in the given location.
    #
    #     If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.
    #
    #     Args:
    #         location: The location to look up weather information for (e.g. city name)
    #     """
    #
    #     logger.info(f"Looking up weather for {location}")
    #
    #     return "sunny with a temperature of 70 degrees."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="en-US-matthew", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
