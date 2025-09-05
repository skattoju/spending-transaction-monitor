"""
SQLAlchemy ORM models mirroring the former Prisma schema
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class TransactionType(str, Enum):
    PURCHASE = "PURCHASE"
    REFUND = "REFUND"
    CASHBACK = "CASHBACK"
    FEE = "FEE"
    INTEREST = "INTEREST"
    PAYMENT = "PAYMENT"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    CANCELLED = "CANCELLED"
    SETTLED = "SETTLED"


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


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))

    # Address
    address_street: Mapped[Optional[str]]
    address_city: Mapped[Optional[str]]
    address_state: Mapped[Optional[str]]
    address_zipcode: Mapped[Optional[str]]
    address_country: Mapped[Optional[str]] = mapped_column(String, server_default=text("'US'"))

    # Financial
    credit_limit: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    credit_balance: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), server_default=text("0.00"))

    # Location tracking
    location_consent_given: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    last_app_location_latitude: Mapped[Optional[float]] = mapped_column(Float)
    last_app_location_longitude: Mapped[Optional[float]] = mapped_column(Float)
    last_app_location_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_app_location_accuracy: Mapped[Optional[float]] = mapped_column(Float)

    # Last transaction location
    last_transaction_latitude: Mapped[Optional[float]] = mapped_column(Float)
    last_transaction_longitude: Mapped[Optional[float]] = mapped_column(Float)
    last_transaction_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_transaction_city: Mapped[Optional[str]]
    last_transaction_state: Mapped[Optional[str]]
    last_transaction_country: Mapped[Optional[str]]

    # Relationships
    creditCards: Mapped[List["CreditCard"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    alertRules: Mapped[List["AlertRule"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    alertNotifications: Mapped[List["AlertNotification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_users_city_state", "address_city", "address_state"),
        Index("ix_users_location_consent", "location_consent_given"),
    )


class CreditCard(Base):
    __tablename__ = "credit_cards"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    card_number: Mapped[str] = mapped_column(String, nullable=False)
    card_type: Mapped[str] = mapped_column(String, nullable=False)
    bank_name: Mapped[str] = mapped_column(String, nullable=False)
    card_holder_name: Mapped[str] = mapped_column(String, nullable=False)
    expiry_month: Mapped[int] = mapped_column(Integer, nullable=False)
    expiry_year: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="creditCards")
    #transactions: Mapped[List["Transaction"]] = relationship(back_populates="creditCard")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    #credit_card_num: Mapped[str] = mapped_column(ForeignKey("credit_cards.id", ondelete="CASCADE"))
    credit_card_num: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String, server_default=text("'USD'"))
    description: Mapped[str] = mapped_column(String, nullable=False)
    merchant_name: Mapped[str] = mapped_column(String, nullable=False)
    merchant_category: Mapped[str] = mapped_column(String, nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(
        SAEnum(TransactionType, name='transaction_type'), server_default=text("'PURCHASE'")
    )

    merchant_latitude: Mapped[Optional[float]]
    merchant_longitude: Mapped[Optional[float]]
    merchant_zipcode: Mapped[Optional[str]]
    merchant_city: Mapped[Optional[str]]
    merchant_state: Mapped[Optional[str]]
    merchant_country: Mapped[Optional[str]]

    status: Mapped[TransactionStatus] = mapped_column(
        SAEnum(TransactionStatus, name='transactionstatus'), server_default=text("'PENDING'"), nullable=False
    )
    authorization_code: Mapped[Optional[str]]
    trans_num: Mapped[Optional[str]]

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="transactions")
    #creditCard: Mapped[CreditCard] = relationship(back_populates="transactions")
    alertNotifications: Mapped[List["AlertNotification"]] = relationship(back_populates="transaction")

    __table_args__ = (
        Index("ix_transactions_user_date", "user_id", "transaction_date"),
        Index("ix_transactions_category", "merchant_category"),
        Index("ix_transactions_amount", "amount"),
    )


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]]
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    alert_type: Mapped[AlertType] = mapped_column(SAEnum(AlertType, name='alert_type'), nullable=False)

    amount_threshold: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    merchant_category: Mapped[Optional[str]]
    merchant_name: Mapped[Optional[str]]
    location: Mapped[Optional[str]]
    timeframe: Mapped[Optional[str]]

    natural_language_query: Mapped[Optional[str]]
    sqlQuery: Mapped[Optional[str]]

    notification_methods: Mapped[Optional[List[NotificationMethod]]] = mapped_column(
        ARRAY(SAEnum(NotificationMethod, name='notification_method')), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_triggered: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    trigger_count: Mapped[int] = mapped_column(Integer, server_default=text("0"))

    user: Mapped[User] = relationship(back_populates="alertRules")
    alertNotifications: Mapped[List["AlertNotification"]] = relationship(
        back_populates="alertRule"
    )

    __table_args__ = (Index("ix_alert_rules_user_active", "user_id", "is_active"),)


class AlertNotification(Base):
    __tablename__ = "alert_notifications"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    alert_rule_id: Mapped[str] = mapped_column(ForeignKey("alert_rules.id", ondelete="CASCADE"))
    transaction_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    notification_method: Mapped[NotificationMethod] = mapped_column(
        SAEnum(NotificationMethod, name='notification_method'), nullable=False
    )
    status: Mapped[NotificationStatus] = mapped_column(
        SAEnum(NotificationStatus, name='notificationstatus'), server_default=text("'PENDING'"), nullable=False
    )

    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="alertNotifications")
    alertRule: Mapped[AlertRule] = relationship(back_populates="alertNotifications")
    transaction: Mapped[Optional[Transaction]] = relationship(back_populates="alertNotifications")


