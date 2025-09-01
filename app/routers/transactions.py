import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import get_current_user
from app.models import (AnalyticsResponse, ExportFormat, Transaction,
                        TransactionCreate, TransactionFilter,
                        TransactionUpdate)
from app.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", tags=["Transactions"])

transaction_service = TransactionService()


@router.post("/", response_model=Transaction)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new transaction manually.
    """
    try:
        user_id = current_user["uid"]
        transaction = await transaction_service.create_transaction(user_id, transaction_data.dict())
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create transaction"
            )
        
        return transaction
        
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=List[Transaction])
async def get_transactions(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    min_amount: Optional[float] = Query(None, description="Minimum amount filter"),
    max_amount: Optional[float] = Query(None, description="Maximum amount filter"),
    transaction_type: Optional[str] = Query(None, description="Transaction type filter"),
    merchant: Optional[str] = Query(None, description="Merchant filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    payment_method: Optional[str] = Query(None, description="Payment method filter"),
    is_failed: Optional[bool] = Query(None, description="Failed transaction filter"),
    tags: Optional[str] = Query(None, description="Tags filter (comma-separated)"),
    limit: int = Query(50, description="Number of transactions to return"),
    offset: int = Query(0, description="Number of transactions to skip"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get transactions with optional filters.
    """
    try:
        user_id = current_user["uid"]
        
        # Parse tags if provided
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        filters = TransactionFilter(
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            transaction_type=transaction_type,
            merchant=merchant,
            category=category,
            payment_method=payment_method,
            is_failed=is_failed,
            tags=tag_list,
            limit=limit,
            offset=offset
        )
        
        transactions = await transaction_service.get_transactions(user_id, filters)
        return transactions
        
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific transaction by ID.
    """
    try:
        user_id = current_user["uid"]
        transaction = await transaction_service.get_transaction(user_id, transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{transaction_id}", response_model=Transaction)
async def update_transaction(
    transaction_id: str,
    update_data: TransactionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a transaction.
    """
    try:
        user_id = current_user["uid"]
        transaction = await transaction_service.update_transaction(
            user_id, transaction_id, update_data.dict(exclude_unset=True)
        )
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a transaction.
    """
    try:
        user_id = current_user["uid"]
        success = await transaction_service.delete_transaction(user_id, transaction_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return {"message": "Transaction deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/analytics/summary", response_model=AnalyticsResponse)
async def get_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get transaction analytics and summary.
    """
    try:
        user_id = current_user["uid"]
        analytics = await transaction_service.get_analytics(user_id, start_date, end_date)
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/recurring/detect", response_model=List[Dict[str, Any]])
async def detect_recurring_transactions(
    current_user: dict = Depends(get_current_user)
):
    """
    Detect recurring transactions for the user.
    """
    try:
        user_id = current_user["uid"]
        recurring_transactions = await transaction_service.detect_recurring_transactions(user_id)
        return recurring_transactions
        
    except Exception as e:
        logger.error(f"Error detecting recurring transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/export/{format}")
async def export_transactions(
    format: ExportFormat,
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    current_user: dict = Depends(get_current_user)
):
    """
    Export transactions in various formats (PDF, Excel, CSV, JSON).
    """
    try:
        user_id = current_user["uid"]
        
        # Build filters for export
        filters = TransactionFilter(
            start_date=start_date,
            end_date=end_date,
            limit=10000  # Large limit for export
        )
        
        transactions = await transaction_service.get_transactions(user_id, filters)
        
        # TODO: Implement export functionality based on format
        # For now, return JSON format
        if format == ExportFormat.JSON:
            return {
                "format": format,
                "transaction_count": len(transactions),
                "data": [tx.dict() for tx in transactions]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Export format {format} not yet implemented"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
