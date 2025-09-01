import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    PAYMENT = "payment"
    TRANSFER = "transfer"
    SPENT = "spent"
    RECEIVED = "received"


class PaymentMethod(str, Enum):
    UPI = "upi"
    CARD = "card"
    NEFT = "neft"
    IMPS = "imps"
    RTGS = "rtgs"
    CASH = "cash"
    WALLET = "wallet"


class SMSMessage(BaseModel):
    id: Optional[str] = None
    user_id: str
    sender: str
    message_text: str
    timestamp: datetime
    parsed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Transaction(BaseModel):
    id: Optional[str] = None
    user_id: str
    sms_message_id: Optional[str] = None
    transaction_type: TransactionType
    amount: float
    currency: str = "INR"
    merchant: Optional[str] = None
    category: Optional[str] = None
    transaction_date: datetime
    reference_number: Optional[str] = None
    account_number: Optional[str] = None
    card_number: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    remarks: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_failed: bool = False
    is_recurring: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @validator('reference_number')
    def validate_reference_number(cls, v):
        if v and not re.match(r'^[A-Za-z0-9]+$', v):
            raise ValueError('Reference number must contain only alphanumeric characters')
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class User(BaseModel):
    id: Optional[str] = None
    firebase_uid: str
    email: str
    phone: Optional[str] = None
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Category(BaseModel):
    id: Optional[str] = None
    user_id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Merchant(BaseModel):
    id: Optional[str] = None
    user_id: str
    name: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SMSRequest(BaseModel):
    sender: str
    message_text: str
    timestamp: datetime


class TransactionCreate(BaseModel):
    transaction_type: TransactionType
    amount: float
    currency: str = "INR"
    merchant: Optional[str] = None
    category: Optional[str] = None
    transaction_date: datetime
    reference_number: Optional[str] = None
    account_number: Optional[str] = None
    card_number: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    remarks: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class TransactionUpdate(BaseModel):
    merchant: Optional[str] = None
    category: Optional[str] = None
    remarks: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class TransactionFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    transaction_type: Optional[TransactionType] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    is_failed: Optional[bool] = None
    tags: Optional[List[str]] = None
    limit: int = 50
    offset: int = 0


class AnalyticsResponse(BaseModel):
    total_transactions: int
    total_amount: float
    average_amount: float
    transaction_count_by_type: Dict[str, int]
    amount_by_type: Dict[str, float]
    top_merchants: List[Dict[str, Any]]
    top_categories: List[Dict[str, Any]]
    monthly_trends: List[Dict[str, Any]]
    failed_transactions: int
    recurring_transactions: int


class ExportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


class BackupFileUpload(BaseModel):
    file_type: str
    file_content: str
    filename: str
