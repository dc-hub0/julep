from fastapi import APIRouter, HTTPException, status
from .protocol import Session, ChatRequest, ChatMessage
from memory_api.clients.cozo import client
from .protocol import SessionsRequest


router = APIRouter()


@router.post("/sessions/")
def create_session(request: Session):
    query = f"""
        ?[session_id, character_id, user_id, situation, metadata] <- [[
        to_uuid("{request.id}"),
        to_uuid("{request.character_id}"),
        to_uuid("{request.user_id}"),
        "{request.situation}",
        {request.metadata},
    ]]

    :put sessions {{
        character_id,
        user_id,
        session_id,
        situation,
        metadata,
    }}
    """

    client.run(query)


@router.get("/sessions/")
def get_sessions(request: SessionsRequest) -> Session:
    query = f"""
        input[session_id] <- [[
        to_uuid("{request.session_id}"),
    ]]

    ?[
        character_id,
        user_id,
        session_id,
        updated_at,
        situation,
        summary,
        metadata,
        created_at,
    ] := input[session_id],
        *sessions{{
            character_id,
            user_id,
            session_id,
            situation,
            summary,
            metadata,
            updated_at: validity,
            created_at,
            @ "NOW"
        }}, updated_at = to_int(validity)
    """

    resp = client.run(query)

    try:
        return Session(
            id=resp["session_id"][0],
            character_id=resp["character_id"][0],
            user_id=resp["user_id"][0],
            updated_at=resp["updated_at"][0],
            situation=resp["situation"][0],
            summary=resp["summary"][0],
            metadata=resp["metadata"][0],
            created_at=resp["created_at"][0],
        )
    except (IndexError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )


@router.post("/sessions/{session_id}/chat")
def session_chat(session_id: str, request: ChatRequest) -> list[ChatMessage]:
    pass
