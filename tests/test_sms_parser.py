from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from app.models import PaymentMethod, TransactionType
from app.services.sms_parser import SMSParser


class TestSMSParser:
    """Test cases for AI-powered SMS parser service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock the Gemini API key for testing
        with patch('app.services.sms_parser.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_api_key"
            self.parser = SMSParser()
    
    def test_init_with_gemini_api_key(self):
        """Test initialization with Gemini API key."""
        with patch('app.services.sms_parser.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_key"
            parser = SMSParser()
            assert parser.use_gemini is True
            assert parser.model is not None
    
    def test_init_without_gemini_api_key(self):
        """Test initialization without Gemini API key raises error."""
        with patch('app.services.sms_parser.settings') as mock_settings:
            mock_settings.gemini_api_key = None
            with pytest.raises(ValueError, match="Gemini API key is required for SMS parsing"):
                SMSParser()
    
    @pytest.mark.asyncio
    async def test_process_sms_intelligently_transactional(self):
        """Test intelligent SMS processing for transactional SMS."""
        # Mock Gemini response for transactional SMS
        mock_response = AsyncMock()
        mock_response.text = '''
        {
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
        }
        '''
        
        with patch.object(self.parser.model, 'generate_content_async', return_value=mock_response):
            result = await self.parser.process_sms_intelligently("TEST-BANK", "Rs 500 spent on card at Amazon")
            
            assert result is not None
            assert result["transaction_type"] == TransactionType.SPENT
            assert result["amount"] == 500.0
            assert result["merchant"] == "Amazon"
            assert result["payment_method"] == PaymentMethod.CARD
            assert result["detection_confidence"] == 0.95
            assert result["detection_reason"] == "Contains amount and spending information"
    
    @pytest.mark.asyncio
    async def test_process_sms_intelligently_non_transactional(self):
        """Test intelligent SMS processing for non-transactional SMS."""
        # Mock Gemini response for non-transactional SMS
        mock_response = AsyncMock()
        mock_response.text = '''
        {
            "is_transaction": false,
            "confidence": 0.9,
            "reason": "OTP message, no transaction details"
        }
        '''
        
        with patch.object(self.parser.model, 'generate_content_async', return_value=mock_response):
            result = await self.parser.process_sms_intelligently("TEST-BANK", "Your OTP is 123456")
            
            assert result is None  # Non-transactional SMS should return None
    
    @pytest.mark.asyncio
    async def test_process_sms_intelligently_missing_amount(self):
        """Test intelligent SMS processing for SMS missing amount field."""
        # Mock Gemini response missing amount
        mock_response = AsyncMock()
        mock_response.text = '''
        {
            "is_transaction": true,
            "transaction_type": "spent",
            "currency": "INR",
            "merchant": "Amazon",
            "confidence": 0.8,
            "reason": "Contains spending information"
        }
        '''
        
        with patch.object(self.parser.model, 'generate_content_async', return_value=mock_response):
            result = await self.parser.process_sms_intelligently("TEST-BANK", "Spent at Amazon")
            
            assert result is None  # Missing amount should return None
    
    @pytest.mark.asyncio
    async def test_process_sms_intelligently_invalid_transaction_type(self):
        """Test intelligent SMS processing for invalid transaction type."""
        # Mock Gemini response with invalid transaction type
        mock_response = AsyncMock()
        mock_response.text = '''
        {
            "is_transaction": true,
            "transaction_type": "invalid_type",
            "amount": 500,
            "currency": "INR",
            "merchant": "Amazon",
            "confidence": 0.8,
            "reason": "Contains spending information"
        }
        '''
        
        with patch.object(self.parser.model, 'generate_content_async', return_value=mock_response):
            result = await self.parser.process_sms_intelligently("TEST-BANK", "Spent at Amazon")
            
            assert result is None  # Invalid transaction type should return None
    
    @pytest.mark.asyncio
    async def test_process_sms_intelligently_empty_response(self):
        """Test intelligent SMS processing with empty Gemini response."""
        mock_response = AsyncMock()
        mock_response.text = ""
        
        with patch.object(self.parser.model, 'generate_content_async', return_value=mock_response):
            result = await self.parser.process_sms_intelligently("TEST-BANK", "Test message")
            
            assert result is None  # Empty response should return None
    
    @pytest.mark.asyncio
    async def test_process_sms_intelligently_json_error(self):
        """Test intelligent SMS processing with invalid JSON response."""
        mock_response = AsyncMock()
        mock_response.text = "Invalid JSON response"
        
        with patch.object(self.parser.model, 'generate_content_async', return_value=mock_response):
            result = await self.parser.process_sms_intelligently("TEST-BANK", "Test message")
            
            assert result is None  # Invalid JSON should return None
    
    @pytest.mark.asyncio
    async def test_parse_backup_file_with_gemini(self):
        """Test backup file parsing with Gemini AI."""
        file_content = "Transaction,Amount,Merchant\nSpent,500,Amazon\nReceived,1000,Salary"
        file_type = "csv"
        
        # Mock Gemini response for backup file
        mock_response = AsyncMock()
        mock_response.text = '''
        [
            {
                "transaction_type": "spent",
                "amount": 500,
                "currency": "INR",
                "merchant": "Amazon",
                "transaction_date": "2025-01-15T12:00:00",
                "payment_method": "card",
                "remarks": "Online purchase"
            },
            {
                "transaction_type": "received",
                "amount": 1000,
                "currency": "INR",
                "merchant": "Salary",
                "transaction_date": "2025-01-15T09:00:00",
                "payment_method": "neft",
                "remarks": "Monthly salary"
            }
        ]
        '''
        
        with patch.object(self.parser.model, 'generate_content_async', return_value=mock_response):
            result = await self.parser.parse_backup_file_with_gemini(file_content, file_type)
            
            assert len(result) == 2
            assert result[0]["transaction_type"] == TransactionType.SPENT
            assert result[0]["amount"] == 500.0
            assert result[0]["merchant"] == "Amazon"
            assert result[1]["transaction_type"] == TransactionType.RECEIVED
            assert result[1]["amount"] == 1000.0
            assert result[1]["merchant"] == "Salary"
    
    def test_convert_transaction_type(self):
        """Test transaction type conversion."""
        assert self.parser._convert_transaction_type("credit") == TransactionType.CREDIT
        assert self.parser._convert_transaction_type("debit") == TransactionType.DEBIT
        assert self.parser._convert_transaction_type("spent") == TransactionType.SPENT
        assert self.parser._convert_transaction_type("received") == TransactionType.RECEIVED
        assert self.parser._convert_transaction_type("invalid") is None
    
    def test_convert_payment_method(self):
        """Test payment method conversion."""
        assert self.parser._convert_payment_method("upi") == PaymentMethod.UPI
        assert self.parser._convert_payment_method("card") == PaymentMethod.CARD
        assert self.parser._convert_payment_method("neft") == PaymentMethod.NEFT
        assert self.parser._convert_payment_method("invalid") is None
    
    def test_parse_date_from_gemini_valid_iso(self):
        """Test date parsing from Gemini with valid ISO format."""
        date_str = "2025-01-15T12:00:00"
        result = self.parser._parse_date_from_gemini(date_str)
        
        assert result == datetime(2025, 1, 15, 12, 0, 0)
    
    def test_parse_date_from_gemini_invalid_format(self):
        """Test date parsing from Gemini with invalid format."""
        date_str = "invalid-date"
        result = self.parser._parse_date_from_gemini(date_str)
        
        # Should return current date as fallback
        assert isinstance(result, datetime)
    
    def test_parse_sms_legacy_method(self):
        """Test legacy parse_sms method."""
        # Mock Gemini response
        mock_response = AsyncMock()
        mock_response.text = '''
        {
            "is_transaction": true,
            "transaction_type": "spent",
            "amount": 500,
            "currency": "INR",
            "merchant": "Amazon",
            "payment_method": "card",
            "confidence": 0.9,
            "reason": "Contains spending information"
        }
        '''
        
        with patch.object(self.parser.model, 'generate_content_async', return_value=mock_response):
            result = self.parser.parse_sms("TEST-BANK", "Rs 500 spent at Amazon")
            
            assert result is not None
            assert result["transaction_type"] == TransactionType.SPENT
            assert result["amount"] == 500.0
    
    @pytest.mark.asyncio
    async def test_parse_sms_async(self):
        """Test async parse_sms_async method."""
        # Mock Gemini response
        mock_response = AsyncMock()
        mock_response.text = '''
        {
            "is_transaction": true,
            "transaction_type": "spent",
            "amount": 500,
            "currency": "INR",
            "merchant": "Amazon",
            "payment_method": "card",
            "confidence": 0.9,
            "reason": "Contains spending information"
        }
        '''
        
        with patch.object(self.parser.model, 'generate_content_async', return_value=mock_response):
            result = await self.parser.parse_sms_async("TEST-BANK", "Rs 500 spent at Amazon")
            
            assert result is not None
            assert result["transaction_type"] == TransactionType.SPENT
            assert result["amount"] == 500.0
    
    def test_is_transaction_sms_legacy_method(self):
        """Test legacy is_transaction_sms method."""
        # Mock Gemini response
        mock_response = AsyncMock()
        mock_response.text = '''
        {
            "is_transaction": true,
            "transaction_type": "spent",
            "amount": 500,
            "currency": "INR",
            "merchant": "Amazon",
            "payment_method": "card",
            "confidence": 0.9,
            "reason": "Contains spending information"
        }
        '''
        
        with patch.object(self.parser.model, 'generate_content_async', return_value=mock_response):
            result = self.parser.is_transaction_sms("TEST-BANK", "Rs 500 spent at Amazon")
            
            assert result is True
