"""Transaction endpoints"""

from db import get_db
from db.models import Transaction, CreditCard, User
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from ..schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionOut,
    CreditCardCreate,
    CreditCardUpdate,
    CreditCardOut,
    TransactionFilters,
    TransactionSummary,
    CategorySpending,
    SpendingAnalysis,
)

router = APIRouter()


@router.get('/', response_model=List[TransactionOut])
async def get_transactions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    credit_card_id: Optional[str] = Query(None, description="Filter by credit card ID"),
    merchant_category: Optional[str] = Query(None, description="Filter by merchant category"),
    min_amount: Optional[float] = Query(None, description="Minimum transaction amount"),
    max_amount: Optional[float] = Query(None, description="Maximum transaction amount"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, description="Maximum number of transactions to return"),
    offset: int = Query(0, description="Number of transactions to skip"),
    session: AsyncSession = Depends(get_db),
):
    """Get all transactions with optional filtering"""
    query = select(Transaction)
    
    if user_id:
        query = query.where(Transaction.userId == user_id)
    
    if credit_card_id:
        query = query.where(Transaction.creditCardId == credit_card_id)
    
    if merchant_category:
        query = query.where(Transaction.merchantCategory == merchant_category)
    
    if min_amount is not None:
        query = query.where(Transaction.amount >= min_amount)
    
    if max_amount is not None:
        query = query.where(Transaction.amount <= max_amount)
    
    if start_date:
        try:
            from datetime import datetime
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.where(Transaction.transactionDate >= start_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start date format. Use ISO format (e.g., '2024-01-16T14:45:00Z')")
    
    if end_date:
        try:
            from datetime import datetime
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.where(Transaction.transactionDate <= end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end date format. Use ISO format (e.g., '2024-01-16T14:45:00Z')")
    
    query = query.order_by(Transaction.transactionDate.desc())
    query = query.offset(offset).limit(limit)
    
    result = await session.execute(query)
    transactions = result.scalars().all()
    
    return [
        TransactionOut(
            id=tx.id,
            userId=tx.userId,
            creditCardId=tx.creditCardId,
            amount=float(tx.amount) if tx.amount is not None else None,
            currency=tx.currency,
            description=tx.description,
            merchantName=tx.merchantName,
            merchantCategory=tx.merchantCategory,
            transactionDate=tx.transactionDate.isoformat() if tx.transactionDate else None,
            transactionType=tx.transactionType,
            merchantLocation=tx.merchantLocation,
            merchantCity=tx.merchantCity,
            merchantState=tx.merchantState,
            merchantCountry=tx.merchantCountry,
            status=tx.status,
            authorizationCode=tx.authorizationCode,
            referenceNumber=tx.referenceNumber,
            createdAt=tx.createdAt.isoformat() if tx.createdAt else None,
            updatedAt=tx.updatedAt.isoformat() if tx.updatedAt else None,
        )
        for tx in transactions
    ]


@router.get('/{transaction_id}', response_model=TransactionOut)
async def get_transaction(transaction_id: str, session: AsyncSession = Depends(get_db)):
    """Get a specific transaction by ID"""
    result = await session.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    tx: Transaction | None = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail='Transaction not found')
    
    return TransactionOut(
        id=tx.id,
        userId=tx.userId,
        creditCardId=tx.creditCardId,
        amount=float(tx.amount) if tx.amount is not None else None,
        currency=tx.currency,
        description=tx.description,
        merchantName=tx.merchantName,
        merchantCategory=tx.merchantCategory,
        transactionDate=tx.transactionDate.isoformat() if tx.transactionDate else None,
        transactionType=tx.transactionType,
        merchantLocation=tx.merchantLocation,
        merchantCity=tx.merchantCity,
        merchantState=tx.merchantState,
        merchantCountry=tx.merchantCountry,
        status=tx.status,
        authorizationCode=tx.authorizationCode,
        referenceNumber=tx.referenceNumber,
        createdAt=tx.createdAt.isoformat() if tx.createdAt else None,
        updatedAt=tx.updatedAt.isoformat() if tx.updatedAt else None,
    )


@router.post('', response_model=TransactionOut)
async def create_transaction(
    payload: TransactionCreate, session: AsyncSession = Depends(get_db)
):
    """Create a new transaction"""
    # Verify user exists
    user_result = await session.execute(select(User).where(User.id == payload.userId))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify credit card exists
    card_result = await session.execute(
        select(CreditCard).where(CreditCard.id == payload.creditCardId)
    )
    card = card_result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Credit card not found")
    
    # Parse the transaction date string to datetime object
    from datetime import datetime
    try:
        transaction_date = datetime.fromisoformat(payload.transactionDate.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid transaction date format. Use ISO format (e.g., '2024-01-16T14:45:00Z')")
    
    tx = Transaction(
        id=payload.id,
        userId=payload.userId,
        creditCardId=payload.creditCardId,
        amount=payload.amount,
        currency=payload.currency,
        description=payload.description,
        merchantName=payload.merchantName,
        merchantCategory=payload.merchantCategory,
        transactionDate=transaction_date,
        transactionType=payload.transactionType,
        merchantLocation=payload.merchantLocation,
        merchantCity=payload.merchantCity,
        merchantState=payload.merchantState,
        merchantCountry=payload.merchantCountry,
        status=payload.status,
        authorizationCode=payload.authorizationCode,
        referenceNumber=payload.referenceNumber,
    )
    session.add(tx)
    await session.commit()
    await session.refresh(tx)
    
    return TransactionOut(
        id=tx.id,
        userId=tx.userId,
        creditCardId=tx.creditCardId,
        amount=float(tx.amount) if tx.amount is not None else None,
        currency=tx.currency,
        description=tx.description,
        merchantName=tx.merchantName,
        merchantCategory=tx.merchantCategory,
        transactionDate=tx.transactionDate.isoformat() if tx.transactionDate else None,
        transactionType=tx.transactionType,
        merchantLocation=tx.merchantLocation,
        merchantCity=tx.merchantCity,
        merchantState=tx.merchantState,
        merchantCountry=tx.merchantCountry,
        status=tx.status,
        authorizationCode=tx.authorizationCode,
        referenceNumber=tx.referenceNumber,
        createdAt=tx.createdAt.isoformat() if tx.createdAt else None,
        updatedAt=tx.updatedAt.isoformat() if tx.updatedAt else None,
    )


@router.put('/{transaction_id}', response_model=TransactionOut)
async def update_transaction(
    transaction_id: str, payload: TransactionUpdate, session: AsyncSession = Depends(get_db)
):
    """Update an existing transaction"""
    # Check if transaction exists
    result = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Build update data
    update_data = {}
    for field, value in payload.dict(exclude_unset=True).items():
        if value is not None:
            # Handle date parsing for transactionDate
            if field == "transactionDate":
                try:
                    from datetime import datetime
                    update_data[field] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid transaction date format. Use ISO format (e.g., '2024-01-16T14:45:00Z')")
            else:
                update_data[field] = value
    
    if update_data:
        from datetime import datetime
        update_data["updatedAt"] = datetime.utcnow()
        await session.execute(
            update(Transaction).where(Transaction.id == transaction_id).values(**update_data)
        )
        await session.commit()
        await session.refresh(tx)
    
    return TransactionOut(
        id=tx.id,
        userId=tx.userId,
        creditCardId=tx.creditCardId,
        amount=float(tx.amount) if tx.amount is not None else None,
        currency=tx.currency,
        description=tx.description,
        merchantName=tx.merchantName,
        merchantCategory=tx.merchantCategory,
        transactionDate=tx.transactionDate.isoformat() if tx.transactionDate else None,
        transactionType=tx.transactionType,
        merchantLocation=tx.merchantLocation,
        merchantCity=tx.merchantCity,
        merchantState=tx.merchantState,
        merchantCountry=tx.merchantCountry,
        status=tx.status,
        authorizationCode=tx.authorizationCode,
        referenceNumber=tx.referenceNumber,
        createdAt=tx.createdAt.isoformat() if tx.createdAt else None,
        updatedAt=tx.updatedAt.isoformat() if tx.updatedAt else None,
    )


@router.delete('/{transaction_id}')
async def delete_transaction(transaction_id: str, session: AsyncSession = Depends(get_db)):
    """Delete a transaction"""
    result = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    await session.delete(tx)
    await session.commit()
    
    return {"message": "Transaction deleted successfully"}


# Credit Card endpoints
@router.get('/cards', response_model=List[CreditCardOut])
async def get_credit_cards(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    session: AsyncSession = Depends(get_db),
):
    """Get all credit cards with optional filtering"""
    query = select(CreditCard)
    
    if user_id:
        query = query.where(CreditCard.userId == user_id)
    
    if is_active is not None:
        query = query.where(CreditCard.isActive == is_active)
    
    result = await session.execute(query)
    cards = result.scalars().all()
    
    return [
        CreditCardOut(
            id=card.id,
            userId=card.userId,
            cardNumber=card.cardNumber,
            cardType=card.cardType,
            bankName=card.bankName,
            cardHolderName=card.cardHolderName,
            expiryMonth=card.expiryMonth,
            expiryYear=card.expiryYear,
            isActive=card.isActive,
            createdAt=card.createdAt.isoformat() if card.createdAt else None,
            updatedAt=card.updatedAt.isoformat() if card.updatedAt else None,
        )
        for card in cards
    ]


@router.get('/cards/{card_id}', response_model=CreditCardOut)
async def get_credit_card(card_id: str, session: AsyncSession = Depends(get_db)):
    """Get a specific credit card by ID"""
    result = await session.execute(select(CreditCard).where(CreditCard.id == card_id))
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Credit card not found")
    
    return CreditCardOut(
        id=card.id,
        userId=card.userId,
        cardNumber=card.cardNumber,
        cardType=card.cardType,
        bankName=card.bankName,
        cardHolderName=card.cardHolderName,
        expiryMonth=card.expiryMonth,
        expiryYear=card.expiryYear,
        isActive=card.isActive,
        createdAt=card.createdAt.isoformat() if card.createdAt else None,
        updatedAt=card.updatedAt.isoformat() if card.updatedAt else None,
    )


@router.post('/cards', response_model=CreditCardOut)
async def create_credit_card(
    payload: CreditCardCreate, session: AsyncSession = Depends(get_db)
):
    """Create a new credit card"""
    # Verify user exists
    user_result = await session.execute(select(User).where(User.id == payload.userId))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    card = CreditCard(
        id=str(uuid.uuid4()),
        userId=payload.userId,
        cardNumber=payload.cardNumber,
        cardType=payload.cardType,
        bankName=payload.bankName,
        cardHolderName=payload.cardHolderName,
        expiryMonth=payload.expiryMonth,
        expiryYear=payload.expiryYear,
        isActive=payload.isActive,
    )
    
    session.add(card)
    await session.commit()
    await session.refresh(card)
    
    return CreditCardOut(
        id=card.id,
        userId=card.userId,
        cardNumber=card.cardNumber,
        cardType=card.cardType,
        bankName=card.bankName,
        cardHolderName=card.cardHolderName,
        expiryMonth=card.expiryMonth,
        expiryYear=card.expiryYear,
        isActive=card.isActive,
        createdAt=card.createdAt.isoformat() if card.createdAt else None,
        updatedAt=card.updatedAt.isoformat() if card.updatedAt else None,
    )


@router.put('/cards/{card_id}', response_model=CreditCardOut)
async def update_credit_card(
    card_id: str, payload: CreditCardUpdate, session: AsyncSession = Depends(get_db)
):
    """Update an existing credit card"""
    # Check if card exists
    result = await session.execute(select(CreditCard).where(CreditCard.id == card_id))
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Credit card not found")
    
    # Build update data
    update_data = {}
    for field, value in payload.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    if update_data:
        from datetime import datetime
        update_data["updatedAt"] = datetime.utcnow()
        await session.execute(
            update(CreditCard).where(CreditCard.id == card_id).values(**update_data)
        )
        await session.commit()
        await session.refresh(card)
    
    return CreditCardOut(
        id=card.id,
        userId=card.userId,
        cardNumber=card.cardNumber,
        cardType=card.cardType,
        bankName=card.bankName,
        cardHolderName=card.cardHolderName,
        expiryMonth=card.expiryMonth,
        expiryYear=card.expiryYear,
        isActive=card.isActive,
        createdAt=card.createdAt.isoformat() if card.createdAt else None,
        updatedAt=card.updatedAt.isoformat() if card.updatedAt else None,
    )


@router.delete('/cards/{card_id}')
async def delete_credit_card(card_id: str, session: AsyncSession = Depends(get_db)):
    """Delete a credit card"""
    result = await session.execute(select(CreditCard).where(CreditCard.id == card_id))
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Credit card not found")
    
    await session.delete(card)
    await session.commit()
    
    return {"message": "Credit card deleted successfully"}


# Analysis endpoints
@router.get('/analysis/summary/{user_id}', response_model=TransactionSummary)
async def get_transaction_summary(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    session: AsyncSession = Depends(get_db),
):
    """Get transaction summary for a user"""
    # Verify user exists
    user_result = await session.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = select(Transaction).where(Transaction.userId == user_id)
    
    if start_date:
        try:
            from datetime import datetime
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.where(Transaction.transactionDate >= start_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start date format. Use ISO format (e.g., '2024-01-16T14:45:00Z')")
    
    if end_date:
        try:
            from datetime import datetime
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.where(Transaction.transactionDate <= end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end date format. Use ISO format (e.g., '2024-01-16T14:45:00Z')")
    
    result = await session.execute(query)
    transactions = result.scalars().all()
    
    if not transactions:
        return TransactionSummary(
            totalTransactions=0,
            totalAmount=0.0,
            averageAmount=0.0,
            largestTransaction=0.0,
            smallestTransaction=0.0,
        )
    
    amounts = [float(tx.amount) for tx in transactions if tx.amount is not None]
    
    return TransactionSummary(
        totalTransactions=len(transactions),
        totalAmount=sum(amounts),
        averageAmount=sum(amounts) / len(amounts) if amounts else 0.0,
        largestTransaction=max(amounts) if amounts else 0.0,
        smallestTransaction=min(amounts) if amounts else 0.0,
    )


@router.get('/analysis/categories/{user_id}', response_model=List[CategorySpending])
async def get_category_spending(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    session: AsyncSession = Depends(get_db),
):
    """Get spending breakdown by category for a user"""
    # Verify user exists
    user_result = await session.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = select(Transaction).where(Transaction.userId == user_id)
    
    if start_date:
        try:
            from datetime import datetime
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.where(Transaction.transactionDate >= start_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start date format. Use ISO format (e.g., '2024-01-16T14:45:00Z')")
    
    if end_date:
        try:
            from datetime import datetime
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.where(Transaction.transactionDate <= end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end date format. Use ISO format (e.g., '2024-01-16T14:45:00Z')")
    
    result = await session.execute(query)
    transactions = result.scalars().all()
    
    # Group by category
    category_data = {}
    for tx in transactions:
        category = tx.merchantCategory
        amount = float(tx.amount) if tx.amount is not None else 0.0
        
        if category not in category_data:
            category_data[category] = {
                'total': 0.0,
                'count': 0,
                'amounts': []
            }
        
        category_data[category]['total'] += amount
        category_data[category]['count'] += 1
        category_data[category]['amounts'].append(amount)
    
    return [
        CategorySpending(
            category=category,
            totalAmount=data['total'],
            transactionCount=data['count'],
            averageAmount=data['total'] / data['count'] if data['count'] > 0 else 0.0,
        )
        for category, data in category_data.items()
    ]
