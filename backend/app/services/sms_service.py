import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId

from app.database import get_sms_messages_collection
from app.models import SMSMessage, SMSRequest
from app.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)


class SMSService:
    """Service for managing SMS messages."""
    
    def __init__(self):
        self.sms_collection = get_sms_messages_collection()
        self.transaction_service = TransactionService()

    async def save_sms(self, user_id: str, sms_data: SMSRequest) -> Optional[SMSMessage]:
        """Save SMS message to database."""
        try:
            sms_message = SMSMessage(
                user_id=user_id,
                sender=sms_data.sender,
                message_text=sms_data.message_text,
                timestamp=sms_data.timestamp
            )
            
            result = await self.sms_collection.insert_one(sms_message.dict())
            sms_message.id = str(result.inserted_id)
            
            logger.info(f"Saved SMS {sms_message.id} for user {user_id}")
            return sms_message
            
        except Exception as e:
            logger.error(f"Error saving SMS: {e}")
            return None

    async def get_sms_message(self, user_id: str, sms_id: str) -> Optional[SMSMessage]:
        """Get a specific SMS message by ID."""
        try:
            result = await self.sms_collection.find_one({
                "_id": ObjectId(sms_id),
                "user_id": user_id
            })
            
            if result:
                result["id"] = str(result["_id"])
                return SMSMessage(**result)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting SMS {sms_id}: {e}")
            return None

    async def get_sms_messages(self, user_id: str, limit: int = 50, offset: int = 0) -> List[SMSMessage]:
        """Get SMS messages for a user."""
        try:
            cursor = self.sms_collection.find({"user_id": user_id}).sort(
                "timestamp", -1
            ).skip(offset).limit(limit)
            
            sms_messages = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                sms_messages.append(SMSMessage(**doc))
            
            return sms_messages
            
        except Exception as e:
            logger.error(f"Error getting SMS messages: {e}")
            return []

    async def process_sms_for_transactions(self, user_id: str, sms_message: SMSMessage) -> Optional[Dict[str, Any]]:
        """Process SMS message and create transaction if applicable using intelligent detection."""
        try:
            # Use intelligent SMS processing that first detects if it's transactional
            parsed_data = await self.transaction_service.sms_parser.process_sms_intelligently(
                sms_message.sender, sms_message.message_text
            )
            
            if not parsed_data:
                logger.info(f"SMS {sms_message.id} skipped - not a transaction SMS")
                return None
            
            # Create transaction from parsed data
            transaction_data = {
                "user_id": user_id,
                "sms_message_id": sms_message.id,
                **parsed_data
            }
            
            transaction = await self.transaction_service.create_transaction(user_id, transaction_data)
            
            if transaction:
                # Mark SMS as parsed
                await self.mark_sms_as_parsed(sms_message.id)
                
                return {
                    "sms_id": sms_message.id,
                    "transaction_id": transaction.id,
                    "transaction_type": transaction.transaction_type,
                    "amount": transaction.amount,
                    "merchant": transaction.merchant,
                    "detection_confidence": parsed_data.get("detection_confidence"),
                    "detection_reason": parsed_data.get("detection_reason")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing SMS for transactions: {e}")
            return None

    async def mark_sms_as_parsed(self, sms_id: str) -> bool:
        """Mark SMS message as parsed."""
        try:
            result = await self.sms_collection.update_one(
                {"_id": ObjectId(sms_id)},
                {"$set": {"parsed": True, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error marking SMS as parsed: {e}")
            return False

    async def get_unparsed_sms_messages(self, user_id: str) -> List[SMSMessage]:
        """Get unparsed SMS messages for a user."""
        try:
            cursor = self.sms_collection.find({
                "user_id": user_id,
                "parsed": False
            }).sort("timestamp", -1)
            
            sms_messages = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                sms_messages.append(SMSMessage(**doc))
            
            return sms_messages
            
        except Exception as e:
            logger.error(f"Error getting unparsed SMS messages: {e}")
            return []

    async def reprocess_unparsed_sms(self, user_id: str) -> List[Dict[str, Any]]:
        """Reprocess all unparsed SMS messages for a user using intelligent detection."""
        try:
            unparsed_sms = await self.get_unparsed_sms_messages(user_id)
            processed_results = []
            
            for sms in unparsed_sms:
                result = await self.process_sms_for_transactions(user_id, sms)
                if result:
                    processed_results.append(result)
            
            logger.info(f"Reprocessed {len(processed_results)} SMS messages for user {user_id}")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error reprocessing unparsed SMS: {e}")
            return []

    async def delete_sms_message(self, user_id: str, sms_id: str) -> bool:
        """Delete an SMS message."""
        try:
            result = await self.sms_collection.delete_one({
                "_id": ObjectId(sms_id),
                "user_id": user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting SMS {sms_id}: {e}")
            return False

    async def get_sms_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get SMS statistics for a user."""
        try:
            # Total SMS count
            total_sms = await self.sms_collection.count_documents({"user_id": user_id})
            
            # Parsed SMS count
            parsed_sms = await self.sms_collection.count_documents({
                "user_id": user_id,
                "parsed": True
            })
            
            # Unparsed SMS count
            unparsed_sms = await self.sms_collection.count_documents({
                "user_id": user_id,
                "parsed": False
            })
            
            # SMS by sender
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$sender",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            sender_stats = await self.sms_collection.aggregate(pipeline).to_list(None)
            
            return {
                "total_sms": total_sms,
                "parsed_sms": parsed_sms,
                "unparsed_sms": unparsed_sms,
                "parsing_rate": (parsed_sms / total_sms * 100) if total_sms > 0 else 0,
                "top_senders": [
                    {"sender": item["_id"], "count": item["count"]}
                    for item in sender_stats
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting SMS statistics: {e}")
            return {
                "total_sms": 0,
                "parsed_sms": 0,
                "unparsed_sms": 0,
                "parsing_rate": 0,
                "top_senders": []
            }
