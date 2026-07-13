import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from fastapi_mail import MessageSchema, MessageType
from sqlalchemy.ext.asyncio import AsyncSession
from app.notifications.email import mail, conf
from app.models.notification import Notification
from app.schemas.enums import NotificationType, NotificationChannel, NotificationStatus
from app.config import settings

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def send_email(
        self,
        user_id: uuid.UUID,
        email_to: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        notification_type: NotificationType
    ) -> Notification:
        
        # 1. Log the notification as pending
        notification = Notification(
            user_id=user_id,
            type=notification_type.value,
            channel=NotificationChannel.EMAIL.value,
            recipient=email_to,
            subject=subject,
            content=template_name, # Storing template name as content reference
            status=NotificationStatus.PENDING.value
        )
        self.db.add(notification)
        await self.db.commit()

        # 2. Prepare Email Message
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            template_body=context,
            subtype=MessageType.html
        )

        try:
            # 3. Send Email
            if not settings.is_testing:
                await mail.send_message(message, template_name=template_name)
            
            notification.status = NotificationStatus.SENT.value
            notification.sent_at = datetime.now(timezone.utc)
            await self.db.commit()
            
        except Exception as e:
            # 4. Handle Failure
            notification.status = NotificationStatus.FAILED.value
            notification.error_message = str(e)
            await self.db.commit()
            raise e

        return notification
