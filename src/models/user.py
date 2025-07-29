from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from .transaction import Location


class User(BaseModel):
    """User data aligned with database schema"""
    id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="Primary email address")
    firstName: str = Field(..., description="User first name")
    lastName: str = Field(..., description="User last name")
    phoneNumber: Optional[str] = Field(None, description="Phone number")
    
    # Timestamps
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Last profile update")
    isActive: bool = Field(default=True, description="Whether account is active")
    
    # Address information
    addressStreet: Optional[str] = Field(None, description="Street address")
    addressCity: Optional[str] = Field(None, description="City")
    addressState: Optional[str] = Field(None, description="State")
    addressZipCode: Optional[str] = Field(None, description="ZIP code")
    addressCountry: Optional[str] = Field(default="US", description="Country")
    
    # Financial information
    creditLimit: Optional[Decimal] = Field(None, description="Credit limit")
    currentBalance: Optional[Decimal] = Field(default=0.00, description="Current account balance")
    
    # Location tracking (with privacy consent)
    locationConsentGiven: bool = Field(default=False, description="Whether user has given location consent")
    lastAppLocationLatitude: Optional[float] = Field(None, description="Last app location latitude")
    lastAppLocationLongitude: Optional[float] = Field(None, description="Last app location longitude")
    lastAppLocationTimestamp: Optional[datetime] = Field(None, description="Last app location timestamp")
    lastAppLocationAccuracy: Optional[float] = Field(None, description="Location accuracy in meters")
    
    # Last transaction location
    lastTransactionLatitude: Optional[float] = Field(None, description="Last transaction latitude")
    lastTransactionLongitude: Optional[float] = Field(None, description="Last transaction longitude")
    lastTransactionTimestamp: Optional[datetime] = Field(None, description="Last transaction timestamp")
    lastTransactionCity: Optional[str] = Field(None, description="Last transaction city")
    lastTransactionState: Optional[str] = Field(None, description="Last transaction state")
    lastTransactionCountry: Optional[str] = Field(None, description="Last transaction country")
    
    # Preferences
    notification_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {"email": True, "sms": False, "push": False},
        description="Notification channel preferences"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional user metadata")

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class UserBalance(BaseModel):
    """Real-time balance information"""
    userId: str = Field(..., description="User identifier")
    currentBalance: Decimal = Field(..., description="Current balance")
    availableCredit: Optional[Decimal] = Field(None, description="Available credit")
    pendingTransactions: Decimal = Field(default=0, description="Sum of pending transactions")
    lastUpdated: datetime = Field(default_factory=datetime.utcnow, description="Last balance update")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        } 