from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


class TransactionType(str, Enum):
    """Transaction types matching database schema"""
    PURCHASE = "PURCHASE"
    WITHDRAWAL = "WITHDRAWAL"
    REFUND = "REFUND"
    PAYMENT = "PAYMENT"
    FEE = "FEE"


class TransactionStatus(str, Enum):
    """Transaction status matching database schema"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    CANCELLED = "CANCELLED"


class Location(BaseModel):
    """Location coordinates for transactions and users"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None


class Transaction(BaseModel):
    """Credit card transaction model aligned with database schema"""
    id: str = Field(..., description="Unique transaction identifier")
    userId: str = Field(..., description="User identifier")
    creditCardId: str = Field(..., description="Credit card identifier")
    amount: Decimal = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    description: str = Field(..., description="Transaction description")
    merchantName: str = Field(..., description="Merchant name")
    merchantCategory: str = Field(..., description="Merchant category code")
    transactionDate: datetime = Field(..., description="Transaction timestamp")
    transactionType: TransactionType = Field(default=TransactionType.PURCHASE, description="Transaction type")
    
    # Location information
    merchantLocation: Optional[str] = Field(None, description="Merchant location string")
    merchantCity: Optional[str] = Field(None, description="Merchant city")
    merchantState: Optional[str] = Field(None, description="Merchant state")
    merchantCountry: Optional[str] = Field(None, description="Merchant country")
    
    # Processing information
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, description="Transaction status")
    authorizationCode: Optional[str] = Field(None, description="Authorization code")
    referenceNumber: Optional[str] = Field(None, description="Reference number")
    
    # Metadata
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional transaction metadata")

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class TransactionEvent(BaseModel):
    """Event wrapper for transaction processing"""
    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(default="transaction.created", description="Event type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    data: Transaction = Field(..., description="Transaction data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Event metadata") 