from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from decimal import Decimal
from enum import Enum


class RuleOperator(str, Enum):
    """Supported comparison operators for rule evaluation"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"
    WITHIN_RADIUS = "within_radius"
    OUTSIDE_RADIUS = "outside_radius"


class AlertType(str, Enum):
    """Alert types matching database schema"""
    AMOUNT_THRESHOLD = "AMOUNT_THRESHOLD"
    BALANCE_THRESHOLD = "BALANCE_THRESHOLD"
    MERCHANT_MATCH = "MERCHANT_MATCH"
    CATEGORY_MATCH = "CATEGORY_MATCH"
    LOCATION_BASED = "LOCATION_BASED"
    HISTORICAL_COMPARISON = "HISTORICAL_COMPARISON"
    AGGREGATION_RULE = "AGGREGATION_RULE"
    BEHAVIORAL_ANOMALY = "BEHAVIORAL_ANOMALY"
    COMPOUND_RULE = "COMPOUND_RULE"


class NotificationMethod(str, Enum):
    """Notification methods matching database schema"""
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"


class AggregationType(str, Enum):
    """Types of aggregations for historical data"""
    SUM = "sum"
    COUNT = "count"
    AVERAGE = "average"
    MAX = "max"
    MIN = "min"


class RuleCondition(BaseModel):
    """Individual condition within a rule"""
    field: str = Field(..., description="Field to evaluate (e.g., 'amount', 'merchantName')")
    operator: RuleOperator = Field(..., description="Comparison operator")
    value: Union[str, int, float, Decimal, List[Any]] = Field(..., description="Value to compare against")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional condition metadata")


class HistoricalComparison(BaseModel):
    """Configuration for historical comparison rules"""
    aggregation_type: AggregationType = Field(..., description="Type of aggregation to perform")
    field: str = Field(..., description="Field to aggregate (e.g., 'amount')")
    time_window: str = Field(..., description="Time window (e.g., '30d', '1m', '1y')")
    comparison_operator: RuleOperator = Field(..., description="How to compare current vs historical")
    multiplier: Optional[float] = Field(None, description="Multiplier for comparison (e.g., 2.0 for 'twice as much')")
    category_filter: Optional[str] = Field(None, description="Optional category filter for aggregation")


class LocationRule(BaseModel):
    """Configuration for location-based rules"""
    reference_location: str = Field(..., description="Reference location type ('home', 'last_mobile', 'last_transaction')")
    radius_miles: float = Field(..., gt=0, description="Radius in miles for comparison")
    comparison_type: str = Field(..., description="'within' or 'outside' the radius")


class Rule(BaseModel):
    """Alert rule model aligned with database schema"""
    id: str = Field(..., description="Unique rule identifier")
    userId: str = Field(..., description="User who owns this rule")
    name: str = Field(..., description="Human-readable rule name")
    description: Optional[str] = Field(None, description="Natural language description of the rule")
    alertType: AlertType = Field(..., description="Type of alert rule")
    isActive: bool = Field(default=True, description="Whether the rule is active")
    
    # Condition parameters (matching database schema)
    amountThreshold: Optional[Decimal] = Field(None, description="Amount threshold for alerts")
    merchantCategory: Optional[str] = Field(None, description="Merchant category filter")
    merchantName: Optional[str] = Field(None, description="Merchant name filter")
    location: Optional[str] = Field(None, description="Location filter")
    timeframe: Optional[str] = Field(None, description="Time window for aggregation (e.g., 'daily', 'weekly')")
    
    # Natural language query for AI-driven alerts
    naturalLanguageQuery: Optional[str] = Field(None, description="Natural language query for AI processing")
    
    # Notification preferences
    notificationMethods: List[NotificationMethod] = Field(default=[NotificationMethod.EMAIL], description="Notification methods")
    
    # Additional rule configurations
    conditions: List[RuleCondition] = Field(default_factory=list, description="List of conditions to evaluate")
    priority: int = Field(default=1, description="Rule priority (higher = more important)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Rule creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Optional configurations for specific rule types
    historical_comparison: Optional[HistoricalComparison] = Field(None, description="Historical comparison config")
    location_rule: Optional[LocationRule] = Field(None, description="Location-based rule config")
    compound_rules: Optional[List[str]] = Field(None, description="List of rule IDs for compound rules")
    
    # Notification settings
    notification_template: Optional[str] = Field(None, description="Custom notification template")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional rule metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RuleEvaluationResult(BaseModel):
    """Result of evaluating a rule against a transaction"""
    rule_id: str = Field(..., description="Rule that was evaluated")
    transaction_id: str = Field(..., description="Transaction that was evaluated")
    userId: str = Field(..., description="User ID")
    triggered: bool = Field(..., description="Whether the rule was triggered")
    evaluation_time: datetime = Field(default_factory=datetime.utcnow, description="When evaluation occurred")
    matched_conditions: List[str] = Field(default_factory=list, description="Conditions that matched")
    failed_conditions: List[str] = Field(default_factory=list, description="Conditions that failed")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in the evaluation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional evaluation metadata") 