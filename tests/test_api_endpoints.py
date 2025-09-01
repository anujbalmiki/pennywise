#!/usr/bin/env python3
"""
Test script for Pennywise SMS Parsing API endpoints.
This script tests the AI-powered SMS parsing with real example messages.
"""

import asyncio
import json
import time
from typing import Any, Dict, List

import requests

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = b'eyJhbGciOiAiUlMyNTYiLCAidHlwIjogIkpXVCIsICJraWQiOiAiNDk1NzNiY2VkNzQ0ODBiYTM3MWE4NmE3YTZkMWY5ODc2NGRiMWVkYiJ9.eyJpc3MiOiAiZmlyZWJhc2UtYWRtaW5zZGstZmJzdmNAcGVubnl3aXNlLWFiLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwgInN1YiI6ICJmaXJlYmFzZS1hZG1pbnNkay1mYnN2Y0BwZW5ueXdpc2UtYWIuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLCAiYXVkIjogImh0dHBzOi8vaWRlbnRpdHl0b29sa2l0Lmdvb2dsZWFwaXMuY29tL2dvb2dsZS5pZGVudGl0eS5pZGVudGl0eXRvb2xraXQudjEuSWRlbnRpdHlUb29sa2l0IiwgInVpZCI6ICJ0ZXN0X3VzZXJfMTIzIiwgImlhdCI6IDE3NTY3NTQ4MzQsICJleHAiOiAxNzU2NzU4NDM0fQ.EsUyyQATZss_u8eabCq5urRUIGbiB47c35N4s4dCGTVoRQ4Zq84ZkUr53Tr2D9P0xlzP7pT3vTeRQgCHUkmZIjJwxC2I2fKRLjf2itZFfzuyfS5GiCy7h2aRaQIhFqVxWZR-cth6V8RyQI2Ta1Y9yDBfsnlVu-9b7UKEhkgGfZp-dQFwe9FDIxMe4ICfjd5dj98f6d2n0_sKYNpMUOpwUrYbM96zDu3x2YO6GwLKQfYxC2QXWwUqMiU3cewTmh_Es31r1SuDCF_ywJbU8_W25xWIyNiunWOQEWBIgw4vMidECOGCgWpI1XC3VinBdMKwsX_-IHCYp4rUt4MkVZz9SA' # Replace with actual Firebase ID token

# Test SMS messages from different banks and credit cards
TEST_SMS_MESSAGES = [
    # Federal Bank UPI Debit
    {
        "sender": "AX-FEDBNK-S",
        "message": "Rs 10.00 sent via UPI on 25-08-2025 17:42:18 to IRCTC UTS Ref No. 560316544643",
        "expected_type": "debit",
        "expected_amount": 10.0,
        "expected_merchant": "IRCTC UTS"
    },
    
    # Federal Bank UPI Credit
    {
        "sender": "AX-FEDBNK-S", 
        "message": "Rs 50.00 received via UPI on 30-08-2025 22:42:51 from JADEJA MAYABA Ref No. 560803433208",
        "expected_type": "credit",
        "expected_amount": 50.0,
        "expected_merchant": "JADEJA MAYABA"
    },
    
    # SBI Card Spent
    {
        "sender": "VM-SBICRD-S",
        "message": "Rs.548.00 spent on your SBI Credit Card ending with 2985 at Airtel on 24-08-25 via UPI (Ref No. 560205419474)",
        "expected_type": "spent",
        "expected_amount": 548.0,
        "expected_merchant": "Airtel"
    },
    
    # SBI UPI Credit
    {
        "sender": "VM-SBIUPI-S",
        "message": "Dear SBI User, your A/c X6729-credited by Rs.3000 on 12Aug25 transfer from MONI Ref No 559001831699 -SBI",
        "expected_type": "credit",
        "expected_amount": 3000.0,
        "expected_merchant": "MONI"
    },
    
    # Axis Bank Spent
    {
        "sender": "AX-AXISBK-S",
        "message": "Spent Card no. XX7613 INR 506.22 21-08-25 23:10:52 Hostinger P Avl Lmt INR 20614.3",
        "expected_type": "spent",
        "expected_amount": 506.22,
        "expected_merchant": "Hostinger P"
    },
    
    # OneCard Spent
    {
        "sender": "CP-OneCrd-S",
        "message": "You've hand-picked groceries for Rs. 6,421.10 at Avenue Supermarts, Navi Mumbai on card ending XX0174 & earned some reward points",
        "expected_type": "spent",
        "expected_amount": 6421.10,
        "expected_merchant": "Avenue Supermarts, Navi Mumbai"
    },
    
    # Non-transactional SMS (should be skipped)
    {
        "sender": "AX-FEDBNK-S",
        "message": "Your OTP for transaction is 123456. Valid for 10 minutes. Do not share with anyone.",
        "expected_type": None,  # Should be skipped
        "expected_amount": None,
        "expected_merchant": None
    },
    
    # HDFC Bank (new bank format)
    {
        "sender": "HDFCBANK",
        "message": "Rs.1500.00 debited from A/c XX1234 on 15-01-2025 at 14:30:15 for payment to AMAZON. Ref No: 987654321",
        "expected_type": "debit",
        "expected_amount": 1500.0,
        "expected_merchant": "AMAZON"
    },
    
    # ICICI Bank (another new format)
    {
        "sender": "ICICIB",
        "message": "Your ICICI Bank Credit Card XX5678 has been charged Rs.2500.00 at FLIPKART on 16-01-2025. Available limit: Rs.75000",
        "expected_type": "spent",
        "expected_amount": 2500.0,
        "expected_merchant": "FLIPKART"
    }
]

