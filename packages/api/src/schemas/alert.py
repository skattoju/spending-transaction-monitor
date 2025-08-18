from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class AlertType(str, Enum):
    AMOUNT_THRESHOLD = "AMOUNT_THRESHOLD"
    MERCHANT_CATEGORY = "MERCHANT_CATEGORY"
    MERCHANT_NAME = "MERCHANT_NAME"
    LOCATION_BASED = "LOCATION_BASED"
    FREQUENCY_BASED = "FREQUENCY_BASED"
    PATTERN_BASED = "PATTERN_BASED"
    CUSTOM_QUERY = "CUSTOM_QUERY"


class NotificationMethod(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    WEBHOOK = "WEBHOOK"


class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    READ = "READ"


# Alert Rule Schemas
class AlertRuleBase(BaseModel):
    name: str = Field(..., description="Name of the alert rule")
    description: Optional[str] = Field(None, description="Description of the alert rule")
    isActive: bool = Field(True, description="Whether the alert rule is active")
    alertType: AlertType = Field(..., description="Type of alert")
    amountThreshold: Optional[float] = Field(None, description="Amount threshold for amount-based alerts")
    merchantCategory: Optional[str] = Field(None, description="Merchant category to monitor")
    merchantName: Optional[str] = Field(None, description="Merchant name to monitor")
    location: Optional[str] = Field(None, description="Location to monitor")
    timeframe: Optional[str] = Field(None, description="Timeframe for frequency-based alerts")
    naturalLanguageQuery: Optional[str] = Field(None, description="Natural language query for custom alerts")
    sqlQuery: Optional[str] = Field(None, description="SQL query generated from natural language query")
    notificationMethods: Optional[List[NotificationMethod]] = Field(None, description="Notification methods")


class AlertRuleCreate(AlertRuleBase):
    userId: str = Field(..., description="User ID")


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    isActive: Optional[bool] = None
    alertType: Optional[AlertType] = None
    amountThreshold: Optional[float] = None
    merchantCategory: Optional[str] = None
    merchantName: Optional[str] = None
    location: Optional[str] = None
    timeframe: Optional[str] = None
    naturalLanguageQuery: Optional[str] = None
    sqlQuery: Optional[str] = None
    notificationMethods: Optional[List[NotificationMethod]] = None


class AlertRuleOut(AlertRuleBase):
    id: str
    userId: str
    createdAt: str
    updatedAt: str
    lastTriggered: Optional[str] = None
    triggerCount: int


# Alert Notification Schemas
class AlertNotificationBase(BaseModel):
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    notificationMethod: NotificationMethod = Field(..., description="Method used for notification")
    status: NotificationStatus = Field(..., description="Status of the notification")


class AlertNotificationCreate(AlertNotificationBase):
    userId: str = Field(..., description="User ID")
    alertRuleId: str = Field(..., description="Alert rule ID")
    transactionId: Optional[str] = Field(None, description="Related transaction ID")


class AlertNotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    notificationMethod: Optional[NotificationMethod] = None
    status: Optional[NotificationStatus] = None
    sentAt: Optional[str] = None
    deliveredAt: Optional[str] = None
    readAt: Optional[str] = None


class AlertNotificationOut(AlertNotificationBase):
    id: str
    userId: str
    alertRuleId: str
    transactionId: Optional[str] = None
    sentAt: Optional[str] = None
    deliveredAt: Optional[str] = None
    readAt: Optional[str] = None
    createdAt: str
    updatedAt: str

