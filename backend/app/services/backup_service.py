import base64
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models import BackupFileUpload
from app.services.sms_parser import SMSParser
from app.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)


class BackupService:
    """Service for handling backup file uploads and parsing."""
    
    def __init__(self):
        self.sms_parser = SMSParser()
        self.transaction_service = TransactionService()

    async def process_backup_file(self, user_id: str, backup_data: BackupFileUpload) -> Dict[str, Any]:
        """Process backup file and extract transactions."""
        try:
            # Decode file content if it's base64 encoded
            try:
                file_content = base64.b64decode(backup_data.file_content).decode('utf-8')
            except:
                # If not base64, use as plain text
                file_content = backup_data.file_content
            
            logger.info(f"Processing backup file: {backup_data.filename} ({backup_data.file_type})")
            
            # Parse file content using Gemini AI
            transactions_data = await self.sms_parser.parse_backup_file_with_gemini(
                file_content, backup_data.file_type
            )
            
            if not transactions_data:
                logger.warning(f"No transactions found in backup file: {backup_data.filename}")
                return {
                    "success": True,
                    "message": "Backup file processed successfully",
                    "filename": backup_data.filename,
                    "file_type": backup_data.file_type,
                    "transactions_found": 0,
                    "transactions_created": 0,
                    "errors": []
                }
            
            # Create transactions in database
            created_transactions = []
            errors = []
            
            for tx_data in transactions_data:
                try:
                    # Add user_id to transaction data
                    tx_data["user_id"] = user_id
                    
                    # Create transaction
                    transaction = await self.transaction_service.create_transaction(user_id, tx_data)
                    
                    if transaction:
                        created_transactions.append({
                            "id": transaction.id,
                            "amount": transaction.amount,
                            "merchant": transaction.merchant,
                            "transaction_type": transaction.transaction_type,
                            "transaction_date": transaction.transaction_date
                        })
                    else:
                        errors.append(f"Failed to create transaction: {tx_data.get('amount', 'Unknown')} - {tx_data.get('merchant', 'Unknown')}")
                        
                except Exception as e:
                    logger.error(f"Error creating transaction from backup: {e}")
                    errors.append(f"Error processing transaction: {str(e)}")
            
            logger.info(f"Successfully processed backup file: {backup_data.filename}")
            logger.info(f"Created {len(created_transactions)} transactions from {len(transactions_data)} found")
            
            return {
                "success": True,
                "message": "Backup file processed successfully",
                "filename": backup_data.filename,
                "file_type": backup_data.file_type,
                "transactions_found": len(transactions_data),
                "transactions_created": len(created_transactions),
                "created_transactions": created_transactions,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Error processing backup file: {e}")
            return {
                "success": False,
                "message": f"Failed to process backup file: {str(e)}",
                "filename": backup_data.filename,
                "file_type": backup_data.file_type,
                "transactions_found": 0,
                "transactions_created": 0,
                "errors": [str(e)]
            }

    async def validate_backup_file(self, backup_data: BackupFileUpload) -> Dict[str, Any]:
        """Validate backup file before processing."""
        try:
            # Check file type
            supported_types = ["csv", "xml", "txt", "json", "pdf"]
            if backup_data.file_type.lower() not in supported_types:
                return {
                    "valid": False,
                    "error": f"Unsupported file type: {backup_data.file_type}. Supported types: {', '.join(supported_types)}"
                }
            
            # Check file content
            if not backup_data.file_content:
                return {
                    "valid": False,
                    "error": "File content is empty"
                }
            
            # Try to decode content
            try:
                file_content = base64.b64decode(backup_data.file_content).decode('utf-8')
            except:
                file_content = backup_data.file_content
            
            if len(file_content.strip()) == 0:
                return {
                    "valid": False,
                    "error": "File content is empty after decoding"
                }
            
            return {
                "valid": True,
                "file_size": len(file_content),
                "file_type": backup_data.file_type
            }
            
        except Exception as e:
            logger.error(f"Error validating backup file: {e}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }

    async def get_backup_processing_stats(self, user_id: str) -> Dict[str, Any]:
        """Get backup processing statistics for a user."""
        try:
            # This would typically query a backup_files collection
            # For now, return basic stats
            return {
                "total_backups_processed": 0,
                "total_transactions_imported": 0,
                "last_backup_processed": None,
                "supported_file_types": ["csv", "xml", "txt", "json", "pdf"]
            }
            
        except Exception as e:
            logger.error(f"Error getting backup stats: {e}")
            return {
                "total_backups_processed": 0,
                "total_transactions_imported": 0,
                "last_backup_processed": None,
                "supported_file_types": ["csv", "xml", "txt", "json", "pdf"]
            }
