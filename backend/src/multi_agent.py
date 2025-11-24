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

logger = logging.getLogger("multi_agent")

load_dotenv(".env.local")


class RouterAgent(Agent):
    """Main router agent that directs users to different services"""
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly AI assistant receptionist for Nero - an AI service platform. 

Your job is to greet users warmly and help them choose which service they need:

**Available Services:**
1. **General Chat** - Just have a friendly conversation about anything
2. **Coffee Shop Barista** - Place a coffee order (latte, cappuccino, etc.)
3. **Wellness Companion** - Daily check-in for mood, energy, and setting intentions

**Your Process:**
1. Greet the user warmly: "Hi! Welcome to Nero AI Services. I'm here to help you today!"
2. Ask which service they'd like: "We have three services available:
   - General chat if you just want to talk
   - Coffee ordering if you'd like to place a coffee order
   - Wellness check-in for your daily reflection
   
   Which would you like to use today?"
3. Once they choose, use the route_to_service tool to direct them

Be friendly, concise, and helpful. If they're unsure, briefly explain each service.""",
        )
        self.selected_service = None

    @function_tool
    async def route_to_service(
        self, 
        context: RunContext,
        service: str
    ):
        """Route the user to the selected service.
        
        Args:
            service: The service to route to. Must be one of: "chat", "barista", "wellness"
        """
        service = service.lower().strip()
        
        if service not in ["chat", "barista", "wellness"]:
            return "I'm sorry, that's not a valid service. Please choose 'chat', 'barista', or 'wellness'."
        
        self.selected_service = service
        logger.info(f"Routing user to service: {service}")
        
        if service == "chat":
            return "Great! Switching you to our general chat assistant. One moment..."
        elif service == "barista":
            return "Perfect! Connecting you to our coffee shop barista. Get ready to order!"
        elif service == "wellness":
            return "Wonderful! Connecting you to your wellness companion. Let's check in on how you're doing."


class GeneralChatAgent(Agent):
    """Day 1 - General conversation agent"""
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly, helpful AI assistant. You can chat about anything the user wants to discuss.

Be conversational, engaging, and helpful. You can:
- Answer questions on various topics
- Have casual conversations
- Provide information and explanations
- Tell jokes or stories
- Discuss current events, technology, science, etc.

Keep your responses natural and concise. Be warm and personable, like talking to a friend.""",
        )


class BaristaAgent(Agent):
    """Day 2 - Coffee shop barista agent"""
    
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
        
        self.order_state.drink_type = drink_type
        self.order_state.size = size
        self.order_state.milk = milk
        self.order_state.name = name
        
        if extras:
            self.order_state.extras = [e.strip() for e in extras.split(",") if e.strip()]
        
        filepath = save_order(self.order_state)
        summary = format_order_summary(self.order_state)
        
        return f"Order saved successfully! {summary}. The order has been saved to {filepath}. Thank you and have a great day!"


class WellnessAgent(Agent):
    """Day 3 - Wellness companion agent"""
    
    def __init__(self) -> None:
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


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    """Main entrypoint with agent routing"""
    
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Start with router agent
    router = RouterAgent()
    
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

    # Start with router agent
    await session.start(
        agent=router,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()
    
    # Wait for service selection
    logger.info("Waiting for user to select a service...")
    
    # Monitor for service selection
    while router.selected_service is None:
        await ctx.room.wait_for_participant()
        if router.selected_service:
            break
    
    # Switch to the selected agent
    if router.selected_service == "chat":
        logger.info("Switching to General Chat Agent")
        await session.update_agent(GeneralChatAgent())
    elif router.selected_service == "barista":
        logger.info("Switching to Barista Agent")
        await session.update_agent(BaristaAgent())
    elif router.selected_service == "wellness":
        logger.info("Switching to Wellness Agent")
        await session.update_agent(WellnessAgent())


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
