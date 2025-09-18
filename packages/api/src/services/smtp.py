from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
import smtplib

from dotenv import load_dotenv
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import AlertNotification, NotificationStatus, User

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class EmailNotification(BaseModel):
    to_emails: list[EmailStr]
    subject: str
    body: str
    html_body: str | None = None
    from_email: str | None = None
    reply_to: str | None = None


class SMTPConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    from_email: str
    reply_to_email: str
    use_tls: bool = True
    use_ssl: bool = False


smtp_details = {
    'host': os.getenv('SMTP_HOST', 'localhost'),
    'port': int(os.getenv('SMTP_PORT', 8025)),
    'username': os.getenv('SMTP_USERNAME', ''),
    'password': os.getenv('SMTP_PASSWORD', ''),
    'from_email': os.getenv('SMTP_FROM_EMAIL', 'noreply@localhost'),
    'reply_to_email': os.getenv('SMTP_REPLY_TO_EMAIL', 'noreply@localhost'),
    'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
    'use_ssl': os.getenv('SMTP_USE_SSL', 'false').lower() == 'true',
}

smtp_config = SMTPConfig(**smtp_details)


async def send_smtp_notification(
    notification: AlertNotification,
    session: AsyncSession,
):
    """Send email notification"""

    try:
        user_email_result = await session.execute(
            select(User.email).where(User.id == notification.user_id)
        )
        user_email = user_email_result.scalar_one_or_none()
        if not user_email:
            raise HTTPException(status_code=404, detail='User email not found')

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = notification.title
        msg['From'] = smtp_config.from_email or smtp_config.username

        if smtp_config.reply_to_email:
            msg['Reply-To'] = smtp_config.reply_to_email

        # Add plain text body
        text_part = MIMEText(notification.message, 'plain')
        msg.attach(text_part)

        # Add HTML body if provided
        # if notification.html_body:
        #     html_part = MIMEText(notification.html_body, 'html')
        #     msg.attach(html_part)

        # Connect to SMTP server
        if smtp_config.use_ssl:
            server = smtplib.SMTP_SSL(smtp_config.host, smtp_config.port)
        else:
            server = smtplib.SMTP(smtp_config.host, smtp_config.port)
            if smtp_config.use_tls:
                server.starttls()

        if smtp_config.username and smtp_config.password:
            server.login(smtp_config.username, smtp_config.password)

        # Send email
        try:
            msg['To'] = user_email
            server.send_message(msg)
            logger.info(f'Email sent successfully to {user_email}')
        except Exception as e:
            logger.error(f'Failed to send email to {user_email}: {str(e)}')

        server.quit()

    except Exception as e:
        logger.error(f'Failed to send notifications: {str(e)}')
        raise HTTPException(
            status_code=500, detail=f'Failed to send notifications: {str(e)}'
        ) from e

    finished_at = datetime.now()

    notification.sent_at = finished_at
    notification.status = NotificationStatus.SENT
    return notification
