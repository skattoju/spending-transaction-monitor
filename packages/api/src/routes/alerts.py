"""Alert endpoints for managing alert rules and notifications"""

import uuid
from datetime import datetime

from db import get_db
from db.models import AlertNotification, AlertRule, User
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.alert import (
    AlertNotificationCreate,
    AlertNotificationOut,
    AlertNotificationUpdate,
    AlertRuleCreate,
    AlertRuleOut,
    AlertRuleUpdate,
)

router = APIRouter()


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
        query = query.where(AlertRule.userId == user_id)

    if is_active is not None:
        query = query.where(AlertRule.isActive == is_active)

    result = await session.execute(query)
    rules = result.scalars().all()

    return [
        AlertRuleOut(
            id=rule.id,
            userId=rule.userId,
            name=rule.name,
            description=rule.description,
            isActive=rule.isActive,
            alertType=rule.alertType,
            amountThreshold=float(rule.amountThreshold)
            if rule.amountThreshold
            else None,
            merchantCategory=rule.merchantCategory,
            merchantName=rule.merchantName,
            location=rule.location,
            timeframe=rule.timeframe,
            naturalLanguageQuery=rule.naturalLanguageQuery,
            notificationMethods=rule.notificationMethods,
            createdAt=rule.createdAt.isoformat(),
            updatedAt=rule.updatedAt.isoformat(),
            lastTriggered=rule.lastTriggered.isoformat()
            if rule.lastTriggered
            else None,
            triggerCount=rule.triggerCount,
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
        userId=rule.userId,
        name=rule.name,
        description=rule.description,
        isActive=rule.isActive,
        alertType=rule.alertType,
        amountThreshold=float(rule.amountThreshold) if rule.amountThreshold else None,
        merchantCategory=rule.merchantCategory,
        merchantName=rule.merchantName,
        location=rule.location,
        timeframe=rule.timeframe,
        naturalLanguageQuery=rule.naturalLanguageQuery,
        notificationMethods=rule.notificationMethods,
        createdAt=rule.createdAt.isoformat(),
        updatedAt=rule.updatedAt.isoformat(),
        lastTriggered=rule.lastTriggered.isoformat() if rule.lastTriggered else None,
        triggerCount=rule.triggerCount,
    )


@router.post('/rules', response_model=AlertRuleOut)
async def create_alert_rule(
    payload: AlertRuleCreate, session: AsyncSession = Depends(get_db)
):
    """Create a new alert rule"""
    # Verify user exists
    user_result = await session.execute(select(User).where(User.id == payload.userId))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    rule = AlertRule(
        id=str(uuid.uuid4()),
        userId=payload.userId,
        name=payload.name,
        description=payload.description,
        isActive=payload.isActive,
        alertType=payload.alertType,
        amountThreshold=payload.amountThreshold,
        merchantCategory=payload.merchantCategory,
        merchantName=payload.merchantName,
        location=payload.location,
        timeframe=payload.timeframe,
        naturalLanguageQuery=payload.naturalLanguageQuery,
        notificationMethods=payload.notificationMethods,
    )

    session.add(rule)
    await session.commit()
    await session.refresh(rule)

    return AlertRuleOut(
        id=rule.id,
        userId=rule.userId,
        name=rule.name,
        description=rule.description,
        isActive=rule.isActive,
        alertType=rule.alertType,
        amountThreshold=float(rule.amountThreshold) if rule.amountThreshold else None,
        merchantCategory=rule.merchantCategory,
        merchantName=rule.merchantName,
        location=rule.location,
        timeframe=rule.timeframe,
        naturalLanguageQuery=rule.naturalLanguageQuery,
        notificationMethods=rule.notificationMethods,
        createdAt=rule.createdAt.isoformat(),
        updatedAt=rule.updatedAt.isoformat(),
        lastTriggered=rule.lastTriggered.isoformat() if rule.lastTriggered else None,
        triggerCount=rule.triggerCount,
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
        update_data['updatedAt'] = datetime.utcnow()
        await session.execute(
            update(AlertRule).where(AlertRule.id == rule_id).values(**update_data)
        )
        await session.commit()
        await session.refresh(rule)

    return AlertRuleOut(
        id=rule.id,
        userId=rule.userId,
        name=rule.name,
        description=rule.description,
        isActive=rule.isActive,
        alertType=rule.alertType,
        amountThreshold=float(rule.amountThreshold) if rule.amountThreshold else None,
        merchantCategory=rule.merchantCategory,
        merchantName=rule.merchantName,
        location=rule.location,
        timeframe=rule.timeframe,
        naturalLanguageQuery=rule.naturalLanguageQuery,
        notificationMethods=rule.notificationMethods,
        createdAt=rule.createdAt.isoformat(),
        updatedAt=rule.updatedAt.isoformat(),
        lastTriggered=rule.lastTriggered.isoformat() if rule.lastTriggered else None,
        triggerCount=rule.triggerCount,
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
        query = query.where(AlertNotification.userId == user_id)

    if alert_rule_id:
        query = query.where(AlertNotification.alertRuleId == alert_rule_id)

    if status:
        query = query.where(AlertNotification.status == status)

    result = await session.execute(query)
    notifications = result.scalars().all()

    return [
        AlertNotificationOut(
            id=notification.id,
            userId=notification.userId,
            alertRuleId=notification.alertRuleId,
            transactionId=notification.transactionId,
            title=notification.title,
            message=notification.message,
            notificationMethod=notification.notificationMethod,
            status=notification.status,
            sentAt=notification.sentAt.isoformat() if notification.sentAt else None,
            deliveredAt=notification.deliveredAt.isoformat()
            if notification.deliveredAt
            else None,
            readAt=notification.readAt.isoformat() if notification.readAt else None,
            createdAt=notification.createdAt.isoformat(),
            updatedAt=notification.updatedAt.isoformat(),
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
        userId=notification.userId,
        alertRuleId=notification.alertRuleId,
        transactionId=notification.transactionId,
        title=notification.title,
        message=notification.message,
        notificationMethod=notification.notificationMethod,
        status=notification.status,
        sentAt=notification.sentAt.isoformat() if notification.sentAt else None,
        deliveredAt=notification.deliveredAt.isoformat()
        if notification.deliveredAt
        else None,
        readAt=notification.readAt.isoformat() if notification.readAt else None,
        createdAt=notification.createdAt.isoformat(),
        updatedAt=notification.updatedAt.isoformat(),
    )


@router.post('/notifications', response_model=AlertNotificationOut)
async def create_alert_notification(
    payload: AlertNotificationCreate, session: AsyncSession = Depends(get_db)
):
    """Create a new alert notification"""
    # Verify user exists
    user_result = await session.execute(select(User).where(User.id == payload.userId))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Verify alert rule exists
    rule_result = await session.execute(
        select(AlertRule).where(AlertRule.id == payload.alertRuleId)
    )
    rule = rule_result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail='Alert rule not found')

    notification = AlertNotification(
        id=str(uuid.uuid4()),
        userId=payload.userId,
        alertRuleId=payload.alertRuleId,
        transactionId=payload.transactionId,
        title=payload.title,
        message=payload.message,
        notificationMethod=payload.notificationMethod,
        status=payload.status,
    )

    session.add(notification)
    await session.commit()
    await session.refresh(notification)

    return AlertNotificationOut(
        id=notification.id,
        userId=notification.userId,
        alertRuleId=notification.alertRuleId,
        transactionId=notification.transactionId,
        title=notification.title,
        message=notification.message,
        notificationMethod=notification.notificationMethod,
        status=notification.status,
        sentAt=notification.sentAt.isoformat() if notification.sentAt else None,
        deliveredAt=notification.deliveredAt.isoformat()
        if notification.deliveredAt
        else None,
        readAt=notification.readAt.isoformat() if notification.readAt else None,
        createdAt=notification.createdAt.isoformat(),
        updatedAt=notification.updatedAt.isoformat(),
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
            if field in ['sentAt', 'deliveredAt', 'readAt'] and value:
                update_data[field] = datetime.fromisoformat(value)
            else:
                update_data[field] = value

    if update_data:
        update_data['updatedAt'] = datetime.utcnow()
        await session.execute(
            update(AlertNotification)
            .where(AlertNotification.id == notification_id)
            .values(**update_data)
        )
        await session.commit()
        await session.refresh(notification)

    return AlertNotificationOut(
        id=notification.id,
        userId=notification.userId,
        alertRuleId=notification.alertRuleId,
        transactionId=notification.transactionId,
        title=notification.title,
        message=notification.message,
        notificationMethod=notification.notificationMethod,
        status=notification.status,
        sentAt=notification.sentAt.isoformat() if notification.sentAt else None,
        deliveredAt=notification.deliveredAt.isoformat()
        if notification.deliveredAt
        else None,
        readAt=notification.readAt.isoformat() if notification.readAt else None,
        createdAt=notification.createdAt.isoformat(),
        updatedAt=notification.updatedAt.isoformat(),
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
        select(AlertNotification).where(AlertNotification.alertRuleId == rule_id)
    )
    notifications = result.scalars().all()

    return [
        AlertNotificationOut(
            id=notification.id,
            userId=notification.userId,
            alertRuleId=notification.alertRuleId,
            transactionId=notification.transactionId,
            title=notification.title,
            message=notification.message,
            notificationMethod=notification.notificationMethod,
            status=notification.status,
            sentAt=notification.sentAt.isoformat() if notification.sentAt else None,
            deliveredAt=notification.deliveredAt.isoformat()
            if notification.deliveredAt
            else None,
            readAt=notification.readAt.isoformat() if notification.readAt else None,
            createdAt=notification.createdAt.isoformat(),
            updatedAt=notification.updatedAt.isoformat(),
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

    if not rule.isActive:
        raise HTTPException(status_code=400, detail='Alert rule is not active')

    # Update trigger count and last triggered time
    await session.execute(
        update(AlertRule)
        .where(AlertRule.id == rule_id)
        .values(
            triggerCount=rule.triggerCount + 1,
            lastTriggered=datetime.utcnow(),
            updatedAt=datetime.utcnow(),
        )
    )
    await session.commit()

    return {
        'message': 'Alert rule triggered successfully',
        'triggerCount': rule.triggerCount + 1,
    }
