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
                
                # Handle different message types
                if message_type == "SUBMIT_CONFIG":
                    await manager.handle_submit_config(client_id, payload)
                elif message_type == "FETCH_FILES":
                    await manager.handle_fetch_files(client_id, payload)
                elif message_type == "SEND_CHAT_MESSAGE":
                    await manager.handle_chat_message(client_id, payload)
                elif message_type == "ADD_REPOSITORY":
                    await manager.handle_add_repository(client_id, payload)
                elif message_type == "UPDATE_REPOSITORY":
                    await manager.handle_update_repository(client_id, payload)
                elif message_type == "DELETE_REPOSITORY":
                    await manager.handle_delete_repository(client_id, payload)
                elif message_type == "SELECT_REPOSITORY":
                    await manager.handle_select_repository(client_id, payload)
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
