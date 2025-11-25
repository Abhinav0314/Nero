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

logger = logging.getLogger("barista_service")

class OrderState:
    """Manages the state of a coffee order"""
    
    def __init__(self):
        self.drink_type: Optional[str] = None
        self.size: Optional[str] = None
        self.milk: Optional[str] = None
        self.extras: List[str] = []
        self.name: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert order state to dictionary"""
        return {
            "drinkType": self.drink_type,
            "size": self.size,
            "milk": self.milk,
            "extras": self.extras,
            "name": self.name
        }
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return all([
            self.drink_type,
            self.size,
            self.milk,
            self.name
        ])
    
    def get_missing_fields(self) -> List[str]:
        """Return list of missing required fields"""
        missing = []
        if not self.drink_type:
            missing.append("drink type")
        if not self.size:
            missing.append("size")
        if not self.milk:
            missing.append("milk preference")
        if not self.name:
            missing.append("name")
        return missing
    
    def update_from_text(self, text: str) -> List[str]:
        """
        Parse text and update order fields.
        Returns list of fields that were updated.
        """
        text_lower = text.lower()
        updated = []
        
        # Detect drink types
        drinks = ["latte", "cappuccino", "espresso", "americano", "mocha", "macchiato", "flat white"]
        for drink in drinks:
            if drink in text_lower:
                self.drink_type = drink.title()
                updated.append("drink_type")
                break
        
        # Detect sizes
        if "small" in text_lower or "tall" in text_lower:
            self.size = "small"
            updated.append("size")
        elif "medium" in text_lower or "grande" in text_lower:
            self.size = "medium"
            updated.append("size")
        elif "large" in text_lower or "venti" in text_lower:
            self.size = "large"
            updated.append("size")
        
        # Detect milk options
        milk_options = {
            "whole": "whole milk",
            "skim": "skim milk",
            "oat": "oat milk",
            "almond": "almond milk",
            "soy": "soy milk",
            "coconut": "coconut milk",
            "no milk": "no milk"
        }
        for key, value in milk_options.items():
            if key in text_lower:
                self.milk = value
                updated.append("milk")
                break
        
        # Detect extras
        extras_keywords = {
            "whipped cream": "whipped cream",
            "extra shot": "extra shot",
            "vanilla": "vanilla syrup",
            "caramel": "caramel syrup",
            "hazelnut": "hazelnut syrup",
            "sugar": "sugar",
            "honey": "honey"
        }
        for keyword, extra_name in extras_keywords.items():
            if keyword in text_lower and extra_name not in self.extras:
                self.extras.append(extra_name)
                updated.append("extras")
        
        return updated


def save_order(order_state: OrderState, output_dir: str = "orders") -> str:
    """
    Save the completed order to a JSON file.
    Returns the path to the saved file.
    """
    # Create orders directory if it doesn't exist
    orders_path = Path(output_dir)
    orders_path.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"order_{timestamp}.json"
    filepath = orders_path / filename
    
    # Save order to JSON
    order_data = order_state.to_dict()
    order_data["timestamp"] = datetime.now().isoformat()
    
    with open(filepath, "w") as f:
        json.dump(order_data, f, indent=2)
    
    logger.info(f"Order saved to {filepath}")
    return str(filepath)


def format_order_summary(order_state: OrderState) -> str:
    """Generate a human-readable summary of the order"""
    summary_parts = []
    
    if order_state.size:
        summary_parts.append(order_state.size)
    if order_state.drink_type:
        summary_parts.append(order_state.drink_type)
    if order_state.milk:
        summary_parts.append(f"with {order_state.milk}")
    if order_state.extras:
        extras_str = ", ".join(order_state.extras)
        summary_parts.append(f"and {extras_str}")
    
    summary = " ".join(summary_parts)
    
    if order_state.name:
        summary = f"{summary} for {order_state.name}"
    
    return summary

class BaristaAgent(Agent):
    """Day 2 - Coffee shop barista agent"""
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly barista at a specialty coffee shop. The user is interacting with you via voice to place their coffee order.

IMPORTANT: When the user first connects, greet them warmly with something like "Hi! Welcome to our coffee shop. What can I get started for you today?"
            
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

async def entrypoint(ctx: JobContext):
    logger.info("Starting Barista Service")
    
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
        agent=BaristaAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
