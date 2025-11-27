import logging
import json
from livekit.agents import (
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
)
from livekit.plugins import silero
from dotenv import load_dotenv

import chat_service
import barista_service
import wellness_service
import tutor_service
import sdr_service
import fraud_service

load_dotenv(".env.local")
logger = logging.getLogger("multi_agent_dispatcher")

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    logger.info("Connecting to LiveKit room...")
    await ctx.connect()
    logger.info(f"Connected to room: {ctx.room.name}")
    
    logger.info("Waiting for participant to determine service...")
    
    try:
        # Wait for participant with timeout
        participant = await ctx.wait_for_participant()
        logger.info(f"Participant joined: {participant.identity}")
    except Exception as e:
        logger.error(f"Error waiting for participant: {e}")
        return
    
    selected_service = "chat"  # Default fallback
    
    # Check attributes (preferred method for LiveKit tokens)
    if participant.attributes and "service" in participant.attributes:
        selected_service = participant.attributes["service"]
        logger.info(f"✓ Service selected from attributes: {selected_service}")
    # Fallback to metadata
    elif participant.metadata:
        try:
            meta = json.loads(participant.metadata)
            if "service" in meta and meta["service"]:
                selected_service = meta["service"]
                logger.info(f"✓ Service selected from metadata: {selected_service}")
            else:
                logger.warning(f"Metadata present but no 'service' field found: {participant.metadata}")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse metadata as JSON: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error parsing metadata: {e}")
    else:
        logger.warning("No attributes or metadata found, using default service: chat")
            
    logger.info(f"🚀 Routing to service: {selected_service}")
    
    # Route to appropriate service
    try:
        if selected_service == "chat":
            await chat_service.entrypoint(ctx)
        elif selected_service == "coffee":
            await barista_service.entrypoint(ctx)
        elif selected_service == "wellness":
            await wellness_service.entrypoint(ctx)
        elif selected_service == "tutor":
            await tutor_service.entrypoint(ctx)
        elif selected_service == "sdr":
            await sdr_service.entrypoint(ctx)
        elif selected_service == "fraud":
            await fraud_service.entrypoint(ctx)
        else:
            logger.warning(f"Unknown service: {selected_service}, defaulting to chat")
            await chat_service.entrypoint(ctx)
    except Exception as e:
        logger.error(f"Error in {selected_service} service: {e}", exc_info=True)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
