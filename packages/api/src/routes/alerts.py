"""Alert endpoints for managing alert rules and notifications"""

import uuid
from datetime import datetime

from db import get_db
from db.models import AlertNotification, AlertRule, AlertType, Transaction, User
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.alert import (
    AlertNotificationCreate,
    AlertNotificationOut,
    AlertNotificationUpdate,
    AlertRuleOut,
    AlertRuleUpdate,
)
from ..services.alerts.generate_alert_graph import app as generate_alert_graph
from ..services.alerts.parse_alert_graph import app as parse_alert_graph

router = APIRouter()


class AlertRuleCreateRequest(BaseModel):
    natural_language_query: str
    user_id: str


async def get_latest_transaction(user_id: str, session: AsyncSession):
    """
    Get the latest transaction for a user.
    """
    result = await session.execute(
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.transaction_date.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


def get_dummy_transaction(user_id: str):
    """
    Get a dummy transaction for a user.
    """
    return {
        'user_id': user_id,
        'transaction_date': datetime.now().isoformat(),
        'credit_card_num': '1234567890',
        'amount': 100.00,
        'currency': 'USD',
        'description': 'Dummy transaction',
        'merchant_name': 'Dummy merchant',
        'merchant_category': 'Dummy category',
        'merchant_city': 'Dummy city',
        'merchant_state': 'Dummy state',
        'merchant_country': 'Dummy country',
        'merchant_zipcode': 'Dummy zipcode',
        'merchant_latitude': 10.00,
        'merchant_longitude': 10.00,
        'trans_num': 'Dummy trans_num',
        'authorization_code': 'Dummy authorization_code',
        'status': 'Dummy status',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
    }


async def validate_alert_rule(rule: str, user_id: str, session: AsyncSession):
    """
    Validate an alert rule using the latest transaction for a user.
    Returns the parsed rule structure and validation results.
    """
    print('Validating rule:', rule)
    transaction = await get_latest_transaction(user_id, session)
    transaction_dict = (
        transaction.__dict__
        if transaction is not None
        else get_dummy_transaction(user_id)
    )

    try:
        parsed_rule = parse_nl_rule_with_llm(rule, transaction_dict)

        if parsed_rule and parsed_rule.get('valid_sql'):
            return {
                'status': 'valid',
                'message': 'Alert rule validated successfully',
                'transaction_used': transaction_dict,
                'user_id': user_id,
                'validation_timestamp': datetime.now().isoformat(),
                'alert_text': parsed_rule.get('alert_text'),
                'sql_query': parsed_rule.get('sql_query'),
            }
        else:
            return {
                'status': 'invalid',
                'transaction_used': transaction_dict,
                'user_id': user_id,
                'message': 'Rule could not be parsed or validated',
                'error': 'LLM could not parse rule structure',
                'alert_text': parsed_rule.get('alert_text'),
                'validation_timestamp': datetime.now().isoformat(),
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Validation failed: {str(e)}',
            'error': str(e),
        }


def parse_nl_rule_with_llm(alert_text, transaction):
    try:
        # Run actual LangGraph app here (uncomment below if integrated)
        result = parse_alert_graph.invoke(
            {'transaction': transaction, 'alert_text': alert_text}
        )
        return result
    except Exception as e:
        print('LLM parsing error:', e)
        raise e


# Alert Rules endpoints
@router.get('/rules', response_model=list[AlertRuleOut])
async def get_alert_rules(
    user_id: str | None = Query(None, description='Filter by user ID'),
    is_active: bool | None = Query(None, description='Filter by active status'),
    session: AsyncSession = Depends(get_db),
):
    """Get all alert rules with optional filtering"""
    query = select(AlertRule)

    if user_id:
        query = query.where(AlertRule.user_id == user_id)

    if is_active is not None:
        query = query.where(AlertRule.is_active == is_active)

    result = await session.execute(query)
    rules = result.scalars().all()

    return [
        AlertRuleOut(
            id=rule.id,
            user_id=rule.user_id,
            name=rule.name,
            description=rule.description,
            is_active=rule.is_active,
            alert_type=rule.alert_type,
            amount_threshold=float(rule.amount_threshold)
            if rule.amount_threshold
            else None,
            merchant_category=rule.merchant_category,
            merchant_name=rule.merchant_name,
            location=rule.location,
            timeframe=rule.timeframe,
            natural_language_query=rule.natural_language_query,
            notification_methods=rule.notification_methods,
            created_at=rule.created_at.isoformat(),
            updated_at=rule.updated_at.isoformat(),
            last_triggered=rule.last_triggered.isoformat()
            if rule.last_triggered
            else None,
            trigger_count=rule.trigger_count,
        )
        for rule in rules
    ]


@router.get('/rules/{rule_id}', response_model=AlertRuleOut)
async def get_alert_rule(rule_id: str, session: AsyncSession = Depends(get_db)):
    """Get a specific alert rule by ID"""
    result = await session.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=404, detail='Alert rule not found')

    return AlertRuleOut(
        id=rule.id,
        user_id=rule.user_id,
        name=rule.name,
        description=rule.description,
        is_active=rule.is_active,
        alert_type=rule.alert_type,
        amount_threshold=float(rule.amount_threshold)
        if rule.amount_threshold
        else None,
        merchant_category=rule.merchant_category,
        merchant_name=rule.merchant_name,
        location=rule.location,
        timeframe=rule.timeframe,
        natural_language_query=rule.natural_language_query,
        notification_methods=rule.notification_methods,
        created_at=rule.created_at.isoformat(),
        updated_at=rule.updated_at.isoformat(),
        last_triggered=rule.last_triggered.isoformat() if rule.last_triggered else None,
        trigger_count=rule.trigger_count,
    )


