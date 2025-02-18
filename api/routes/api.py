from fastapi import APIRouter, HTTPException, Depends
from api.models.api_models import APIRegistration
from api.models.chat_models import ChatRequest
from api.core.agent_manager import agent_manager
from api.utils.auth import verify_supabase_token
import uuid

router = APIRouter()


@router.post("/apis/register")
async def register_api(
    registration: APIRegistration, user_data=Depends(verify_supabase_token)
):
    """Register a new API and create its agent"""
    try:
        api_id = str(uuid.uuid4())
        await agent_manager.create_agent(api_id, registration.openapi_spec)
        return {"api_id": api_id, "message": "API registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to register API")


@router.post("/{service}/chat")
async def chat(
    service: str,
    request: ChatRequest,
    user_data: dict = Depends(verify_supabase_token),
):
    """Handle chat requests for any service"""
    try:
        if service in ["spotify", "ticketmaster"]:
            user_id = user_data.get("id")  # Changed from 'sub' to 'id'
            if not user_id:
                raise HTTPException(
                    status_code=401, detail="User ID not found in token"
                )

            response_text = await agent_manager.process_message(
                service, request.message, request.sessionId, user_id
            )
            return {"response": response_text}

        raise HTTPException(status_code=400, detail="Unsupported service")

    except Exception as e:
        print(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/agents")
async def list_agents(user_data=Depends(verify_supabase_token)):
    """List available agents including predefined ones"""
    try:
        agents = list(agent_manager._agents.keys())
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list agents")


@router.post("/{service}/cleanup-session")
async def cleanup_session(
    service: str,
    session_id: str,
    user_data=Depends(verify_supabase_token),
):
    """Clean up session resources when user leaves or refreshes the page"""
    try:
        agent_manager.cleanup_session(session_id)
        return {"message": "Session cleaned up successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to cleanup session")
