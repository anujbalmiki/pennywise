import logging
from typing import Any, Dict

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.database import get_users_collection
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user information.
    """
    try:
        users_collection = get_users_collection()
        
        # Get user from database
        user_doc = await users_collection.find_one({"firebase_uid": current_user["uid"]})
        
        if not user_doc:
            # Create user if not exists
            user_data = {
                "firebase_uid": current_user["uid"],
                "email": current_user["email"],
                "phone": current_user.get("phone_number"),
                "name": current_user.get("name")
            }
            
            result = await users_collection.insert_one(user_data)
            user_doc = await users_collection.find_one({"_id": result.inserted_id})
        
        # Convert ObjectId to string
        user_doc["id"] = str(user_doc["_id"])
        del user_doc["_id"]
        
        return user_doc
        
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/me", response_model=Dict[str, Any])
async def update_user_info(
    user_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user information.
    """
    try:
        users_collection = get_users_collection()
        
        # Remove sensitive fields that shouldn't be updated
        update_data = {k: v for k, v in user_data.items() 
                      if k in ["name", "phone"] and v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        result = await users_collection.update_one(
            {"firebase_uid": current_user["uid"]},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get updated user
        updated_user = await users_collection.find_one({"firebase_uid": current_user["uid"]})
        updated_user["id"] = str(updated_user["_id"])
        del updated_user["_id"]
        
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/me")
async def delete_user_account(
    current_user: dict = Depends(get_current_user)
):
    """
    Delete current user account and all associated data.
    """
    try:
        users_collection = get_users_collection()
        
        # Delete user from database
        result = await users_collection.delete_one({"firebase_uid": current_user["uid"]})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # TODO: Delete all associated data (transactions, SMS messages, etc.)
        # This should be implemented in a separate service
        
        return {"message": "User account deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_user_statistics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user statistics and summary.
    """
    try:
        user_id = current_user["uid"]
        
        # Import here to avoid circular imports
        from app.services.sms_service import SMSService
        from app.services.transaction_service import TransactionService
        
        transaction_service = TransactionService()
        sms_service = SMSService()
        
        # Get transaction analytics
        analytics = await transaction_service.get_analytics(user_id)
        
        # Get SMS statistics
        sms_stats = await sms_service.get_sms_statistics(user_id)
        
        # Get recurring transactions
        recurring_transactions = await transaction_service.detect_recurring_transactions(user_id)
        
        return {
            "transaction_stats": {
                "total_transactions": analytics.total_transactions,
                "total_amount": analytics.total_amount,
                "average_amount": analytics.average_amount,
                "failed_transactions": analytics.failed_transactions,
                "recurring_transactions": analytics.recurring_transactions
            },
            "sms_stats": sms_stats,
            "recurring_patterns": len(recurring_transactions),
            "top_merchants": analytics.top_merchants[:5],
            "top_categories": analytics.top_categories[:5]
        }
        
    except Exception as e:
        logger.error(f"Error getting user statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
