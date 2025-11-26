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

logger = logging.getLogger("sdr_service")

class LeadState:
    """Manages the state of a lead/prospect"""
    
    def __init__(self):
        self.name: Optional[str] = None
        self.company: Optional[str] = None
        self.email: Optional[str] = None
        self.role: Optional[str] = None
        self.use_case: Optional[str] = None
        self.team_size: Optional[str] = None
        self.timeline: Optional[str] = None
        self.questions_asked: List[str] = []
        self.answers_provided: List[str] = []
    
    def to_dict(self) -> Dict:
        """Convert lead state to dictionary"""
        return {
            "name": self.name,
            "company": self.company,
            "email": self.email,
            "role": self.role,
            "useCase": self.use_case,
            "teamSize": self.team_size,
            "timeline": self.timeline,
            "questionsAsked": self.questions_asked,
            "answersProvided": self.answers_provided
        }
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return all([
            self.name,
            self.company,
            self.email,
            self.role,
            self.use_case
        ])
    
    def get_missing_fields(self) -> List[str]:
        """Return list of missing required fields"""
        missing = []
        if not self.name:
            missing.append("name")
        if not self.company:
            missing.append("company")
        if not self.email:
            missing.append("email")
        if not self.role:
            missing.append("role")
        if not self.use_case:
            missing.append("use case")
        return missing


def load_faq_data(faq_file: str = "wipro_faq.json") -> Dict:
    """Load FAQ data from JSON file"""
    try:
        faq_path = Path(faq_file)
        with open(faq_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"FAQ file not found: {faq_file}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing FAQ JSON: {e}")
        return {}


def search_faq(query: str, faq_data: Dict) -> Optional[str]:
    """
    Simple keyword-based FAQ search.
    Returns the most relevant answer or None if no match found.
    """
    query_lower = query.lower()
    
    # Search through FAQs
    if "faqs" in faq_data:
        for faq in faq_data["faqs"]:
            question = faq.get("question", "").lower()
            answer = faq.get("answer", "")
            
            # Simple keyword matching
            if any(word in question for word in query_lower.split() if len(word) > 3):
                return answer
    
    return None


def save_lead(lead_state: LeadState, output_dir: str = "leads") -> str:
    """
    Save the collected lead information to a JSON file.
    Returns the path to the saved file.
    """
    # Create leads directory if it doesn't exist
    leads_path = Path(output_dir)
    leads_path.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"lead_{timestamp}.json"
    filepath = leads_path / filename
    
    # Save lead to JSON
    lead_data = lead_state.to_dict()
    lead_data["timestamp"] = datetime.now().isoformat()
    lead_data["source"] = "Voice SDR Agent"
    
    with open(filepath, "w") as f:
        json.dump(lead_data, f, indent=2)
    
    logger.info(f"Lead saved to {filepath}")
    return str(filepath)


def format_lead_summary(lead_state: LeadState) -> str:
    """Generate a human-readable summary of the lead"""
    summary_parts = []
    
    if lead_state.name:
        summary_parts.append(f"{lead_state.name}")
    if lead_state.role and lead_state.company:
        summary_parts.append(f"{lead_state.role} at {lead_state.company}")
    elif lead_state.company:
        summary_parts.append(f"from {lead_state.company}")
    
    if lead_state.use_case:
        summary_parts.append(f"interested in {lead_state.use_case}")
    
    if lead_state.team_size:
        summary_parts.append(f"with a team of {lead_state.team_size}")
    
    if lead_state.timeline:
        summary_parts.append(f"looking to start {lead_state.timeline}")
    
    return ", ".join(summary_parts) if summary_parts else "prospect"


