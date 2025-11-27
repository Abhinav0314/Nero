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

logger = logging.getLogger("fraud_service")

class FraudState:
    """Manages the state of a fraud investigation session"""
    
    def __init__(self):
        self.username: Optional[str] = None
        self.case_data: Optional[Dict] = None
        self.is_verified: bool = False
        self.user_response: Optional[str] = None
        self.status: Optional[str] = None
        self.verification_complete: bool = False

    def to_dict(self):
        """Convert fraud state to dictionary"""
        return {
            "username": self.username,
            "case_data": self.case_data,
            "is_verified": self.is_verified,
            "user_response": self.user_response,
            "status": self.status,
            "verification_complete": self.verification_complete
        }

    def is_complete(self):
        """Check if investigation is complete"""
        return self.verification_complete and self.status is not None


def load_fraud_cases(cases_file: str = "fraud_cases.json") -> Dict:
    """
    Load fraud cases from JSON file.
    Returns empty dict if file doesn't exist.
    """
    cases_path = Path(cases_file)
    
    if cases_path.exists():
        try:
            with open(cases_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing fraud cases JSON: {e}")
            return {"users": []}
        except Exception as e:
            logger.error(f"Error loading fraud cases: {e}")
            return {"users": []}
    else:
        logger.warning(f"Fraud cases file not found: {cases_file}")
        return {"users": []}


def get_user_fraud_case(username: str, cases_file: str = "fraud_cases.json") -> Optional[Dict]:
    """
    Retrieve fraud case for a specific user.
    Returns user data including all their fraud cases.
    """
    fraud_data = load_fraud_cases(cases_file)
    
    for user in fraud_data.get("users", []):
        if user.get("userName", "").lower() == username.lower():
            return user
    
    logger.warning(f"No fraud case found for user: {username}")
    return None


def update_fraud_case_status(
    username: str,
    case_id: str,
    status: str,
    outcome: str,
    cases_file: str = "fraud_cases.json"
) -> bool:
    """
    Update fraud case status after investigation.
    Returns True if successful, False otherwise.
    """
    fraud_data = load_fraud_cases(cases_file)
    
    for user in fraud_data.get("users", []):
        if user.get("userName", "").lower() == username.lower():
            for case in user.get("cases", []):
                if case.get("caseId") == case_id:
                    case["status"] = status
                    case["outcome"] = outcome
                    case["updatedAt"] = datetime.now().isoformat()
                    
                    # Save updated data
                    try:
                        with open(cases_file, 'w') as f:
                            json.dump(fraud_data, f, indent=2)
                        logger.info(f"Updated fraud case {case_id} for {username}: {status}")
                        return True
                    except Exception as e:
                        logger.error(f"Error saving fraud case update: {e}")
                        return False
    
    logger.error(f"Could not find case {case_id} for user {username}")
    return False


class FraudAgent(Agent):
    """Day 6 - Fraud Alert Voice Agent"""
    
    def __init__(self) -> None:
        self.fraud_state = FraudState()
        
        super().__init__(
            instructions="""You are a professional fraud detection representative from SecureBank.

IMPORTANT: When the customer first connects, immediately greet them warmly. Say something like "Hello, this is Sarah from SecureBank's Fraud Detection Department. We've detected some unusual activity on your account and wanted to verify it with you. May I please have your username to look up your account?"
            
Your role:
1. Greet the customer and ask for their username
2. Once you have the username, ask them the security question from the database
3. If they answer correctly, read the transaction details and ask if they authorized it
4. Use the complete_fraud_investigation tool to save the result
5. Thank them and end the call

Be calm, professional, and reassuring. NEVER ask for full card numbers or PINs.
""",
        )

    @function_tool()
    async def complete_fraud_investigation(
        self, 
        context: RunContext,
        username: str,
        verification_passed: bool,
        transaction_legitimate: Optional[bool] = None
    ):
        """Use this tool when you have completed the fraud investigation to finalize the case.
        
        Args:
            username: The customer's username
            verification_passed: True if the customer passed security verification, False if they failed
            transaction_legitimate: True if customer confirmed the transaction, False if denied, None if verification failed
        
        Returns a confirmation message about the action taken.
        """
        logger.info(f"Completing fraud investigation for {username}")
        logger.info(f"Verification passed: {verification_passed}, Transaction legitimate: {transaction_legitimate}")
        
        # Update fraud state
        self.fraud_state.username = username
        self.fraud_state.is_verified = verification_passed
        self.fraud_state.verification_complete = True
        
        # Get user's fraud case
        user_data = get_user_fraud_case(username)
        
        if not user_data:
            return f"Error: Could not find fraud case for user {username}. Please contact support."
        
        # Get the first pending case
        case = None
        for c in user_data.get("cases", []):
            if c.get("status") == "pending_review":
                case = c
                break
        
        if not case:
            return f"Error: No pending fraud case found for {username}."
        
        case_id = case.get("caseId")
        
        # Determine status and outcome
        if not verification_passed:
            status = "verification_failed"
            outcome = "Customer failed security verification."
            action_message = "Since we couldn't verify your identity, this case will be escalated to our security team."
        elif transaction_legitimate is True:
            status = "confirmed_safe"
            outcome = "Customer confirmed the transaction was legitimate."
            action_message = "Perfect! We've marked this transaction as safe. No action is needed."
        elif transaction_legitimate is False:
            status = "confirmed_fraud"
            outcome = "Customer denied the transaction. Fraud confirmed."
            action_message = f"We've immediately blocked your card ending in {case.get('cardEnding', '****')}. A new card will be mailed to you within 3-5 business days."
        else:
            status = "verification_failed"
            outcome = "Investigation incomplete."
            action_message = "This case will require additional review."
        
        # Update the case in database
        success = update_fraud_case_status(username, case_id, status, outcome)
        
        if success:
            self.fraud_state.status = status
            logger.info(f"✅ Fraud case {case_id} updated: {status}")
            return f"Investigation complete. {action_message}"
        else:
            logger.error(f"❌ Failed to update fraud case {case_id}")
            return f"There was an error updating the case. {action_message}"


async def entrypoint(ctx: JobContext):
    logger.info("🚨 Starting Fraud Alert Service")
    
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",  # Valid Murf voice
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
        agent=FraudAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
