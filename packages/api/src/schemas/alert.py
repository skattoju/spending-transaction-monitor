from enum import Enum

from pydantic import BaseModel, Field


class AlertType(str, Enum):
    AMOUNT_THRESHOLD = 'AMOUNT_THRESHOLD'
    MERCHANT_CATEGORY = 'MERCHANT_CATEGORY'
    MERCHANT_NAME = 'MERCHANT_NAME'
    LOCATION_BASED = 'LOCATION_BASED'
    FREQUENCY_BASED = 'FREQUENCY_BASED'
    PATTERN_BASED = 'PATTERN_BASED'
    CUSTOM_QUERY = 'CUSTOM_QUERY'


class NotificationMethod(str, Enum):
    EMAIL = 'EMAIL'
    SMS = 'SMS'
    PUSH = 'PUSH'
    WEBHOOK = 'WEBHOOK'


class NotificationStatus(str, Enum):
    PENDING = 'PENDING'
    SENT = 'SENT'
    DELIVERED = 'DELIVERED'
    FAILED = 'FAILED'
    READ = 'READ'


# Alert Rule Schemas
class AlertRuleBase(BaseModel):
    name: str = Field(..., description='Name of the alert rule')
    description: str | None = Field(None, description='Description of the alert rule')
    isActive: bool = Field(True, description='Whether the alert rule is active')
    alertType: AlertType = Field(..., description='Type of alert')
    amountThreshold: float | None = Field(
        None, description='Amount threshold for amount-based alerts'
    )
    merchantCategory: str | None = Field(
        None, description='Merchant category to monitor'
    )
    merchantName: str | None = Field(None, description='Merchant name to monitor')
    location: str | None = Field(None, description='Location to monitor')
    timeframe: str | None = Field(
        None, description='Timeframe for frequency-based alerts'
    )
    naturalLanguageQuery: str | None = Field(
        None, description='Natural language query for custom alerts'
    )
    sqlQuery: str | None = Field(
        None, description='SQL query generated from natural language query'
    )
    notificationMethods: list[NotificationMethod] | None = Field(
        None, description='Notification methods'
    )


class AlertRuleCreate(AlertRuleBase):
    userId: str = Field(..., description='User ID')


class AlertRuleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    isActive: bool | None = None
    alertType: AlertType | None = None
    amountThreshold: float | None = None
    merchantCategory: str | None = None
    merchantName: str | None = None
    location: str | None = None
    timeframe: str | None = None
    naturalLanguageQuery: str | None = None
    sqlQuery: str | None = None
    notificationMethods: list[NotificationMethod] | None = None


class AlertRuleOut(AlertRuleBase):
    id: str
    userId: str
    createdAt: str
    updatedAt: str
    lastTriggered: str | None = None
    triggerCount: int


# Alert Notification Schemas
class AlertNotificationBase(BaseModel):
    title: str = Field(..., description='Notification title')
    message: str = Field(..., description='Notification message')
    notificationMethod: NotificationMethod = Field(
        ..., description='Method used for notification'
    )
    status: NotificationStatus = Field(..., description='Status of the notification')


class AlertNotificationCreate(AlertNotificationBase):
    userId: str = Field(..., description='User ID')
    alertRuleId: str = Field(..., description='Alert rule ID')
    transactionId: str | None = Field(None, description='Related transaction ID')


class AlertNotificationUpdate(BaseModel):
    title: str | None = None
    message: str | None = None
    notificationMethod: NotificationMethod | None = None
    status: NotificationStatus | None = None
    sentAt: str | None = None
    deliveredAt: str | None = None
    readAt: str | None = None


class AlertNotificationOut(AlertNotificationBase):
    id: str
    userId: str
    alertRuleId: str
    transactionId: str | None = None
    sentAt: str | None = None
    deliveredAt: str | None = None
    readAt: str | None = None
    createdAt: str
    updatedAt: str
