"""Transaction endpoints"""

from db import get_db
from db.models import Transaction
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class TransactionCreate(BaseModel):
    id: str = Field(...)
    userId: str
    creditCardId: str
    amount: float
    description: str
    merchantName: str
    merchantCategory: str
    transactionDate: str


@router.get('/{transaction_id}')
async def get_transaction(transaction_id: str, session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    tx: Transaction | None = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail='Transaction not found')
    return {
        'id': tx.id,
        'userId': tx.userId,
        'creditCardId': tx.creditCardId,
        'amount': float(tx.amount) if tx.amount is not None else None,
        'currency': tx.currency,
        'description': tx.description,
        'merchantName': tx.merchantName,
        'merchantCategory': tx.merchantCategory,
        'transactionDate': tx.transactionDate.isoformat()
        if tx.transactionDate
        else None,
        'status': tx.status.value,
    }


@router.post('')
async def create_transaction(
    payload: TransactionCreate, session: AsyncSession = Depends(get_db)
):
    tx = Transaction(
        id=payload.id,
        userId=payload.userId,
        creditCardId=payload.creditCardId,
        amount=payload.amount,
        description=payload.description,
        merchantName=payload.merchantName,
        merchantCategory=payload.merchantCategory,
        transactionDate=payload.transactionDate,
    )
    session.add(tx)
    await session.commit()
    await session.refresh(tx)
    return {'id': tx.id}
