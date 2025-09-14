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
    is_active: bool = Field(True, description='Whether the alert rule is active')
    alert_type: AlertType = Field(..., description='Type of alert')
    amount_threshold: float | None = Field(
        None, description='Amount threshold for amount-based alerts'
    )
    merchant_category: str | None = Field(
        None, description='Merchant category to monitor'
    )
    merchant_name: str | None = Field(None, description='Merchant name to monitor')
    location: str | None = Field(None, description='Location to monitor')
    timeframe: str | None = Field(
        None, description='Timeframe for frequency-based alerts'
    )
    natural_language_query: str | None = Field(
        None, description='Natural language query for custom alerts'
    )
    sql_query: str | None = Field(
        None, description='SQL query generated from natural language query'
    )
    notification_methods: list[NotificationMethod] | None = Field(
        None, description='Notification methods'
    )


class AlertRuleCreate(AlertRuleBase):
    user_id: str = Field(..., description='User ID')


class AlertRuleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
    alert_type: AlertType | None = None
    amount_threshold: float | None = None
    merchant_category: str | None = None
    merchant_name: str | None = None
    location: str | None = None
    timeframe: str | None = None
    natural_language_query: str | None = None
    sql_query: str | None = None
    notification_methods: list[NotificationMethod] | None = None


class AlertRuleOut(AlertRuleBase):
    id: str
    user_id: str
    created_at: str
    updated_at: str
    last_triggered: str | None = None
    trigger_count: int


# Alert Notification Schemas
class AlertNotificationBase(BaseModel):
    title: str = Field(..., description='Notification title')
    message: str = Field(..., description='Notification message')
    notification_method: NotificationMethod = Field(
        ..., description='Method used for notification'
    )
    status: NotificationStatus = Field(..., description='Status of the notification')


class AlertNotificationCreate(AlertNotificationBase):
    user_id: str = Field(..., description='User ID')
    alert_rule_id: str = Field(..., description='Alert rule ID')
    transaction_id: str | None = Field(None, description='Related transaction ID')


class AlertNotificationUpdate(BaseModel):
    title: str | None = None
    message: str | None = None
    notification_method: NotificationMethod | None = None
    status: NotificationStatus | None = None
    sent_at: str | None = None
    delivered_at: str | None = None
    read_at: str | None = None


class AlertNotificationOut(AlertNotificationBase):
    id: str
    user_id: str
    alert_rule_id: str
    transaction_id: str | None = None
    sent_at: str | None = None
    delivered_at: str | None = None
    read_at: str | None = None
    created_at: str
    updated_at: str