class SDRAgent(Agent):
    """Day 5 - Sales Development Representative agent for Wipro"""
    
    def __init__(self, faq_data: Dict) -> None:
        # Create FAQ context from the data
        faq_context = self._build_faq_context(faq_data)
        
        super().__init__(
            instructions=f"""You are a friendly and professional Sales Development Representative (SDR) for Wipro Limited, a leading global IT services and consulting company.

IMPORTANT: When the user first connects, greet them warmly with something like "Hi! Welcome to Wipro. I'm here to help you learn about our services and understand how we can support your business. What brings you here today?"

Your role is to:
1. Greet visitors warmly and ask what brought them here
2. Answer questions about Wipro's services, capabilities, and offerings using the FAQ knowledge below
3. Understand the visitor's business needs and challenges
4. Naturally collect lead information during the conversation: name, company, email, role, use case, team size, and timeline
5. Qualify the lead by understanding their requirements and timeline
6. Provide a summary at the end and thank them for their time

WIPRO KNOWLEDGE BASE:
{faq_context}

CONVERSATION GUIDELINES:
- Be conversational and consultative, not pushy
- Ask open-ended questions to understand their needs
- When they ask about services, pricing, or capabilities, refer to the knowledge base above
- Naturally weave in questions to collect lead information (don't make it feel like an interrogation)
- If they ask something not in the knowledge base, acknowledge it and offer to have someone follow up
- Keep responses concise and natural for voice conversation
- When you have collected the key lead information (name, company, email, role, use case), use the save_lead tool

Remember: You're here to help and qualify, not just to collect information. Build rapport first.""",
        )
        self.lead_state = LeadState()
        self.faq_data = faq_data
    
    def _build_faq_context(self, faq_data: Dict) -> str:
        """Build a formatted FAQ context string for the agent"""
        context_parts = []
        
        # Company overview
        if "company" in faq_data:
            company = faq_data["company"]
            context_parts.append(f"COMPANY: {company.get('name', 'Wipro')}")
            context_parts.append(f"Overview: {company.get('overview', '')}")
            context_parts.append(f"Tagline: {company.get('tagline', '')}")
            context_parts.append("")
        
        # Services
        if "services" in faq_data:
            context_parts.append("SERVICES:")
            for service in faq_data["services"]:
                context_parts.append(f"- {service.get('category', '')}: {service.get('description', '')}")
            context_parts.append("")
        
        # FAQs
        if "faqs" in faq_data:
            context_parts.append("COMMON QUESTIONS & ANSWERS:")
            for faq in faq_data["faqs"]:
                context_parts.append(f"Q: {faq.get('question', '')}")
                context_parts.append(f"A: {faq.get('answer', '')}")
                context_parts.append("")
        
        return "\n".join(context_parts)

    @function_tool
    async def save_lead(
        self, 
        context: RunContext,
        name: str,
        company: str,
        email: str,
        role: str,
        use_case: str,
        team_size: str = "",
        timeline: str = ""
    ):
        """Use this tool when you have collected the key lead information to save it.
        
        Args:
            name: The prospect's full name
            company: The company they work for
            email: Their business email address
            role: Their job title/role
            use_case: What they want to use Wipro's services for
            team_size: Size of their team (optional)
            timeline: When they're looking to start (optional, e.g., "now", "next quarter", "6 months")
        """
        logger.info(f"Saving lead: {name} from {company}")
        
        self.lead_state.name = name
        self.lead_state.company = company
        self.lead_state.email = email
        self.lead_state.role = role
        self.lead_state.use_case = use_case
        self.lead_state.team_size = team_size if team_size else "Not specified"
        self.lead_state.timeline = timeline if timeline else "Not specified"
        
        filepath = save_lead(self.lead_state)
        summary = format_lead_summary(self.lead_state)
        
        return f"""Perfect! I've captured all your information. Let me summarize: {summary}. 

Your details have been saved and someone from our team will reach out to you at {email} within 24 hours to discuss how Wipro can help with {use_case}. 

Thank you so much for your time today! Is there anything else you'd like to know before we wrap up?"""


async def entrypoint(ctx: JobContext):
    logger.info("Starting SDR Service")
    
    # Load FAQ data during initialization
    faq_data = load_faq_data()
    if not faq_data:
        logger.warning("FAQ data not loaded, agent will have limited knowledge")
    
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
        agent=SDRAgent(faq_data),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
