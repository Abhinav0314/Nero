"""
Health & Wellness Voice Companion - Day 3 Challenge
Handles wellness check-in state management and saves sessions to JSON files
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("wellness")


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