# Non-transactional SMS messages (should all be skipped)
NON_TRANSACTIONAL_SMS = [
    {
        "sender": "AX-FEDBNK-S",
        "message": "Your account has been successfully linked with UPI ID user@federalbank"
    },
    {
        "sender": "VM-SBICRD-S", 
        "message": "Your SBI Credit Card statement for Jan 2025 is ready. View at sbi.co.in"
    },
    {
        "sender": "AX-AXISBK-S",
        "message": "Your Axis Bank Credit Card XX1234 is due for renewal. Call 1800-419-5577"
    },
    {
        "sender": "CP-OneCrd-S",
        "message": "Welcome to OneCard! Your card is now active. Set PIN at onecard.co.in"
    }
]


class APITester:
    """Test the SMS parsing API endpoints."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.test_user_id = "test_user_123"
    
    def test_health_endpoint(self) -> bool:
        """Test the health endpoint."""
        print("�� Testing Health Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data.get('status', 'Unknown')}")
                print(f"   Gemini AI Status: {data.get('gemini_ai_status', 'Unknown')}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_root_endpoint(self) -> bool:
        """Test the root endpoint."""
        print("\n🏠 Testing Root Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Root endpoint working: {data.get('name', 'Unknown')}")
                print(f"   Version: {data.get('version', 'Unknown')}")
                print(f"   Features: {', '.join(data.get('features', []))}")
                return True
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            return False
    
    def test_sms_parsing_endpoint(self, sender: str, message: str, expected: Dict[str, Any]) -> bool:
        """Test the SMS parsing endpoint."""
        print(f"\n📱 Testing SMS Parsing: {sender}")
        print(f"   Message: {message[:80]}{'...' if len(message) > 80 else ''}")
        
        try:
            # Test the SMS processing endpoint
            payload = {
                "sender": sender,
                "message": message,
                "timestamp": "2025-01-15T12:00:00Z"
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/sms/",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if expected["expected_type"] is None:
                    # This should be a non-transactional SMS
                    if data.get("transaction") is None:
                        print(f"✅ Non-transactional SMS correctly skipped")
                        return True
                    else:
                        print(f"❌ Non-transactional SMS should have been skipped")
                        return False
                else:
                    # This should be a transactional SMS
                    transaction = data.get("transaction")
                    if transaction:
                        print(f"✅ Transaction parsed successfully!")
                        print(f"   Type: {transaction.get('transaction_type')}")
                        print(f"   Amount: {transaction.get('amount')}")
                        print(f"   Merchant: {transaction.get('merchant')}")
                        print(f"   Confidence: {transaction.get('detection_confidence', 'N/A')}")
                        print(f"   Reason: {transaction.get('detection_reason', 'N/A')}")
                        
                        # Basic validation
                        if (transaction.get('transaction_type') == expected["expected_type"] and
                            abs(transaction.get('amount', 0) - expected["expected_amount"]) < 0.01):
                            return True
                        else:
                            print(f"❌ Parsed data doesn't match expected values")
                            return False
                    else:
                        print(f"❌ No transaction data returned")
                        return False
                        
            elif response.status_code == 401:
                print(f"❌ Authentication failed - check your Firebase ID token")
                return False
            else:
                print(f"❌ SMS processing failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ SMS parsing error: {e}")
            return False
    
    def test_backup_file_parsing(self) -> bool:
        """Test the backup file parsing endpoint."""
        print(f"\n📁 Testing Backup File Parsing...")
        
        # Create a sample CSV content
        csv_content = """Transaction,Amount,Merchant,Date
