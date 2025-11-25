import json
import logging
import asyncio
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable
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

logger = logging.getLogger("tutor_service")

# --- Tutor State and Utils ---

# Path to tutor content
CONTENT_FILE = Path(__file__).parent.parent / "tutor_content.json"
SESSIONS_DIR = Path(__file__).parent.parent / "tutor_sessions"

# Ensure sessions directory exists
SESSIONS_DIR.mkdir(exist_ok=True)


@dataclass
class TutorSession:
    """Tracks a single tutoring session"""
    timestamp: str = ""
    mode: str = ""  # learn, quiz, or teach_back
    concept_id: str = ""
    concept_title: str = ""
    user_response: str = ""
    feedback: str = ""
    score: Optional[int] = None  # 0-100 for teach_back mode
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class TutorState:
    """Manages the state of the tutoring system"""
    current_mode: str = ""  # learn, quiz, teach_back
    current_concept_id: str = ""
    sessions: List[TutorSession] = field(default_factory=list)
    
    def add_session(self, session: TutorSession):
        """Add a session to history"""
        self.sessions.append(session)
    
    def get_concept_history(self, concept_id: str) -> List[TutorSession]:
        """Get all sessions for a specific concept"""
        return [s for s in self.sessions if s.concept_id == concept_id]


def load_tutor_content() -> List[Dict]:
    """Load the tutor content from JSON file"""
    try:
        with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
            content = json.load(f)
        logger.info(f"Loaded {len(content)} concepts from tutor content")
        return content
    except Exception as e:
        logger.error(f"Error loading tutor content: {e}")
        return []


def get_concept_by_id(concept_id: str) -> Optional[Dict]:
    """Get a specific concept by ID"""
    content = load_tutor_content()
    for concept in content:
        if concept.get("id") == concept_id:
            return concept
    return None


def get_all_concept_ids() -> List[str]:
    """Get list of all available concept IDs"""
    content = load_tutor_content()
    return [c.get("id") for c in content if c.get("id")]


def get_all_concept_titles() -> List[str]:
    """Get list of all available concept titles"""
    content = load_tutor_content()
    return [c.get("title") for c in content if c.get("title")]


def save_tutor_session(session: TutorSession) -> str:
    """Save a tutoring session to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"session_{session.mode}_{session.concept_id}_{timestamp}.json"
    filepath = SESSIONS_DIR / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(session), f, indent=2)
        logger.info(f"Saved tutor session to {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Error saving tutor session: {e}")
        return ""


def format_session_summary(session: TutorSession) -> str:
    """Format a session summary for display"""
    summary = f"Mode: {session.mode.title()}, Concept: {session.concept_title}"
    
    if session.score is not None:
        summary += f", Score: {session.score}/100"
    
    if session.feedback:
        summary += f". Feedback: {session.feedback}"
    
    return summary


def generate_learn_prompt(concept: Dict) -> str:
    """Generate instruction text for learn mode"""
    return f"""You are teaching the concept of '{concept['title']}'. 

Here's what you need to explain:
{concept['summary']}

Explain this concept clearly and engagingly. Use examples and analogies to make it easy to understand. 
Keep your explanation conversational and check if the user has any questions before moving on."""


def generate_quiz_prompt(concept: Dict) -> str:
    """Generate instruction text for quiz mode"""
    return f"""You are quizzing the user on '{concept['title']}'.

Concept summary:
{concept['summary']}

Sample question: {concept['sample_question']}

Ask the user questions about this concept. You can use the sample question or create your own based on the summary.
Listen to their answer, provide feedback on whether it's correct, and explain any misconceptions.
Be encouraging and educational."""


def generate_teach_back_prompt(concept: Dict) -> str:
    """Generate instruction text for teach-back mode"""
    return f"""You are asking the user to teach YOU about '{concept['title']}'.

Here's what they should explain:
{concept['summary']}

