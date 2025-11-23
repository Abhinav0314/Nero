"""
Coffee Shop Barista Agent - Day 2 Challenge
Handles order state management and saves completed orders to JSON files
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("barista")


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
