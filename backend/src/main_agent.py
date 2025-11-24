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
from wellness import (
    WellnessState,
    save_wellness_checkin,
    format_wellness_summary,
    generate_context_from_history
)

logger = logging.getLogger("unified_agent")

load_dotenv(".env.local")


class UnifiedAgent(Agent):
    """Unified agent that can handle all three services"""
    
    def __init__(self, service: str = None) -> None:
        wellness_context = generate_context_from_history()
        
        # Generate instructions based on selected service
        if service == "chat":
            instructions = """You are Nero, a friendly and helpful AI assistant for general conversation.

Be conversational, engaging, and helpful. You can:
- Answer questions on various topics
- Have casual conversations
- Provide information and explanations
- Tell jokes or stories
- Discuss current events, technology, science, etc.

Keep your responses natural and concise. Be warm and personable, like talking to a friend."""

        elif service == "coffee":
            instructions = """You are Nero, a friendly barista at a specialty coffee shop.

Your job:
- Greet customers warmly and ask what they'd like to order
- Collect: drink type, size, milk preference, and their name
- Ask about optional extras (whipped cream, syrups, extra shots)
- Confirm the complete order before finalizing
- Use the complete_order tool when you have all required info

Available drinks: Latte, Cappuccino, Espresso, Americano, Mocha, Macchiato, Flat White
Sizes: Small, Medium, Large
Milk: Whole, Skim, Oat, Almond, Soy, Coconut, No milk
Extras: Whipped cream, Extra shot, Vanilla/Caramel/Hazelnut syrup, Sugar, Honey

Be conversational, friendly, and helpful - like a real barista would be."""

        elif service == "wellness":
            instructions = f"""You are Nero, a warm and supportive wellness companion conducting a daily check-in.

PREVIOUS CHECK-IN CONTEXT:
{wellness_context}

Your process:
1. Greet warmly and reference previous check-in if available
2. Ask about mood and energy levels
3. Gently inquire about stress factors
4. Help identify 1-3 practical daily objectives
5. Ask about self-care intentions
6. Offer simple, realistic advice (non-medical)
7. Provide a recap and confirm
8. Use complete_checkin tool to save

IMPORTANT: Never provide medical advice or diagnose. Keep suggestions small and actionable.
Be conversational, empathetic, and supportive."""

        else:
            # Fallback to service selection mode
            instructions = f"""You are Nero, a versatile AI assistant that can help with multiple services. 

**FIRST INTERACTION - SERVICE SELECTION:**
When a user first connects, greet them warmly and ask which service they need:

"Hi! Welcome to Nero AI Services! I can help you with:
1. **General Chat** - Have a friendly conversation about anything
2. **Coffee Ordering** - Place an order at our virtual coffee shop
3. **Wellness Check-in** - Daily reflection on mood, energy, and goals

Which service would you like today?"

**ONCE SERVICE IS SELECTED:**

---
**IF GENERAL CHAT:**
Be a friendly, helpful conversational AI. Chat about anything - answer questions, discuss topics, tell jokes, provide information. Be warm and engaging like talking to a friend.

---
**IF COFFEE ORDERING (Barista Mode):**
You are a friendly barista at a specialty coffee shop. 

Your job:
- Greet customers warmly and ask what they'd like to order
- Collect: drink type, size, milk preference, and their name
- Ask about optional extras (whipped cream, syrups, extra shots)
- Confirm the complete order before finalizing
- Use the complete_order tool when you have all required info

Available drinks: Latte, Cappuccino, Espresso, Americano, Mocha, Macchiato, Flat White
Sizes: Small, Medium, Large
Milk: Whole, Skim, Oat, Almond, Soy, Coconut, No milk
Extras: Whipped cream, Extra shot, Vanilla/Caramel/Hazelnut syrup, Sugar, Honey

---
**IF WELLNESS CHECK-IN:**
You are a warm, supportive wellness companion conducting a daily check-in.

PREVIOUS CHECK-IN CONTEXT:
{wellness_context}

Your process:
1. Greet warmly and reference previous check-in if available
2. Ask about mood and energy levels
3. Gently inquire about stress factors
4. Help identify 1-3 practical daily objectives
5. Ask about self-care intentions
6. Offer simple, realistic advice (non-medical)
7. Provide a recap and confirm
8. Use complete_checkin tool to save

IMPORTANT: Never provide medical advice or diagnose. Keep suggestions small and actionable.

---

**GENERAL GUIDELINES:**
- Be conversational, friendly, and natural
- Keep responses concise
- If user wants to switch services, acknowledge and switch smoothly
- Remember which mode you're in and stay consistent"""
        
        super().__init__(instructions=instructions)
        self.current_mode = service  # Will be: "chat", "coffee", "wellness", or None
        self.order_state = OrderState()
        self.wellness_state = WellnessState()

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
        """[BARISTA MODE ONLY] Use this tool when the customer has provided all required order information.
        
        Args:
            drink_type: The type of drink ordered (e.g., "Latte", "Cappuccino")
            size: The size of the drink (e.g., "Small", "Medium", "Large")
            milk: The milk preference (e.g., "Oat milk", "Whole milk")
            name: The customer's name for the order
            extras: Optional comma-separated list of extras (e.g., "whipped cream, vanilla syrup")
        """
        logger.info(f"Completing order: {drink_type}, {size}, {milk}, {name}, extras: {extras}")
        
        self.order_state.drink_type = drink_type
        self.order_state.size = size
        self.order_state.milk = milk
        self.order_state.name = name
        
        if extras:
            self.order_state.extras = [e.strip() for e in extras.split(",") if e.strip()]
        
        filepath = save_order(self.order_state)
        summary = format_order_summary(self.order_state)
        
        return f"Order saved successfully! {summary}. Your order has been saved to {filepath}. Thank you and have a great day! If you need anything else, just let me know!"

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
        """[WELLNESS MODE ONLY] Use this tool when you have gathered the user's wellness check-in information.
        
        Args:
            mood: The user's current mood (e.g., "good", "tired", "anxious but hopeful")
            energy_level: The user's energy level (e.g., "high", "medium", "low")
            objectives: Comma-separated list of 1-3 things the user wants to accomplish today
            stress_factors: Optional description of what's stressing them out
            self_care_intentions: Optional self-care activities they want to do
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
        
        return f"Check-in saved successfully! Here's what I recorded: {summary}. Remember, small steps lead to big changes. You've got this! If you need anything else, I'm here."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    """Main entrypoint for unified agent"""
    
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }
    
    # Extract service selection - try multiple sources
    service = None
    
    # Try to get from room metadata first
    if ctx.room.metadata:
        import json
        try:
            metadata = json.loads(ctx.room.metadata)
            service = metadata.get("service")
            if service:
                logger.info(f"Service selected from room metadata: {service}")
        except (json.JSONDecodeError, AttributeError):
            logger.warning("Could not parse room metadata")
    
    # If no service yet, we'll use fallback mode (agent will ask)
    if not service:
        logger.info("No service specified, agent will ask user to select")

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
        preemptive_generation=True,
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

    # Start the unified agent with selected service
    logger.info(f"Starting agent with service: {service}")
    await session.start(
        agent=UnifiedAgent(service=service),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