@router.post('/rules', response_model=AlertRuleOut)
async def create_alert_rule(
    payload: AlertRuleCreateRequest, session: AsyncSession = Depends(get_db)
):
    """Create a new alert rule"""
    # Verify user exists
    user_result = await session.execute(select(User).where(User.id == payload.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    print('Creating alert rule:', payload)

    # Validate alert rule
    validate_result = await validate_alert_rule(
        payload.natural_language_query, payload.user_id, session
    )
    if validate_result.get('status') != 'valid':
        raise HTTPException(status_code=400, detail='Invalid alert rule')

    rule = AlertRule(
        id=str(uuid.uuid4()),
        user_id=payload.user_id,
        name=payload.natural_language_query,
        description=payload.natural_language_query,
        is_active=True,
        alert_type=AlertType.CUSTOM_QUERY,
        # alert_type=payload.alert_type,
        # amount_threshold=payload.amount_threshold,
        # merchant_category=payload.merchant_category,
        # merchant_name=payload.merchant_name,
        # location=payload.location,
        # timeframe=payload.timeframe,
        natural_language_query=payload.natural_language_query,
        notification_methods=None,
    )

    session.add(rule)
    await session.commit()
    await session.refresh(rule)

    return AlertRuleOut(
        id=rule.id,
        user_id=rule.user_id,
        name=rule.name,
        description=rule.description,
        is_active=rule.is_active,
        alert_type=rule.alert_type,
        amount_threshold=float(rule.amount_threshold)
        if rule.amount_threshold
        else None,
        merchant_category=rule.merchant_category,
        merchant_name=rule.merchant_name,
        location=rule.location,
        timeframe=rule.timeframe,
        natural_language_query=rule.natural_language_query,
        notification_methods=rule.notification_methods,
        created_at=rule.created_at.isoformat(),
        updated_at=rule.updated_at.isoformat(),
        last_triggered=rule.last_triggered.isoformat() if rule.last_triggered else None,
        trigger_count=rule.trigger_count,
    )


@router.put('/rules/{rule_id}', response_model=AlertRuleOut)
async def update_alert_rule(
    rule_id: str, payload: AlertRuleUpdate, session: AsyncSession = Depends(get_db)
):
    """Update an existing alert rule"""
    # Check if rule exists
    result = await session.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail='Alert rule not found')

    # Build update data
    update_data = {}
    for field, value in payload.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value

    if update_data:
        update_data['updated_at'] = datetime.utcnow()
        await session.execute(
            update(AlertRule).where(AlertRule.id == rule_id).values(**update_data)
        )
        await session.commit()
        await session.refresh(rule)

    return AlertRuleOut(
        id=rule.id,
        user_id=rule.user_id,
        name=rule.name,
        description=rule.description,
        is_active=rule.is_active,
        alert_type=rule.alert_type,
        amount_threshold=float(rule.amount_threshold)
        if rule.amount_threshold
        else None,
        merchant_category=rule.merchant_category,
        merchant_name=rule.merchant_name,
        location=rule.location,
        timeframe=rule.timeframe,
        natural_language_query=rule.natural_language_query,
        notification_methods=rule.notification_methods,
        created_at=rule.created_at.isoformat(),
        updated_at=rule.updated_at.isoformat(),
        last_triggered=rule.last_triggered.isoformat() if rule.last_triggered else None,
        trigger_count=rule.trigger_count,
    )


@router.delete('/rules/{rule_id}')
async def delete_alert_rule(rule_id: str, session: AsyncSession = Depends(get_db)):
    """Delete an alert rule"""
    result = await session.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail='Alert rule not found')

    await session.delete(rule)
    await session.commit()

    return {'message': 'Alert rule deleted successfully'}


