import json
import os
import logging
from typing import List, Dict, Any
from datetime import datetime
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

logger = logging.getLogger("grocery_service")

# Define the recipe mapping for "ingredients for X" logic
RECIPES = {
    "peanut butter sandwich": ["Whole Wheat Bread", "Peanut Butter", "Strawberry Jam"],
    "pasta": ["Spaghetti Pasta", "Tomato Basil Sauce", "Cheddar Cheese"],
    "breakfast": ["Whole Wheat Bread", "Free-Range Eggs (Dozen)", "Organic Milk"],
    "snack time": ["Potato Chips", "Chocolate Chip Cookies"]
}

class GroceryAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You are a friendly and helpful Grocery Assistant for 'FreshMart'.
            
IMPORTANT: When the user first connects, greet them warmly with something like "Hi! Welcome to FreshMart, your friendly neighborhood grocery store. What can I help you find today?"
            
Your goal is to help users order groceries, snacks, and prepared foods.
            
Capabilities:
- You can add items to the cart, remove them, and check the cart status.
- You can intelligently add multiple items if the user asks for ingredients for a specific dish (e.g., "ingredients for a sandwich").
- You should always confirm what you've added or removed.
- If a user asks for something vague like "milk", ask if they want "Organic Milk" or check if there are other options.
- When the user is ready, use the place_order tool to finalize the purchase.
            
Tone:
- Cheerful, efficient, and polite.
- If you don't find an item, apologize and suggest something similar if possible.
- Keep your responses concise and natural, without complex formatting or emojis.
"""
        )
        self.catalog = self._load_catalog()
        self.cart: Dict[str, Dict[str, Any]] = {} # item_name -> {quantity, price, item_details}

    def _load_catalog(self) -> List[Dict[str, Any]]:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            catalog_path = os.path.join(base_dir, "grocery_catalog.json")
            
            with open(catalog_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading catalog: {e}")
            return []

    def _find_item(self, item_name: str):
        item_name_lower = item_name.lower()
        for item in self.catalog:
            if item["name"].lower() == item_name_lower:
                return item
            if item_name_lower in item["name"].lower():
                return item
        return None

    @function_tool
    async def add_to_cart(
        self, 
        context: RunContext,
        item_name: str,
        quantity: int = 1
    ) -> str:
        """Add an item to the grocery cart.
        
        Args:
            item_name: The name of the item to add
            quantity: The quantity to add (default 1)
        """
        item = self._find_item(item_name)
        if not item:
            return f"Sorry, I couldn't find '{item_name}' in our catalog."
        
        real_name = item["name"]
        if real_name in self.cart:
            self.cart[real_name]["quantity"] += quantity
        else:
            self.cart[real_name] = {
                "quantity": quantity,
                "price": item["price"],
                "details": item
            }
        
        return f"Added {quantity} x {real_name} to your cart."

    @function_tool
    async def remove_from_cart(
        self, 
        context: RunContext,
        item_name: str
    ) -> str:
        """Remove an item from the grocery cart.
        
        Args:
            item_name: The name of the item to remove
        """
        target_key = None
        for key in self.cart.keys():
            if item_name.lower() in key.lower():
                target_key = key
                break
        
        if target_key:
            del self.cart[target_key]
            return f"Removed {target_key} from your cart."
        else:
            return f"Item '{item_name}' is not in your cart."

    @function_tool
    async def view_cart(self, context: RunContext) -> str:
        """View the current contents of the cart."""
        if not self.cart:
            return "Your cart is currently empty."
        
        summary = "Here is what's in your cart:\n"
        total = 0.0
        for name, data in self.cart.items():
            qty = data["quantity"]
            price = data["price"]
            subtotal = qty * price
            total += subtotal
            summary += f"- {name} (x{qty}): ${subtotal:.2f}\n"
        
        summary += f"\nTotal: ${total:.2f}"
        return summary

    @function_tool
    async def add_ingredients_for_dish(
        self, 
        context: RunContext,
        dish_name: str
    ) -> str:
        """Add ingredients for a specific dish or meal to the cart.
        
        Args:
            dish_name: The name of the dish (e.g., 'peanut butter sandwich', 'pasta')
        """
        dish_key = None
        for key in RECIPES.keys():
            if key in dish_name.lower():
                dish_key = key
                break
        
        if not dish_key:
            return f"I don't have a recipe for '{dish_name}' yet. I can help with 'peanut butter sandwich', 'pasta', 'breakfast', or 'snack time'."
        
        ingredients = RECIPES[dish_key]
        added_items = []
        for ing in ingredients:
            await self.add_to_cart(context, ing, 1)
            added_items.append(ing)
        
        return f"I've added the ingredients for {dish_key} to your cart: {', '.join(added_items)}."

    @function_tool
    async def place_order(self, context: RunContext) -> str:
        """Place the order and save it."""
        if not self.cart:
            return "Your cart is empty. I can't place an empty order."
        
        order_id = f"ORD-{int(datetime.now().timestamp())}"
        total = sum(item["quantity"] * item["price"] for item in self.cart.values())
        
        order_data = {
            "order_id": order_id,
            "timestamp": datetime.now().isoformat(),
            "items": [
                {
                    "name": name,
                    "quantity": data["quantity"],
                    "price": data["price"],
                    "subtotal": data["quantity"] * data["price"]
                }
                for name, data in self.cart.items()
            ],
            "total_amount": total,
            "status": "received"
        }
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        orders_dir = os.path.join(base_dir, "orders")
        os.makedirs(orders_dir, exist_ok=True)
        
        order_file = os.path.join(orders_dir, f"{order_id}.json")
        with open(order_file, "w") as f:
            json.dump(order_data, f, indent=2)
            
        self.cart = {}
        
        return f"Order placed successfully! Your Order ID is {order_id}. The total was ${total:.2f}."

async def entrypoint(ctx: JobContext):
    logger.info("Starting Grocery Service")
    
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
        agent=GroceryAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
