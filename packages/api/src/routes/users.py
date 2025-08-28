"""User endpoints"""

import uuid

from db import get_db
from db.models import AlertRule, User
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..schemas.user import UserOut

router = APIRouter()


class UserCreate(BaseModel):
    email: str = Field(..., description='User email')
    firstName: str = Field(..., description='User first name')
    lastName: str = Field(..., description='User last name')
    phoneNumber: str | None = Field(None, description='User phone number')


class UserUpdate(BaseModel):
    email: str | None = Field(None, description='User email')
    firstName: str | None = Field(None, description='User first name')
    lastName: str | None = Field(None, description='User last name')
    phoneNumber: str | None = Field(None, description='User phone number')
    isActive: bool | None = Field(None, description='Whether the user is active')
    addressStreet: str | None = Field(None, description='Street address')
    addressCity: str | None = Field(None, description='City')
    addressState: str | None = Field(None, description='State')
    addressZipCode: str | None = Field(None, description='ZIP code')
    addressCountry: str | None = Field(None, description='Country')
    creditLimit: float | None = Field(None, description='Credit limit')
    currentBalance: float | None = Field(None, description='Current balance')
    locationConsentGiven: bool | None = Field(
        None, description='Whether location consent is given'
    )
    lastAppLocationLatitude: float | None = Field(
        None, description='Last app location latitude'
    )
    lastAppLocationLongitude: float | None = Field(
        None, description='Last app location longitude'
    )
    lastAppLocationAccuracy: float | None = Field(
        None, description='Last app location accuracy'
    )


@router.get('/', response_model=list[UserOut])
async def get_users(
    is_active: bool | None = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
):
    """Get all users with optional filtering"""
    try:
        query = select(User).options(
            selectinload(User.creditCards),
            selectinload(User.transactions),
        )

        if is_active is not None:
            query = query.where(User.isActive == is_active)

        query = query.offset(offset).limit(limit)

        result = await session.execute(query)
        users = result.scalars().all()

        return [
            {
                'id': user.id,
                'email': user.email,
                'firstName': user.firstName,
                'lastName': user.lastName,
                'phoneNumber': user.phoneNumber,
                'isActive': user.isActive,
                'createdAt': user.createdAt.isoformat() if user.createdAt else None,
                'updatedAt': user.updatedAt.isoformat() if user.updatedAt else None,
                'creditCardsCount': len(user.creditCards),
                'transactionsCount': len(user.transactions),
            }
            for user in users
        ]
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@router.get('/{user_id}', response_model=UserOut)
async def get_user(user_id: str, session: AsyncSession = Depends(get_db)):
    try:
        result = await session.execute(
            select(User)
            .options(
                selectinload(User.creditCards),
                selectinload(User.transactions),
            )
            .where(User.id == user_id)
        )
        user: User | None = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
    except SQLAlchemyError as err:
        # Surface DB errors with proper exception chaining
        raise HTTPException(status_code=500, detail=str(err)) from err

    # simple aggregation: counts
    credit_cards_count = len(user.creditCards)
    transactions_count = len(user.transactions)

    return {
        'id': user.id,
        'email': user.email,
        'firstName': user.firstName,
        'lastName': user.lastName,
        'phoneNumber': user.phoneNumber,
        'isActive': user.isActive,
        'createdAt': user.createdAt.isoformat() if user.createdAt else None,
        'updatedAt': user.updatedAt.isoformat() if user.updatedAt else None,
        'creditCardsCount': credit_cards_count,
        'transactionsCount': transactions_count,
    }