Ask them to explain the concept back to you as if they're teaching it. Listen carefully to their explanation.
When they're done, use the evaluate_explanation tool to score their explanation and provide constructive feedback.

Be supportive and encouraging. If they miss key points, gently guide them to think about those aspects."""


def evaluate_explanation(concept_summary: str, user_explanation: str) -> Dict[str, any]:
    """
    Evaluate a user's explanation against the concept summary.
    This is a simple heuristic-based evaluation.
    
    Returns:
        dict with 'score' (0-100) and 'feedback' (string)
    """
    # Simple keyword-based evaluation
    # In a real system, you might use an LLM to evaluate
    
    concept_keywords = set(concept_summary.lower().split())
    user_keywords = set(user_explanation.lower().split())
    
    # Calculate overlap
    common_keywords = concept_keywords.intersection(user_keywords)
    coverage = len(common_keywords) / len(concept_keywords) if concept_keywords else 0
    
    # Base score on coverage
    score = int(coverage * 100)
    
    # Adjust score based on length (too short = incomplete)
    if len(user_explanation.split()) < 20:
        score = max(0, score - 20)
    
    # Generate feedback
    if score >= 80:
        feedback = "Excellent explanation! You covered the key concepts very well."
    elif score >= 60:
        feedback = "Good effort! You got the main ideas, but could add more detail on some aspects."
    elif score >= 40:
        feedback = "You're on the right track, but your explanation is missing some important points."
    else:
        feedback = "Your explanation needs more detail. Try to cover the core concepts more thoroughly."
    
    return {
        "score": score,
        "feedback": feedback
    }

# --- Tutor Agents ---

class TutorRouterAgent(Agent):
    """Router agent that greets users and directs them to learning modes"""
    
    def __init__(self) -> None:
        # Load available concepts
        concepts = load_tutor_content()
        concept_list = "\n".join([f"- {c['title']}" for c in concepts])
        
        super().__init__(
            instructions=f"""You are a friendly AI tutor assistant. Your job is to help users learn programming concepts through active recall.

IMPORTANT: When the user first connects, immediately greet them with: "Hi! Welcome to the Active Recall Coach. I'm here to help you learn programming concepts!"

**Available Concepts:**
{concept_list}

**Three Learning Modes:**
1. **Learn Mode** - I'll explain a concept to you in detail
2. **Quiz Mode** - I'll ask you questions to test your understanding
3. **Teach-Back Mode** - You explain the concept back to me, and I'll give you feedback

**Your Process:**
1. Greet the user warmly as instructed above
2. Ask which learning mode they'd like to use
3. Ask which concept they want to work on
4. Once they choose both, use the route_to_mode tool to direct them

Be encouraging, supportive, and enthusiastic about learning. If they're unsure, explain each mode briefly.""",
        )
        self.selected_mode = None
        self.selected_concept = None

    async def on_user_transcript(self, transcript: str):
        logger.info(f"Tutor User transcript received: {transcript}")
        
    async def on_agent_speech(self, speech: str):
        logger.info(f"Tutor Agent speech generated: {speech}")

    @function_tool
    async def route_to_mode(
        self, 
        context: RunContext,
        mode: str,
        concept: str
    ):
        """Route the user to the selected learning mode and concept.
        
        Args:
            mode: The learning mode. Must be one of: "learn", "quiz", "teach_back"
            concept: The concept ID or title to work on (e.g., "variables", "loops", "functions")
        """
        mode = mode.lower().strip()
        concept = concept.lower().strip()
        
        if mode not in ["learn", "quiz", "teach_back"]:
            return "I'm sorry, that's not a valid mode. Please choose 'learn', 'quiz', or 'teach_back'."
        
        # Find the concept
        concepts = load_tutor_content()
        found_concept = None
        for c in concepts:
            if c['id'] == concept or c['title'].lower() == concept:
                found_concept = c
                break
        
        if not found_concept:
            available = ", ".join([c['title'] for c in concepts])
            return f"I couldn't find that concept. Available concepts are: {available}"
        
        self.selected_mode = mode
        self.selected_concept = found_concept['id']
        logger.info(f"Routing to mode: {mode}, concept: {found_concept['title']}")
        
        if mode == "learn":
            return f"Great! Let me teach you about {found_concept['title']}. Switching to Learn Mode..."
        elif mode == "quiz":
            return f"Perfect! Let's test your knowledge of {found_concept['title']}. Switching to Quiz Mode..."
        elif mode == "teach_back":
            return f"Excellent! I'm ready to learn about {found_concept['title']} from you. Switching to Teach-Back Mode..."


