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
    user_data=Depends(verify_supabase_token),
):
    """Handle chat requests for any service"""
    try:
        if service == "spotify":
            response_text = await agent_manager.process_message(
                "spotify", request.message
            )
            return {"response": response_text}  # Simple response with just content

        raise HTTPException(status_code=400, detail="Unsupported service")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/agents")
async def list_agents(user_data=Depends(verify_supabase_token)):
    """List available agents including predefined ones"""
    try:
        agents = list(agent_manager._agents.keys())
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list agents")