@router.post('', response_model=UserOut)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_db)):
    """Create a new user"""
    try:
        # Check if user with email already exists
        existing = await session.execute(
            select(User).where(User.email == payload.email)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400, detail='User with this email already exists'
            )

        user = User(
            id=str(uuid.uuid4()),
            email=payload.email,
            firstName=payload.firstName,
            lastName=payload.lastName,
            phoneNumber=payload.phoneNumber,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        return {
            'id': user.id,
            'email': user.email,
            'firstName': user.firstName,
            'lastName': user.lastName,
            'phoneNumber': user.phoneNumber,
            'isActive': user.isActive,
            'createdAt': user.createdAt.isoformat() if user.createdAt else None,
            'updatedAt': user.updatedAt.isoformat() if user.updatedAt else None,
            'creditCardsCount': 0,
            'transactionsCount': 0,
        }
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@router.put('/{user_id}', response_model=UserOut)
async def update_user(
    user_id: str, payload: UserUpdate, session: AsyncSession = Depends(get_db)
):
    """Update an existing user"""
    try:
        # Check if user exists
        result = await session.execute(
            select(User)
            .options(
                selectinload(User.creditCards),
                selectinload(User.transactions),
            )
            .where(User.id == user_id)
        )
        user: User | None = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        # Check if email is being updated and if it already exists
        if payload.email and payload.email != user.email:
            existing = await session.execute(
                select(User).where(User.email == payload.email)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=400, detail='User with this email already exists'
                )

        # Build update data
        update_data = {}
        for field, value in payload.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value

        if update_data:
            from datetime import datetime

            update_data['updatedAt'] = datetime.utcnow()

            # Update the user object
            for field, value in update_data.items():
                setattr(user, field, value)

            await session.commit()
            await session.refresh(user)

        credit_cards_count = len(user.creditCards)
        transactions_count = len(user.transactions)

        return {
            'id': user.id,
            'email': user.email,
            'firstName': user.firstName,
            'lastName': user.lastName,
            'phoneNumber': user.phoneNumber,
            'isActive': user.isActive,
            'createdAt': user.createdAt.isoformat() if user.createdAt else None,
            'updatedAt': user.updatedAt.isoformat() if user.updatedAt else None,
            'creditCardsCount': credit_cards_count,
            'transactionsCount': transactions_count,
        }
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@router.delete('/{user_id}')
async def delete_user(user_id: str, session: AsyncSession = Depends(get_db)):
    """Delete a user and all associated data"""
    try:
        # Check if user exists
        result = await session.execute(select(User).where(User.id == user_id))
        user: User | None = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        # Delete the user (cascade will handle related data)
        await session.delete(user)
        await session.commit()

        return {'message': 'User deleted successfully'}
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@router.get('/{user_id}/rules')
async def get_user_rules(user_id: str, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(AlertRule).where(AlertRule.userId == user_id))
    rules = result.scalars().all()
    return [
        {
            'id': r.id,
            'userId': r.userId,
            'name': r.name,
            'description': r.description,
            'isActive': r.isActive,
            'alertType': r.alertType.value,
            'notificationMethods': [m.value for m in (r.notificationMethods or [])],
        }
        for r in rules
    ]


@router.get('/{user_id}/transactions')
async def get_user_transactions(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
):
    """Get all transactions for a specific user"""
    try:
        # Check if user exists
        result = await session.execute(select(User).where(User.id == user_id))
        user: User | None = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        from db.models import Transaction

        query = select(Transaction).where(Transaction.userId == user_id)
        query = query.order_by(Transaction.transactionDate.desc())
        query = query.offset(offset).limit(limit)

        result = await session.execute(query)
        transactions = result.scalars().all()

        return [
            {
                'id': tx.id,
                'amount': float(tx.amount) if tx.amount is not None else None,
                'currency': tx.currency,
                'description': tx.description,
                'merchantName': tx.merchantName,
                'merchantCategory': tx.merchantCategory,
                'transactionDate': tx.transactionDate.isoformat()
                if tx.transactionDate
                else None,
                'transactionType': tx.transactionType.value,
                'status': tx.status.value,
            }
            for tx in transactions
        ]
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@router.get('/{user_id}/credit-cards')
async def get_user_credit_cards(
    user_id: str, is_active: bool | None = None, session: AsyncSession = Depends(get_db)
):
    """Get all credit cards for a specific user"""
    try:
        # Check if user exists
        result = await session.execute(select(User).where(User.id == user_id))
        user: User | None = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        from db.models import CreditCard

        query = select(CreditCard).where(CreditCard.userId == user_id)

        if is_active is not None:
            query = query.where(CreditCard.isActive == is_active)

        result = await session.execute(query)
        cards = result.scalars().all()

        return [
            {
                'id': card.id,
                'cardNumber': card.cardNumber,
                'cardType': card.cardType,
                'bankName': card.bankName,
                'cardHolderName': card.cardHolderName,
                'expiryMonth': card.expiryMonth,
                'expiryYear': card.expiryYear,
                'isActive': card.isActive,
                'createdAt': card.createdAt.isoformat() if card.createdAt else None,
                'updatedAt': card.updatedAt.isoformat() if card.updatedAt else None,
            }
            for card in cards
        ]
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@router.patch('/{user_id}/deactivate')
async def deactivate_user(user_id: str, session: AsyncSession = Depends(get_db)):
    """Deactivate a user (soft delete)"""
    try:
        # Check if user exists
        result = await session.execute(select(User).where(User.id == user_id))
        user: User | None = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        user.isActive = False
        from datetime import datetime

        user.updatedAt = datetime.utcnow()

        await session.commit()
        await session.refresh(user)

        return {'message': 'User deactivated successfully', 'isActive': user.isActive}
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@router.patch('/{user_id}/activate')
async def activate_user(user_id: str, session: AsyncSession = Depends(get_db)):
    """Activate a user"""
    try:
        # Check if user exists
        result = await session.execute(select(User).where(User.id == user_id))
        user: User | None = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        user.isActive = True
        from datetime import datetime

        user.updatedAt = datetime.utcnow()

        await session.commit()
        await session.refresh(user)

        return {'message': 'User activated successfully', 'isActive': user.isActive}
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail=str(err)) from err