class LearnModeAgent(Agent):
    """Agent that explains concepts - uses Matthew voice"""
    
    def __init__(self, concept_id: str, on_switch: Optional[Callable] = None) -> None:
        concept = get_concept_by_id(concept_id)
        if not concept:
            raise ValueError(f"Concept {concept_id} not found")
        
        self.concept = concept
        self.tutor_state = TutorState(current_mode="learn", current_concept_id=concept_id)
        self.on_switch = on_switch
        
        instructions = generate_learn_prompt(concept)
        
        super().__init__(
            instructions=f"""{instructions}

After explaining, ask if they have any questions. If they want to switch modes or concepts, 
acknowledge their request and let them know they can ask to switch at any time.

Be patient, clear, and encouraging. Use examples and analogies to make concepts memorable.""",
        )

    @function_tool
    async def complete_learning_session(
        self,
        context: RunContext,
        user_feedback: str = ""
    ):
        """Complete the learning session and save it.
        
        Args:
            user_feedback: Optional feedback from the user about the explanation
        """
        session = TutorSession(
            mode="learn",
            concept_id=self.concept['id'],
            concept_title=self.concept['title'],
            user_response=user_feedback,
            feedback="Concept explained successfully"
        )
        
        filepath = save_tutor_session(session)
        self.tutor_state.add_session(session)
        
        return f"Great! I've recorded that we covered {self.concept['title']}. Would you like to quiz yourself on this concept, or learn something else?"

    @function_tool
    async def switch_learning_mode(self, context: RunContext, mode: str, concept: str = ""):
        """Switch to a different learning mode (learn, quiz, or teach_back).
        
        Args:
            mode: The learning mode to switch to (learn, quiz, teach_back)
            concept: Optional concept to switch to. If not provided, stays on current concept.
        """
        if self.on_switch:
            target_concept = concept if concept else self.concept['id']
            self.on_switch(mode, target_concept)
            return f"Switching to {mode} mode..."
        return "Switching modes is not available in this session."


class QuizModeAgent(Agent):
    """Agent that quizzes users - uses Alicia voice"""
    
    def __init__(self, concept_id: str, on_switch: Optional[Callable] = None) -> None:
        concept = get_concept_by_id(concept_id)
        if not concept:
            raise ValueError(f"Concept {concept_id} not found")
        
        self.concept = concept
        self.tutor_state = TutorState(current_mode="quiz", current_concept_id=concept_id)
        self.on_switch = on_switch
        
        instructions = generate_quiz_prompt(concept)
        
        super().__init__(
            instructions=f"""{instructions}

After they answer, provide immediate feedback. If correct, praise them and maybe ask a follow-up.
If incorrect, gently explain the right answer and why.

Keep the quiz engaging and educational. You can ask multiple questions if they want to continue.
When done, use the complete_quiz_session tool to save the session.""",
        )

    @function_tool
    async def complete_quiz_session(
        self,
        context: RunContext,
        user_answers: str,
        performance_summary: str
    ):
        """Complete the quiz session and save it.
        
        Args:
            user_answers: Summary of the user's answers
            performance_summary: Brief summary of how well they did
        """
        session = TutorSession(
            mode="quiz",
            concept_id=self.concept['id'],
            concept_title=self.concept['title'],
            user_response=user_answers,
            feedback=performance_summary
        )
        
        filepath = save_tutor_session(session)
        self.tutor_state.add_session(session)
        
        return f"Quiz complete! {performance_summary}. Would you like to try teaching this concept back to me, or work on something else?"

    @function_tool
    async def switch_learning_mode(self, context: RunContext, mode: str, concept: str = ""):
        """Switch to a different learning mode (learn, quiz, or teach_back).
        
        Args:
            mode: The learning mode to switch to (learn, quiz, teach_back)
            concept: Optional concept to switch to. If not provided, stays on current concept.
        """
        if self.on_switch:
            target_concept = concept if concept else self.concept['id']
            self.on_switch(mode, target_concept)
            return f"Switching to {mode} mode..."
        return "Switching modes is not available in this session."


