"""User endpoints"""

from db import get_db
from db.models import AlertRule, User
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..schemas.user import UserOut

router = APIRouter()


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