# Alert Notifications endpoints
@router.get('/notifications', response_model=list[AlertNotificationOut])
async def get_alert_notifications(
    user_id: str | None = Query(None, description='Filter by user ID'),
    alert_rule_id: str | None = Query(None, description='Filter by alert rule ID'),
    status: str | None = Query(None, description='Filter by notification status'),
    session: AsyncSession = Depends(get_db),
):
    """Get all alert notifications with optional filtering"""
    query = select(AlertNotification)

    if user_id:
        query = query.where(AlertNotification.user_id == user_id)

    if alert_rule_id:
        query = query.where(AlertNotification.alert_rule_id == alert_rule_id)

    if status:
        query = query.where(AlertNotification.status == status)

    result = await session.execute(query)
    notifications = result.scalars().all()

    return [
        AlertNotificationOut(
            id=notification.id,
            user_id=notification.user_id,
            alert_rule_id=notification.alert_rule_id,
            transaction_id=notification.transaction_id,
            title=notification.title,
            message=notification.message,
            notification_method=notification.notification_method,
            status=notification.status,
            sent_at=notification.sent_at.isoformat() if notification.sent_at else None,
            delivered_at=notification.delivered_at.isoformat()
            if notification.delivered_at
            else None,
            read_at=notification.read_at.isoformat() if notification.read_at else None,
            created_at=notification.created_at.isoformat(),
            updated_at=notification.updated_at.isoformat(),
        )
        for notification in notifications
    ]