class TeachBackModeAgent(Agent):
    """Agent that learns from the user - uses Ken voice"""
    
    def __init__(self, concept_id: str, on_switch: Optional[Callable] = None) -> None:
        concept = get_concept_by_id(concept_id)
        if not concept:
            raise ValueError(f"Concept {concept_id} not found")
        
        self.concept = concept
        self.tutor_state = TutorState(current_mode="teach_back", current_concept_id=concept_id)
        self.on_switch = on_switch
        
        instructions = generate_teach_back_prompt(concept)
        
        super().__init__(
            instructions=f"""{instructions}

Be an engaged student. Ask clarifying questions if their explanation is unclear.
When they finish explaining, use the evaluate_explanation tool to score them and provide feedback.

Be supportive and constructive. Highlight what they did well and gently point out what they could improve.""",
        )

    @function_tool
    async def evaluate_user_explanation(
        self,
        context: RunContext,
        user_explanation: str
    ):
        """Evaluate the user's explanation and provide feedback.
        
        Args:
            user_explanation: The user's complete explanation of the concept
        """
        # Evaluate the explanation
        evaluation = evaluate_explanation(self.concept['summary'], user_explanation)
        
        score = evaluation['score']
        feedback = evaluation['feedback']
        
        # Save the session
        session = TutorSession(
            mode="teach_back",
            concept_id=self.concept['id'],
            concept_title=self.concept['title'],
            user_response=user_explanation,
            feedback=feedback,
            score=score
        )
        
        filepath = save_tutor_session(session)
        self.tutor_state.add_session(session)
        
        # Provide detailed feedback
        result = f"Thank you for teaching me about {self.concept['title']}! "
        result += f"I'd give your explanation a score of {score} out of 100. "
        result += feedback
        
        if score >= 80:
            result += " You clearly understand this concept well!"
        elif score >= 60:
            result += " You're getting there - maybe review the material once more."
        else:
            result += " I think reviewing this concept in Learn mode might help solidify your understanding."
        
        return result

    @function_tool
    async def switch_learning_mode(self, context: RunContext, mode: str, concept: str = ""):
        """Switch to a different learning mode (learn, quiz, or teach_back).
        
        Args:
            mode: The learning mode to switch to (learn, quiz, teach_back)
            concept: Optional concept to switch to. If not provided, stays on current concept.
        """
        if self.on_switch:
            target_concept = concept if concept else self.concept['id']
            self.on_switch(mode, target_concept)
            return f"Switching to {mode} mode..."
        return "Switching modes is not available in this session."


# --- Entrypoint ---

async def entrypoint(ctx: JobContext):
    """Main entrypoint for Tutor service"""
    
    logger.info("Starting Tutor Service")
    
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
        preemptive_generation=False,  # Disabled for reliable greeting
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

    # Start with router agent - it will greet immediately
    router = TutorRouterAgent()
    
    await session.start(
        agent=router,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    logger.info("Tutor router agent started, waiting for mode selection through conversation...")
    
    # Note: The router agent will use the route_to_mode tool when user selects mode
    # We don't block here - the agent handles everything through conversation
    # The advanced multi-mode switching is currently simplified for stability
    # Future enhancement: Add dynamic agent switching based on router.selected_mode
