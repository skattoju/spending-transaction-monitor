from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class Location(BaseModel):
    """Location coordinates for transactions and users"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None


class Transaction(BaseModel):
    """Credit card transaction model"""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    customer_id: str = Field(..., description="Customer identifier")
    amount: Decimal = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    merchant_name: str = Field(..., description="Merchant name")
    merchant_category: str = Field(..., description="Merchant category code")
    transaction_type: str = Field(..., description="Transaction type (online, in-person)")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    location: Optional[Location] = Field(None, description="Merchant location for in-person transactions")
    card_id: Optional[str] = Field(None, description="Card identifier")
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