@router.get('/notifications/{notification_id}', response_model=AlertNotificationOut)
async def get_alert_notification(
    notification_id: str, session: AsyncSession = Depends(get_db)
):
    """Get a specific alert notification by ID"""
    result = await session.execute(
        select(AlertNotification).where(AlertNotification.id == notification_id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail='Alert notification not found')

    return AlertNotificationOut(
        id=notification.id,
        user_id=notification.user_id,
        alert_rule_id=notification.alert_rule_id,
        transaction_id=notification.transaction_id,
        title=notification.title,
        message=notification.message,
        notification_method=notification.notification_method,
        status=notification.status,
        sent_at=notification.sent_at.isoformat() if notification.sent_at else None,
        delivered_at=notification.delivered_at.isoformat()
        if notification.delivered_at
        else None,
        read_at=notification.read_at.isoformat() if notification.read_at else None,
        created_at=notification.created_at.isoformat(),
        updated_at=notification.updated_at.isoformat(),
    )


@router.post('/notifications', response_model=AlertNotificationOut)
async def create_alert_notification(
    payload: AlertNotificationCreate, session: AsyncSession = Depends(get_db)
):
    """Create a new alert notification"""
    # Verify user exists
    user_result = await session.execute(select(User).where(User.id == payload.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Verify alert rule exists
    rule_result = await session.execute(
        select(AlertRule).where(AlertRule.id == payload.alert_rule_id)
    )
    rule = rule_result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail='Alert rule not found')

    notification = AlertNotification(
        id=str(uuid.uuid4()),
        user_id=payload.user_id,
        alert_rule_id=payload.alert_rule_id,
        transaction_id=payload.transaction_id,
        title=payload.title,
        message=payload.message,
        notification_method=payload.notification_method,
        status=payload.status,
    )

    session.add(notification)
    await session.commit()
    await session.refresh(notification)

    return AlertNotificationOut(
        id=notification.id,
        user_id=notification.user_id,
        alert_rule_id=notification.alert_rule_id,
        transaction_id=notification.transaction_id,
        title=notification.title,
        message=notification.message,
        notification_method=notification.notification_method,
        status=notification.status,
        sent_at=notification.sent_at.isoformat() if notification.sent_at else None,
        delivered_at=notification.delivered_at.isoformat()
        if notification.delivered_at
        else None,
        read_at=notification.read_at.isoformat() if notification.read_at else None,
        created_at=notification.created_at.isoformat(),
        updated_at=notification.updated_at.isoformat(),
    )


@router.put('/notifications/{notification_id}', response_model=AlertNotificationOut)
async def update_alert_notification(
    notification_id: str,
    payload: AlertNotificationUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Update an existing alert notification"""
    # Check if notification exists
    result = await session.execute(
        select(AlertNotification).where(AlertNotification.id == notification_id)
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail='Alert notification not found')

    # Build update data
    update_data = {}
    for field, value in payload.dict(exclude_unset=True).items():
        if value is not None:
            if field in ['sent_at', 'delivered_at', 'read_at'] and value:
                update_data[field] = datetime.fromisoformat(value)
            else:
                update_data[field] = value

    if update_data:
        update_data['updated_at'] = datetime.utcnow()
        await session.execute(
            update(AlertNotification)
            .where(AlertNotification.id == notification_id)
            .values(**update_data)
        )
        await session.commit()
        await session.refresh(notification)

    return AlertNotificationOut(
        id=notification.id,
        user_id=notification.user_id,
        alert_rule_id=notification.alert_rule_id,
        transaction_id=notification.transaction_id,
        title=notification.title,
        message=notification.message,
        notification_method=notification.notification_method,
        status=notification.status,
        sent_at=notification.sent_at.isoformat() if notification.sent_at else None,
        delivered_at=notification.delivered_at.isoformat()
        if notification.delivered_at
        else None,
        read_at=notification.read_at.isoformat() if notification.read_at else None,
        created_at=notification.created_at.isoformat(),
        updated_at=notification.updated_at.isoformat(),
    )


@router.delete('/notifications/{notification_id}')
async def delete_alert_notification(
    notification_id: str, session: AsyncSession = Depends(get_db)
):
    """Delete an alert notification"""
    result = await session.execute(
        select(AlertNotification).where(AlertNotification.id == notification_id)
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail='Alert notification not found')

    await session.delete(notification)
    await session.commit()

    return {'message': 'Alert notification deleted successfully'}


# Additional utility endpoints
@router.get('/rules/{rule_id}/notifications', response_model=list[AlertNotificationOut])
async def get_notifications_for_rule(
    rule_id: str, session: AsyncSession = Depends(get_db)
):
    """Get all notifications for a specific alert rule"""
    result = await session.execute(
        select(AlertNotification).where(AlertNotification.alert_rule_id == rule_id)
    )
    notifications = result.scalars().all()

    return [
        AlertNotificationOut(
            id=notification.id,
            user_id=notification.user_id,
            alert_rule_id=notification.alert_rule_id,
            transaction_id=notification.transaction_id,
            title=notification.title,
            message=notification.message,
            notification_method=notification.notification_method,
            status=notification.status,
            sent_at=notification.sent_at.isoformat() if notification.sent_at else None,
            delivered_at=notification.delivered_at.isoformat()
            if notification.delivered_at
            else None,
            read_at=notification.read_at.isoformat() if notification.read_at else None,
            created_at=notification.created_at.isoformat(),
            updated_at=notification.updated_at.isoformat(),
        )
        for notification in notifications
    ]


@router.post('/rules/{rule_id}/trigger')
async def trigger_alert_rule(rule_id: str, session: AsyncSession = Depends(get_db)):
    """Manually trigger an alert rule (for testing purposes)"""
    result = await session.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail='Alert rule not found')

    if not rule.is_active:
        raise HTTPException(status_code=400, detail='Alert rule is not active')

    transaction = None
    try:
        transaction = await get_latest_transaction(rule.user_id, session)
        if transaction is None:
            raise HTTPException(status_code=404, detail='No Transaction found for user')

        alert_result = generate_alert_with_llm(
            rule.natural_language_query, transaction.__dict__
        )

        if alert_result and alert_result.get('should_trigger', False):
            # Create AlertNotification object
            notification = AlertNotification(
                id=str(uuid.uuid4()),
                user_id=rule.user_id,
                alert_rule_id=rule_id,
                transaction_id=transaction.trans_num,
                title=f'Alert: {rule.name}',
                message=alert_result.get('message', 'Alert triggered'),
                notification_method='system',
                status='sent',
            )

            # Add notification to session
            session.add(notification)

            # Update trigger count and last triggered time
            await session.execute(
                update(AlertRule)
                .where(AlertRule.id == rule_id)
                .values(
                    trigger_count=rule.trigger_count + 1,
                    last_triggered=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            )
            await session.commit()

            return {
                'message': 'Alert rule triggered successfully',
                'trigger_count': rule.trigger_count + 1,
                'rule_evaluation': alert_result,
                'transaction_id': transaction.trans_num,
                'notification_id': notification.id,
            }

        else:
            return {
                'status': 'not_triggered',
                'message': 'Rule evaluated but alert not triggered',
                'rule_evaluation': alert_result,
                'transaction_id': transaction.trans_num,
            }

    except Exception as e:
        transaction_id = transaction.trans_num if transaction else 'unknown'
        return {
            'status': 'error',
            'message': f'Alert generation failed: {str(e)}',
            'error': str(e),
            'transaction_id': transaction_id,
        }


def generate_alert_with_llm(alert_text, transaction):
    try:
        result = generate_alert_graph.invoke(
            {'transaction': transaction, 'alert_text': alert_text}
        )
        return result
    except Exception as e:
        print('LLM parsing error:', e)
        raise e