Spent,500,Amazon,2025-01-15
Received,1000,Salary,2025-01-15
Spent,250,Netflix,2025-01-14"""
        
        try:
            payload = {
                "file_content": csv_content,
                "file_type": "csv",
                "filename": "test_transactions.csv"
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/backup/upload",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backup file processed successfully!")
                print(f"   Transactions found: {data.get('transactions_processed', 0)}")
                return True
            else:
                print(f"❌ Backup file processing failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Backup file parsing error: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all API tests."""
        print("�� Starting Pennywise API Endpoint Tests")
        print("=" * 50)
        
        results = {}
        
        # Test basic endpoints
        results["health"] = self.test_health_endpoint()
        results["root"] = self.test_root_endpoint()
        
        # Test SMS parsing with various bank formats
        print(f"\n📱 Testing SMS Parsing ({len(TEST_SMS_MESSAGES)} messages)...")
        sms_success_count = 0
        
        for i, test_case in enumerate(TEST_SMS_MESSAGES, 1):
            test_name = f"sms_{i}_{test_case['sender']}"
            success = self.test_sms_parsing_endpoint(
                test_case["sender"], 
                test_case["message"], 
                test_case
            )
            results[test_name] = success
            if success:
                sms_success_count += 1
        
        # Test non-transactional SMS
        print(f"\n🚫 Testing Non-Transactional SMS ({len(NON_TRANSACTIONAL_SMS)} messages)...")
        non_tx_success_count = 0
        
        for i, test_case in enumerate(NON_TRANSACTIONAL_SMS, 1):
            test_name = f"non_tx_{i}_{test_case['sender']}"
            success = self.test_sms_parsing_endpoint(
                test_case["sender"],
                test_case["message"],
                {"expected_type": None, "expected_amount": None, "expected_merchant": "None"}
            )
            results[test_name] = success
            if success:
                non_tx_success_count += 1
        
        # Test backup file parsing
        results["backup_file"] = self.test_backup_file_parsing()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\nSMS Parsing Tests: {sms_success_count}/{len(TEST_SMS_MESSAGES)} passed")
        print(f"Non-Transactional Tests: {non_tx_success_count}/{len(NON_TRANSACTIONAL_SMS)} passed")
        
        if results["health"] and results["root"]:
            print(f"\n✅ Basic API endpoints working")
        else:
            print(f"\n❌ Basic API endpoints have issues")
        
        if results["backup_file"]:
            print(f"✅ Backup file processing working")
        else:
            print(f"❌ Backup file processing has issues")
        
        return results


def main():
    """Main function to run the API tests."""
    print("Pennywise SMS Parsing API Test Script")
    print("=" * 50)
    
    # Check if API key is provided
    if API_KEY == "your_firebase_id_token_here":
        print("❌ Please update the API_KEY variable with your actual Firebase ID token")
        print("   You can get this from your mobile app or Firebase console")
        return
    
    # Create tester and run tests
    tester = APITester(BASE_URL, API_KEY)
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if all(results.values()):
        print("\n🎉 All tests passed! Your Pennywise API is working perfectly!")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        exit(1)


if __name__ == "__main__":
    main()