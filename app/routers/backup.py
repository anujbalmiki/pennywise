import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.models import BackupFileUpload
from app.services.backup_service import BackupService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/backup", tags=["Backup Files"])

backup_service = BackupService()


@router.post("/upload", response_model=Dict[str, Any])
async def upload_backup_file(
    backup_data: BackupFileUpload,
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and process a backup file (CSV, XML, TXT, JSON, PDF).
    
    This endpoint accepts backup files from banks or credit card statements
    and uses Gemini AI to extract transaction information.
    """
    try:
        user_id = current_user["uid"]
        
        # Validate backup file
        validation_result = await backup_service.validate_backup_file(backup_data)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_result["error"]
            )
        
        # Process backup file
        result = await backup_service.process_backup_file(user_id, backup_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        return {
            "message": "Backup file processed successfully",
            "filename": result["filename"],
            "file_type": result["file_type"],
            "transactions_found": result["transactions_found"],
            "transactions_created": result["transactions_created"],
            "created_transactions": result["created_transactions"],
            "errors": result["errors"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading backup file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/validate", response_model=Dict[str, Any])
async def validate_backup_file(
    backup_data: BackupFileUpload,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate a backup file before processing.
    
    This endpoint checks if the file format is supported and content is valid.
    """
    try:
        validation_result = await backup_service.validate_backup_file(backup_data)
        
        return {
            "valid": validation_result["valid"],
            "file_type": validation_result.get("file_type"),
            "file_size": validation_result.get("file_size"),
            "error": validation_result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error validating backup file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_backup_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get backup processing statistics for the user.
    """
    try:
        user_id = current_user["uid"]
        stats = await backup_service.get_backup_processing_stats(user_id)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting backup stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
