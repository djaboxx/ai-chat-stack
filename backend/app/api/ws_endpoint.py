"""
WebSocket API endpoints
"""
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..core.ws_manager import manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for client communication"""
    # Connect the client
    client_id = await manager.connect(websocket)
    
    try:
        # Process messages while the connection is active
        while True:
            # Wait for a message from the client
            data = await websocket.receive_text()
            
            # Parse the message
            try:
                message = json.loads(data)
                message_type = message.get("type", "").upper()
                payload = message.get("payload", {})
                
                logger.info(f"Received message from {client_id}: {message_type}")
                ws_router = dict(
                    SUBMIT_CONFIG=partial(manager.handle_submit_config, client_id),
                    FETCH_FILES=partial(manager.handle_fetch_files, client_id),
                    SEND_CHAT_MESSAGE=partial(manager.handle_chat_message, client_id),
                    ADD_REPOSITORY=partial(manager.handle_add_repository, client_id),
                    UPDATE_REPOSITORY=partial(manager.handle_update_repository, client_id),
                    DELETE_REPOSITORY=partial(manager.handle_delete_repository, client_id),
                    SELECT_REPOSITORY=partial(manager.handle_select_repository, client_id)
                )
                if message_type in ws_router:
                    await ws_router[message_type](payload)
                elif message_type == "PING":
                    await websocket.send_text(json.dumps({"type": "PONG"}))
                elif message_type == "PONG":
                    logger.info(f"Received PONG from {client_id}")
                else:
                    logger.warning(f"Unknown message type: {message_type}")
                    
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    except WebSocketDisconnect:
        # Handle client disconnect
        manager.disconnect(client_id)
    except Exception as e:
        # Handle any other exceptions
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(client_id)
