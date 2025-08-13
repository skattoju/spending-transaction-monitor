"""Seed database with sample data"""

import asyncio
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import SessionLocal
from db.models import (
    User,
    CreditCard,
    Transaction,
    AlertRule,
    AlertType,
    NotificationMethod,
)


async def seed() -> None:
    async with SessionLocal() as session:  # type: AsyncSession
        # Check if already seeded
        existing = await session.execute(select(User).where(User.email == "john.doe@example.com"))
        if existing.scalar_one_or_none():
            print("Database already seeded; skipping.")
            return

        user_id = str(uuid.uuid4())
        card_id = str(uuid.uuid4())

        user = User(
            id=user_id,
            email="john.doe@example.com",
            firstName="John",
            lastName="Doe",
            phoneNumber="+1-555-0123",
            addressStreet="123 Main Street, Apt 4B",
            addressCity="San Francisco",
            addressState="CA",
            addressZipCode="94102",
            addressCountry="US",
            creditLimit=Decimal("15000.00"),
            currentBalance=Decimal("2347.85"),
            locationConsentGiven=True,
            lastAppLocationLatitude=37.7749,
            lastAppLocationLongitude=-122.4194,
            lastAppLocationTimestamp=datetime.fromisoformat("2024-01-17T18:30:00+00:00"),
            lastAppLocationAccuracy=5.0,
            lastTransactionLatitude=37.7849,
            lastTransactionLongitude=-122.4094,
            lastTransactionTimestamp=datetime.fromisoformat("2024-01-17T19:20:00+00:00"),
            lastTransactionCity="San Francisco",
            lastTransactionState="CA",
            lastTransactionCountry="US",
        )
        session.add(user)

        card = CreditCard(
            id=card_id,
            userId=user_id,
            cardNumber="1234",
            cardType="Visa",
            bankName="Example Bank",
            cardHolderName="John Doe",
            expiryMonth=12,
            expiryYear=2027,
        )
        session.add(card)

        txs = [
            Transaction(
                id=str(uuid.uuid4()),
                userId=user_id,
                creditCardId=card_id,
                amount=Decimal("89.99"),
                description="Grocery shopping",
                merchantName="Whole Foods Market",
                merchantCategory="Grocery",
                transactionDate=datetime.fromisoformat("2024-01-15T10:30:00+00:00"),
                merchantCity="San Francisco",
                merchantState="CA",
                merchantCountry="US",
                status=None,  # default
            ),
            Transaction(
                id=str(uuid.uuid4()),
                userId=user_id,
                creditCardId=card_id,
                amount=Decimal("1299.99"),
                description="Laptop purchase",
                merchantName="Apple Store",
                merchantCategory="Electronics",
                transactionDate=datetime.fromisoformat("2024-01-16T14:45:00+00:00"),
                merchantCity="San Francisco",
                merchantState="CA",
                merchantCountry="US",
            ),
            Transaction(
                id=str(uuid.uuid4()),
                userId=user_id,
                creditCardId=card_id,
                amount=Decimal("45.50"),
                description="Dinner",
                merchantName="Restaurant ABC",
                merchantCategory="Dining",
                transactionDate=datetime.fromisoformat("2024-01-17T19:20:00+00:00"),
                merchantCity="San Francisco",
                merchantState="CA",
                merchantCountry="US",
            ),
        ]
        session.add_all(txs)

        rules = [
            AlertRule(
                id=str(uuid.uuid4()),
                userId=user_id,
                name="High Amount Alert",
                description="Alert for transactions over $1000",
                alertType=AlertType.AMOUNT_THRESHOLD,
                amountThreshold=Decimal("1000.00"),
                notificationMethods=[NotificationMethod.EMAIL, NotificationMethod.SMS],
            ),
            AlertRule(
                id=str(uuid.uuid4()),
                userId=user_id,
                name="Electronics Purchase Alert",
                description="Alert for all electronics purchases",
                alertType=AlertType.MERCHANT_CATEGORY,
                merchantCategory="Electronics",
                notificationMethods=[NotificationMethod.EMAIL],
            ),
            AlertRule(
                id=str(uuid.uuid4()),
                userId=user_id,
                name="AI Smart Alert",
                description="Smart pattern-based alerts using AI",
                alertType=AlertType.PATTERN_BASED,
                naturalLanguageQuery="Alert me when I spend more than usual on dining in a week",
                notificationMethods=[NotificationMethod.PUSH],
            ),
        ]
        session.add_all(rules)

        await session.commit()
        print("Seeded sample user, card, transactions, and rules.")


if __name__ == "__main__":
    asyncio.run(seed())


