from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from .transaction import Location


class UserProfile(BaseModel):
    """User profile data needed for rule evaluation"""
    customer_id: str = Field(..., description="Unique customer identifier")
    first_name: str = Field(..., description="Customer first name")
    last_name: str = Field(..., description="Customer last name")
    email: str = Field(..., description="Primary email address")
    phone: Optional[str] = Field(None, description="Phone number")
    
    # Financial data
    current_balance: Decimal = Field(..., description="Current account balance")
    credit_limit: Decimal = Field(..., description="Credit limit")
    available_credit: Decimal = Field(..., description="Available credit")
    
    # Location data
    home_address: Optional[str] = Field(None, description="Home address")
    home_location: Optional[Location] = Field(None, description="Home coordinates")
    last_mobile_location: Optional[Location] = Field(None, description="Last known mobile app location")
    last_transaction_location: Optional[Location] = Field(None, description="Location of last transaction")
    
    # Preferences
    notification_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {"email": True, "sms": False, "push": False},
        description="Notification channel preferences"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last profile update")
    is_active: bool = Field(default=True, description="Whether account is active")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional user metadata")

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class UserBalance(BaseModel):
    """Real-time balance information"""
    customer_id: str = Field(..., description="Customer identifier")
    current_balance: Decimal = Field(..., description="Current balance")
    available_credit: Decimal = Field(..., description="Available credit")
    pending_transactions: Decimal = Field(default=0, description="Sum of pending transactions")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last balance update")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        } 