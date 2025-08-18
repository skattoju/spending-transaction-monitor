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
    firstName: Mapped[str] = mapped_column(String, nullable=False)
    lastName: Mapped[str] = mapped_column(String, nullable=False)
    phoneNumber: Mapped[Optional[str]]
    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    isActive: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))

    # Address
    addressStreet: Mapped[Optional[str]]
    addressCity: Mapped[Optional[str]]
    addressState: Mapped[Optional[str]]
    addressZipCode: Mapped[Optional[str]]
    addressCountry: Mapped[Optional[str]] = mapped_column(String, server_default=text("'US'"))

    # Financial
    creditLimit: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    currentBalance: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), server_default=text("0.00"))

    # Location tracking
    locationConsentGiven: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    lastAppLocationLatitude: Mapped[Optional[float]] = mapped_column(Float)
    lastAppLocationLongitude: Mapped[Optional[float]] = mapped_column(Float)
    lastAppLocationTimestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    lastAppLocationAccuracy: Mapped[Optional[float]] = mapped_column(Float)

    # Last transaction location
    lastTransactionLatitude: Mapped[Optional[float]] = mapped_column(Float)
    lastTransactionLongitude: Mapped[Optional[float]] = mapped_column(Float)
    lastTransactionTimestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    lastTransactionCity: Mapped[Optional[str]]
    lastTransactionState: Mapped[Optional[str]]
    lastTransactionCountry: Mapped[Optional[str]]

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
        Index("ix_users_city_state", "addressCity", "addressState"),
        Index("ix_users_location_consent", "locationConsentGiven"),
    )


class CreditCard(Base):
    __tablename__ = "credit_cards"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    userId: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    cardNumber: Mapped[str] = mapped_column(String, nullable=False)
    cardType: Mapped[str] = mapped_column(String, nullable=False)
    bankName: Mapped[str] = mapped_column(String, nullable=False)
    cardHolderName: Mapped[str] = mapped_column(String, nullable=False)
    expiryMonth: Mapped[int] = mapped_column(Integer, nullable=False)
    expiryYear: Mapped[int] = mapped_column(Integer, nullable=False)
    isActive: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="creditCards")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="creditCard")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    userId: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    creditCardId: Mapped[str] = mapped_column(ForeignKey("credit_cards.id", ondelete="CASCADE"))

    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String, server_default=text("'USD'"))
    description: Mapped[str] = mapped_column(String, nullable=False)
    merchantName: Mapped[str] = mapped_column(String, nullable=False)
    merchantCategory: Mapped[str] = mapped_column(String, nullable=False)
    transactionDate: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    transactionType: Mapped[TransactionType] = mapped_column(
        SAEnum(TransactionType), server_default=text("'PURCHASE'")
    )

    merchantLocation: Mapped[Optional[str]]
    merchantCity: Mapped[Optional[str]]
    merchantState: Mapped[Optional[str]]
    merchantCountry: Mapped[Optional[str]]

    status: Mapped[TransactionStatus] = mapped_column(
        SAEnum(TransactionStatus), server_default=text("'PENDING'"), nullable=False
    )
    authorizationCode: Mapped[Optional[str]]
    referenceNumber: Mapped[Optional[str]]

    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="transactions")
    creditCard: Mapped[CreditCard] = relationship(back_populates="transactions")
    alertNotifications: Mapped[List["AlertNotification"]] = relationship(back_populates="transaction")

    __table_args__ = (
        Index("ix_transactions_user_date", "userId", "transactionDate"),
        Index("ix_transactions_category", "merchantCategory"),
        Index("ix_transactions_amount", "amount"),
    )


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    userId: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]]
    isActive: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    alertType: Mapped[AlertType] = mapped_column(SAEnum(AlertType), nullable=False)

    amountThreshold: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    merchantCategory: Mapped[Optional[str]]
    merchantName: Mapped[Optional[str]]
    location: Mapped[Optional[str]]
    timeframe: Mapped[Optional[str]]

    naturalLanguageQuery: Mapped[Optional[str]]
    sqlQuery: Mapped[Optional[str]]

    notificationMethods: Mapped[Optional[List[NotificationMethod]]] = mapped_column(
        ARRAY(SAEnum(NotificationMethod)), nullable=True
    )

    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    lastTriggered: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    triggerCount: Mapped[int] = mapped_column(Integer, server_default=text("0"))

    user: Mapped[User] = relationship(back_populates="alertRules")
    alertNotifications: Mapped[List["AlertNotification"]] = relationship(
        back_populates="alertRule"
    )

    __table_args__ = (Index("ix_alert_rules_user_active", "userId", "isActive"),)


class AlertNotification(Base):
    __tablename__ = "alert_notifications"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    userId: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    alertRuleId: Mapped[str] = mapped_column(ForeignKey("alert_rules.id", ondelete="CASCADE"))
    transactionId: Mapped[Optional[str]] = mapped_column(
        ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    notificationMethod: Mapped[NotificationMethod] = mapped_column(
        SAEnum(NotificationMethod), nullable=False
    )
    status: Mapped[NotificationStatus] = mapped_column(
        SAEnum(NotificationStatus), server_default=text("'PENDING'"), nullable=False
    )

    sentAt: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    deliveredAt: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    readAt: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="alertNotifications")
    alertRule: Mapped[AlertRule] = relationship(back_populates="alertNotifications")
    transaction: Mapped[Optional[Transaction]] = relationship(back_populates="alertNotifications")


