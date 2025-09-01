import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from bson import ObjectId

from app.database import (get_categories_collection, get_merchants_collection,
                          get_transactions_collection)
from app.models import AnalyticsResponse, Transaction, TransactionFilter
from app.services.sms_parser import SMSParser

logger = logging.getLogger(__name__)


class TransactionService:
    """Service for managing transactions."""
    
    def __init__(self):
        self.sms_parser = SMSParser()
        self.transactions_collection = get_transactions_collection()
        self.categories_collection = get_categories_collection()
        self.merchants_collection = get_merchants_collection()

    async def create_transaction_from_sms(self, user_id: str, sms_message_id: str, 
                                        sender: str, message: str, timestamp: datetime) -> Optional[Transaction]:
        """Create transaction from parsed SMS message."""
        try:
            # Parse SMS to extract transaction data
            parsed_data = self.sms_parser.parse_sms(sender, message)
            
            if not parsed_data:
                logger.info(f"No transaction data found in SMS from {sender}")
                return None
            
            # Create transaction object
            transaction_data = {
                "user_id": user_id,
                "sms_message_id": sms_message_id,
                **parsed_data
            }
            
            transaction = Transaction(**transaction_data)
            
            # Save to database
            result = await self.transactions_collection.insert_one(transaction.dict())
            transaction.id = str(result.inserted_id)
            
            # Auto-categorize transaction
            await self._auto_categorize_transaction(transaction)
            
            logger.info(f"Created transaction {transaction.id} from SMS {sms_message_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error creating transaction from SMS: {e}")
            return None

    async def create_transaction(self, user_id: str, transaction_data: Dict[str, Any]) -> Optional[Transaction]:
        """Create a new transaction."""
        try:
            transaction_data["user_id"] = user_id
            transaction = Transaction(**transaction_data)
            
            result = await self.transactions_collection.insert_one(transaction.dict())
            transaction.id = str(result.inserted_id)
            
            # Auto-categorize transaction
            await self._auto_categorize_transaction(transaction)
            
            logger.info(f"Created transaction {transaction.id} for user {user_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            return None

    async def get_transaction(self, user_id: str, transaction_id: str) -> Optional[Transaction]:
        """Get a specific transaction by ID."""
        try:
            result = await self.transactions_collection.find_one({
                "_id": ObjectId(transaction_id),
                "user_id": user_id
            })
            
            if result:
                result["id"] = str(result["_id"])
                return Transaction(**result)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting transaction {transaction_id}: {e}")
            return None

    async def get_transactions(self, user_id: str, filters: TransactionFilter) -> List[Transaction]:
        """Get transactions with filters."""
        try:
            # Build query
            query = {"user_id": user_id}
            
            if filters.start_date:
                query["transaction_date"] = {"$gte": filters.start_date}
            
            if filters.end_date:
                if "transaction_date" in query:
                    query["transaction_date"]["$lte"] = filters.end_date
                else:
                    query["transaction_date"] = {"$lte": filters.end_date}
            
            if filters.min_amount:
                query["amount"] = {"$gte": filters.min_amount}
            
            if filters.max_amount:
                if "amount" in query:
                    query["amount"]["$lte"] = filters.max_amount
                else:
                    query["amount"] = {"$lte": filters.max_amount}
            
            if filters.transaction_type:
                query["transaction_type"] = filters.transaction_type
            
            if filters.merchant:
                query["merchant"] = {"$regex": filters.merchant, "$options": "i"}
            
            if filters.category:
                query["category"] = filters.category
            
            if filters.payment_method:
                query["payment_method"] = filters.payment_method
            
            if filters.is_failed is not None:
                query["is_failed"] = filters.is_failed
            
            if filters.tags:
                query["tags"] = {"$in": filters.tags}
            
            # Execute query
            cursor = self.transactions_collection.find(query).sort(
                "transaction_date", -1
            ).skip(filters.offset).limit(filters.limit)
            
            transactions = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                transactions.append(Transaction(**doc))
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            return []

    async def update_transaction(self, user_id: str, transaction_id: str, 
                               update_data: Dict[str, Any]) -> Optional[Transaction]:
        """Update a transaction."""
        try:
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.transactions_collection.update_one(
                {"_id": ObjectId(transaction_id), "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_transaction(user_id, transaction_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating transaction {transaction_id}: {e}")
            return None

    async def delete_transaction(self, user_id: str, transaction_id: str) -> bool:
        """Delete a transaction."""
        try:
            result = await self.transactions_collection.delete_one({
                "_id": ObjectId(transaction_id),
                "user_id": user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting transaction {transaction_id}: {e}")
            return False

    async def get_analytics(self, user_id: str, start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None) -> AnalyticsResponse:
        """Get transaction analytics."""
        try:
            # Build date filter
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            
            query = {"user_id": user_id}
            if date_filter:
                query["transaction_date"] = date_filter
            
            # Get total transactions and amount
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": None,
                    "total_transactions": {"$sum": 1},
                    "total_amount": {"$sum": "$amount"},
                    "average_amount": {"$avg": "$amount"},
                    "failed_transactions": {"$sum": {"$cond": ["$is_failed", 1, 0]}},
                    "recurring_transactions": {"$sum": {"$cond": ["$is_recurring", 1, 0]}}
                }}
            ]
            
            result = await self.transactions_collection.aggregate(pipeline).to_list(1)
            
            if not result:
                return AnalyticsResponse(
                    total_transactions=0,
                    total_amount=0.0,
                    average_amount=0.0,
                    transaction_count_by_type={},
                    amount_by_type={},
                    top_merchants=[],
                    top_categories=[],
                    monthly_trends=[],
                    failed_transactions=0,
                    recurring_transactions=0
                )
            
            stats = result[0]
            
            # Get transaction count by type
            type_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$transaction_type",
                    "count": {"$sum": 1},
                    "amount": {"$sum": "$amount"}
                }}
            ]
            
            type_results = await self.transactions_collection.aggregate(type_pipeline).to_list(None)
            transaction_count_by_type = {item["_id"]: item["count"] for item in type_results}
            amount_by_type = {item["_id"]: item["amount"] for item in type_results}
            
            # Get top merchants
            merchant_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$merchant",
                    "count": {"$sum": 1},
                    "amount": {"$sum": "$amount"}
                }},
                {"$sort": {"amount": -1}},
                {"$limit": 10}
            ]
            
            merchant_results = await self.transactions_collection.aggregate(merchant_pipeline).to_list(None)
            top_merchants = [
                {"merchant": item["_id"], "count": item["count"], "amount": item["amount"]}
                for item in merchant_results if item["_id"]
            ]
            
            # Get top categories
            category_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "amount": {"$sum": "$amount"}
                }},
                {"$sort": {"amount": -1}},
                {"$limit": 10}
            ]
            
            category_results = await self.transactions_collection.aggregate(category_pipeline).to_list(None)
            top_categories = [
                {"category": item["_id"], "count": item["count"], "amount": item["amount"]}
                for item in category_results if item["_id"]
            ]
            
            # Get monthly trends
            trend_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": {
                        "year": {"$year": "$transaction_date"},
                        "month": {"$month": "$transaction_date"}
                    },
                    "count": {"$sum": 1},
                    "amount": {"$sum": "$amount"}
                }},
                {"$sort": {"_id.year": 1, "_id.month": 1}}
            ]
            
            trend_results = await self.transactions_collection.aggregate(trend_pipeline).to_list(None)
            monthly_trends = [
                {
                    "year": item["_id"]["year"],
                    "month": item["_id"]["month"],
                    "count": item["count"],
                    "amount": item["amount"]
                }
                for item in trend_results
            ]
            
            return AnalyticsResponse(
                total_transactions=stats["total_transactions"],
                total_amount=stats["total_amount"],
                average_amount=stats["average_amount"],
                transaction_count_by_type=transaction_count_by_type,
                amount_by_type=amount_by_type,
                top_merchants=top_merchants,
                top_categories=top_categories,
                monthly_trends=monthly_trends,
                failed_transactions=stats["failed_transactions"],
                recurring_transactions=stats["recurring_transactions"]
            )
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return AnalyticsResponse(
                total_transactions=0,
                total_amount=0.0,
                average_amount=0.0,
                transaction_count_by_type={},
                amount_by_type={},
                top_merchants=[],
                top_categories=[],
                monthly_trends=[],
                failed_transactions=0,
                recurring_transactions=0
            )

    async def _auto_categorize_transaction(self, transaction: Transaction) -> None:
        """Auto-categorize transaction based on merchant name."""
        try:
            if not transaction.merchant or transaction.category:
                return
            
            # Simple merchant-based categorization
            merchant_lower = transaction.merchant.lower()
            
            category_mapping = {
                "grocery": ["grocery", "supermarket", "food", "restaurant", "cafe", "swiggy", "zomato", "blinkit", "bigbasket"],
                "transport": ["uber", "ola", "metro", "bus", "train", "fuel", "petrol", "diesel"],
                "shopping": ["amazon", "flipkart", "myntra", "shopping", "mall", "store"],
                "entertainment": ["netflix", "prime", "hotstar", "movie", "cinema", "theatre"],
                "utilities": ["electricity", "water", "gas", "internet", "mobile", "airtel", "jio"],
                "healthcare": ["hospital", "clinic", "pharmacy", "medical", "doctor"],
                "education": ["school", "college", "university", "course", "training"],
                "travel": ["hotel", "flight", "booking", "travel", "tourism"]
            }
            
            for category, keywords in category_mapping.items():
                if any(keyword in merchant_lower for keyword in keywords):
                    await self.update_transaction(
                        transaction.user_id,
                        transaction.id,
                        {"category": category}
                    )
                    break
                    
        except Exception as e:
            logger.error(f"Error auto-categorizing transaction: {e}")

    async def detect_recurring_transactions(self, user_id: str) -> List[Dict[str, Any]]:
        """Detect recurring transactions."""
        try:
            # Get transactions from last 6 months
            six_months_ago = datetime.utcnow() - timedelta(days=180)
            
            pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "transaction_date": {"$gte": six_months_ago},
                    "merchant": {"$exists": True, "$ne": None}
                }},
                {"$group": {
                    "_id": {
                        "merchant": "$merchant",
                        "amount": "$amount",
                        "day_of_month": {"$dayOfMonth": "$transaction_date"}
                    },
                    "count": {"$sum": 1},
                    "transactions": {"$push": {
                        "id": "$_id",
                        "transaction_date": "$transaction_date",
                        "amount": "$amount"
                    }}
                }},
                {"$match": {"count": {"$gte": 2}}},
                {"$sort": {"count": -1}}
            ]
            
            results = await self.transactions_collection.aggregate(pipeline).to_list(None)
            
            recurring_transactions = []
            for result in results:
                if result["count"] >= 2:
                    # Mark transactions as recurring
                    for tx in result["transactions"]:
                        await self.update_transaction(
                            user_id,
                            str(tx["id"]),
                            {"is_recurring": True}
                        )
                    
                    recurring_transactions.append({
                        "merchant": result["_id"]["merchant"],
                        "amount": result["_id"]["amount"],
                        "day_of_month": result["_id"]["day_of_month"],
                        "frequency": result["count"],
                        "transactions": result["transactions"]
                    })
            
            return recurring_transactions
            
        except Exception as e:
            logger.error(f"Error detecting recurring transactions: {e}")
            return []
