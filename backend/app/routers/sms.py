import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.models import SMSMessage, SMSRequest
from app.services.sms_service import SMSService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sms", tags=["SMS"])

sms_service = SMSService()


@router.post("/", response_model=Dict[str, Any])
async def receive_sms(
    sms_data: SMSRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Receive SMS message from mobile app and process for transactions.
    
    This endpoint is called by the React Native app when a new SMS is received.
    """
    try:
        user_id = current_user["uid"]
        
        # Save SMS message
        sms_message = await sms_service.save_sms(user_id, sms_data)
        
        if not sms_message:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save SMS message"
            )
        
        # Process SMS for transactions
        transaction_result = await sms_service.process_sms_for_transactions(
            user_id, sms_message
        )
        
        response = {
            "message": "SMS received successfully",
            "sms_id": sms_message.id,
            "transaction_created": transaction_result is not None
        }
        
        if transaction_result:
            response["transaction"] = transaction_result
        
        return response
        
    except Exception as e:
        logger.error(f"Error receiving SMS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=List[SMSMessage])
async def get_sms_messages(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    Get SMS messages for the authenticated user.
    """
    try:
        user_id = current_user["uid"]
        sms_messages = await sms_service.get_sms_messages(user_id, limit, offset)
        return sms_messages
        
    except Exception as e:
        logger.error(f"Error getting SMS messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{sms_id}", response_model=SMSMessage)
async def get_sms_message(
    sms_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific SMS message by ID.
    """
    try:
        user_id = current_user["uid"]
        sms_message = await sms_service.get_sms_message(user_id, sms_id)
        
        if not sms_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SMS message not found"
            )
        
        return sms_message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting SMS message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/reprocess", response_model=List[Dict[str, Any]])
async def reprocess_unparsed_sms(
    current_user: dict = Depends(get_current_user)
):
    """
    Reprocess all unparsed SMS messages for the user.
    """
    try:
        user_id = current_user["uid"]
        results = await sms_service.reprocess_unparsed_sms(user_id)
        
        return results
        
    except Exception as e:
        logger.error(f"Error reprocessing SMS messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/statistics/summary", response_model=Dict[str, Any])
async def get_sms_statistics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get SMS statistics for the authenticated user.
    """
    try:
        user_id = current_user["uid"]
        statistics = await sms_service.get_sms_statistics(user_id)
        return statistics
        
    except Exception as e:
        logger.error(f"Error getting SMS statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{sms_id}")
async def delete_sms_message(
    sms_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an SMS message.
    """
    try:
        user_id = current_user["uid"]
        success = await sms_service.delete_sms_message(user_id, sms_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SMS message not found"
            )
        
        return {"message": "SMS message deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting SMS message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
