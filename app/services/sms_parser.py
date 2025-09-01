import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import google.generativeai as genai

from app.config import settings
from app.models import PaymentMethod, TransactionType

logger = logging.getLogger(__name__)


class SMSParser:
    """Universal SMS parser using Google Gemini AI for any bank or credit card format."""
    
    def __init__(self):
        # Initialize Gemini AI
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.use_gemini = True
            logger.info("Gemini AI initialized for universal SMS parsing")
        else:
            self.use_gemini = False
            logger.error("Gemini API key not provided. SMS parsing will not work without AI.")
            raise ValueError("Gemini API key is required for SMS parsing")

    def _create_unified_sms_prompt(self, sender: str, message: str) -> str:
        """Create a unified prompt for Gemini to detect and parse SMS in one request."""
        return f"""
You are an expert SMS analyzer for financial transactions. Analyze the following SMS message and determine if it contains transaction information.

SMS Sender: {sender}
SMS Message: {message}

**TASK**: In a single analysis, determine if this SMS contains financial transaction information AND if yes, extract the transaction details.

**ANALYSIS STEPS**:
1. First, analyze if the SMS contains any financial transaction information (money amounts, spending, receiving, payments, etc.)
2. If it IS a transaction SMS, extract all transaction details
3. If it is NOT a transaction SMS, return a simple response indicating it's not transactional

**RESPONSE FORMAT**:

**For Transactional SMS**, return this JSON structure:
{{
    "is_transaction": true,
    "transaction_type": "credit|debit|payment|spent|received|transfer",
    "amount": <numeric_amount>,
    "currency": "INR",
    "merchant": "<merchant_name_or_recipient>",
    "transaction_date": "<date_in_ISO_format>",
    "reference_number": "<reference_number_if_available>",
    "account_number": "<account_number_if_available>",
    "card_number": "<card_number_if_available>",
    "payment_method": "upi|card|neft|imps|rtgs|cash|wallet",
    "remarks": "<brief_description>",
    "is_failed": <boolean_if_transaction_failed>,
    "bank_name": "<detected_bank_name>",
    "confidence": <number_between_0_and_1>,
    "reason": "<brief_explanation_of_why_it_is_a_transaction>"
}}

**For Non-Transactional SMS**, return this JSON structure:
{{
    "is_transaction": false,
    "confidence": <number_between_0_and_1>,
    "reason": "<brief_explanation_of_why_it_is_not_a_transaction>"
}}

**EXAMPLES**:

**Transactional SMS Example:**
"Rs 500 spent on card at Amazon" → 
{{
    "is_transaction": true,
    "transaction_type": "spent",
    "amount": 500,
    "currency": "INR",
    "merchant": "Amazon",
    "transaction_date": "2025-01-15T12:00:00",
    "payment_method": "card",
    "remarks": "Card transaction at Amazon",
    "is_failed": false,
    "confidence": 0.95,
    "reason": "Contains amount and spending information"
}}

**Non-Transactional SMS Example:**
"Your OTP is 123456" → 
{{
    "is_transaction": false,
    "confidence": 0.9,
    "reason": "OTP message, no transaction details"
}}

**RULES**:
1. Return ONLY the JSON response, no additional text
2. For amounts, extract only the numeric value
3. For dates, convert to ISO format (YYYY-MM-DDTHH:MM:SS) or use current date if not specified
4. For card numbers, extract only the last 4 digits if masked
5. Be flexible with different SMS formats and variations
6. Handle typos and variations in bank SMS formats
7. If unsure about a field, omit it rather than guess
8. This parser works for ANY bank or credit card - be universal

Return only the JSON response, no additional text.
"""

    def _create_backup_file_prompt(self, file_content: str, file_type: str) -> str:
        """Create a prompt for Gemini to parse backup files."""
        return f"""
You are an expert financial data parser. Parse the following {file_type} file content and extract transaction details.

File Content:
{file_content}

Please analyze this {file_type} file and return a JSON array of transactions with the following structure:
[
    {{
        "transaction_type": "credit|debit|payment|spent|received|transfer",
        "amount": <numeric_amount>,
        "currency": "INR",
        "merchant": "<merchant_name>",
        "transaction_date": "<date_in_ISO_format>",
        "reference_number": "<reference_number_if_available>",
        "account_number": "<account_number_if_available>",
        "card_number": "<card_number_if_available>",
        "payment_method": "upi|card|neft|imps|rtgs|cash|wallet",
        "remarks": "<brief_description>",
        "is_failed": <boolean_if_transaction_failed>
    }}
]

Rules:
1. Extract all transactions found in the file
2. For amounts, extract only the numeric value
3. For dates, convert to ISO format (YYYY-MM-DDTHH:MM:SS)
4. Handle different file formats (CSV, XML, PDF text, etc.)
5. Be flexible with different data structures
6. If no transactions found, return empty array []

Return only the JSON array, no additional text.
"""

    async def process_sms_intelligently(self, sender: str, message: str) -> Optional[Dict[str, Any]]:
        """Intelligently process SMS: detect if transactional and parse details in a single AI request."""
        try:
            if not self.use_gemini:
                logger.error("Gemini AI not available. Cannot parse SMS without AI.")
                return None
            
            # Single unified prompt for both detection and parsing
            prompt = self._create_unified_sms_prompt(sender, message)
            
            # Generate response from Gemini
            response = await self.model.generate_content_async(prompt)
            
            if not response.text:
                logger.warning("Empty response from Gemini")
                return None
            
            # Parse JSON response
            try:
                # Clean the response text to extract JSON
                json_text = response.text.strip()
                
                # Remove any markdown formatting
                if json_text.startswith("```json"):
                    json_text = json_text[7:]
                if json_text.endswith("```"):
                    json_text = json_text[:-3]
                
                parsed_data = json.loads(json_text.strip())
                
                # Check if SMS is transactional
                if not parsed_data.get("is_transaction", False):
                    logger.info(f"SMS skipped - not a transaction: {parsed_data.get('reason', 'Unknown')}")
                    return None
                
                logger.info(f"SMS identified as transaction (confidence: {parsed_data.get('confidence', 0)}): {parsed_data.get('reason', 'Unknown')}")
                
                # Validate and convert transaction data
                if "amount" not in parsed_data:
                    logger.warning("Transaction SMS missing amount field")
                    return None
                
                # Convert transaction type
                transaction_type = self._convert_transaction_type(parsed_data.get("transaction_type", ""))
                if not transaction_type:
                    logger.warning("Invalid transaction type")
                    return None
                
                # Convert payment method
                payment_method = self._convert_payment_method(parsed_data.get("payment_method", ""))
                
                # Parse date
                transaction_date = self._parse_date_from_gemini(parsed_data.get("transaction_date", ""))
                if not transaction_date:
                    transaction_date = datetime.utcnow()
                
                return {
                    "transaction_type": transaction_type,
                    "amount": float(parsed_data["amount"]),
                    "currency": parsed_data.get("currency", "INR"),
                    "merchant": parsed_data.get("merchant"),
                    "transaction_date": transaction_date,
                    "reference_number": parsed_data.get("reference_number"),
                    "account_number": parsed_data.get("account_number"),
                    "card_number": parsed_data.get("card_number"),
                    "payment_method": payment_method,
                    "remarks": parsed_data.get("remarks"),
                    "is_failed": parsed_data.get("is_failed", False),
                    "detection_confidence": parsed_data.get("confidence", 0.0),
                    "detection_reason": parsed_data.get("reason", "Unknown")
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini JSON response: {e}")
                logger.error(f"Response text: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error in intelligent SMS processing: {e}")
            return None

    async def parse_backup_file_with_gemini(self, file_content: str, file_type: str) -> List[Dict[str, Any]]:
        """Parse backup file using Gemini AI."""
        try:
            if not self.use_gemini:
                logger.error("Gemini AI not available for backup file parsing")
                return []
            
            prompt = self._create_backup_file_prompt(file_content, file_type)
            
            # Generate response from Gemini
            response = await self.model.generate_content_async(prompt)
            
            if not response.text:
                logger.warning("Empty response from Gemini for backup file")
                return []
            
            # Parse JSON response
            try:
                # Clean the response text to extract JSON
                json_text = response.text.strip()
                
                # Remove any markdown formatting
                if json_text.startswith("```json"):
                    json_text = json_text[7:]
                if json_text.endswith("```"):
                    json_text = json_text[:-3]
                
                transactions_data = json.loads(json_text.strip())
                
                if not isinstance(transactions_data, list):
                    logger.error("Gemini response is not a list of transactions")
                    return []
                
                # Convert and validate each transaction
                valid_transactions = []
                for tx_data in transactions_data:
                    if not tx_data or "amount" not in tx_data:
                        continue
                    
                    # Convert transaction type
                    transaction_type = self._convert_transaction_type(tx_data.get("transaction_type", ""))
                    if not transaction_type:
                        continue
                    
                    # Convert payment method
                    payment_method = self._convert_payment_method(tx_data.get("payment_method", ""))
                    
                    # Parse date
                    transaction_date = self._parse_date_from_gemini(tx_data.get("transaction_date", ""))
                    if not transaction_date:
                        transaction_date = datetime.utcnow()
                    
                    valid_transactions.append({
                        "transaction_type": transaction_type,
                        "amount": float(tx_data["amount"]),
                        "currency": tx_data.get("currency", "INR"),
                        "merchant": tx_data.get("merchant"),
                        "transaction_date": transaction_date,
                        "reference_number": tx_data.get("reference_number"),
                        "account_number": tx_data.get("account_number"),
                        "card_number": tx_data.get("card_number"),
                        "payment_method": payment_method,
                        "remarks": tx_data.get("remarks"),
                        "is_failed": tx_data.get("is_failed", False)
                    })
                
                return valid_transactions
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini JSON response for backup file: {e}")
                logger.error(f"Response text: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error parsing backup file with Gemini: {e}")
            return []

    def _convert_transaction_type(self, type_str: str) -> Optional[TransactionType]:
        """Convert string transaction type to enum."""
        type_mapping = {
            "credit": TransactionType.CREDIT,
            "debit": TransactionType.DEBIT,
            "payment": TransactionType.PAYMENT,
            "spent": TransactionType.SPENT,
            "received": TransactionType.RECEIVED,
            "transfer": TransactionType.TRANSFER
        }
        return type_mapping.get(type_str.lower())

    def _convert_payment_method(self, method_str: str) -> Optional[PaymentMethod]:
        """Convert string payment method to enum."""
        method_mapping = {
            "upi": PaymentMethod.UPI,
            "card": PaymentMethod.CARD,
            "neft": PaymentMethod.NEFT,
            "imps": PaymentMethod.IMPS,
            "rtgs": PaymentMethod.RTGS,
            "cash": PaymentMethod.CASH,
            "wallet": PaymentMethod.WALLET
        }
        return method_mapping.get(method_str.lower())

    def _parse_date_from_gemini(self, date_str: str) -> Optional[datetime]:
        """Parse date string from Gemini response."""
        try:
            # Try to parse ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            # Fallback to current date if parsing fails
            logger.warning(f"Could not parse date from Gemini: {date_str}, using current date")
            return datetime.utcnow()

    def parse_sms(self, sender: str, message: str) -> Optional[Dict[str, Any]]:
        """Parse SMS message and extract transaction information (legacy method)."""
        try:
            # Use intelligent processing
            import asyncio
            return asyncio.run(self.process_sms_intelligently(sender, message))
                
        except Exception as e:
            logger.error(f"Error parsing SMS: {e}")
            return None

    async def parse_sms_async(self, sender: str, message: str) -> Optional[Dict[str, Any]]:
        """Async version of SMS parsing with intelligent detection."""
        try:
            return await self.process_sms_intelligently(sender, message)
                
        except Exception as e:
            logger.error(f"Error parsing SMS: {e}")
            return None

    def is_transaction_sms(self, sender: str, message: str) -> bool:
        """Check if SMS contains transaction information (legacy method)."""
        try:
            import asyncio
            result = asyncio.run(self.process_sms_intelligently(sender, message))
            return result is not None
        except Exception as e:
            logger.error(f"Error checking if SMS is transactional: {e}")
            return False
