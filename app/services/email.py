import os
import json
import logging
from datetime import datetime, timezone
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.use_mock = settings.USE_MOCK_EMAIL
        self.mock_dir = os.path.join("logs", "emails")
        if self.use_mock:
            if not os.path.exists(self.mock_dir):
                os.makedirs(self.mock_dir)
            logger.info("Email service initialized in MOCK mode.")

    async def send_contact_emails(
        self, 
        name: str, 
        email: str, 
        phone: str, 
        message: str,
        sentiment: str,
        category: str,
        ai_response: str
    ) -> bool:
        owner_subject = f"Новое обращение на сайте от {name} [{category.upper()}]"
        owner_body = f"""У вас новое обращение через форму обратной связи!

Отправитель: {name}
Email: {email}
Телефон: {phone}

Сообщение:
{message}

------------------------------------------
AI АНАЛИЗ (Gemini):
Тональность: {sentiment}
Категория: {category}
Предложенный ответ:
{ai_response}
"""

        user_subject = f"Спасибо за ваше обращение, {name}!"
        user_body = f"""Здравствуйте, {name}!

Мы получили ваше сообщение через форму обратной связи:
"{message}"

Мы свяжемся с вами по указанным контактам (Email: {email}, Телефон: {phone}) в ближайшее время.

С уважением,
Команда разработчика
"""
        
        if self.use_mock:
            return await self._send_mock_email(
                sender=email,
                owner_subject=owner_subject,
                owner_body=owner_body,
                user_subject=user_subject,
                user_body=user_body
            )
            
        try:
            await self._send_smtp_email(
                to_addr=settings.CONTACT_RECEIVER_EMAIL,
                subject=owner_subject,
                body=owner_body
            )
            await self._send_smtp_email(
                to_addr=email,
                subject=user_subject,
                body=user_body
            )
            logger.info(f"SMTP emails sent successfully to {settings.CONTACT_RECEIVER_EMAIL} and {email}")
            return True
        except Exception as e:
            logger.error(f"SMTP send failed: {e}. Falling back to writing mock files.")
            await self._send_mock_email(
                sender=email,
                owner_subject=owner_subject,
                owner_body=owner_body,
                user_subject=user_subject,
                user_body=user_body
            )
            return False

    async def _send_smtp_email(self, to_addr: str, subject: str, body: str):
        message = MIMEMultipart()
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = to_addr
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain", "utf-8"))

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=settings.SMTP_PORT == 465,
            start_tls=settings.SMTP_PORT == 587
        )

    async def _send_mock_email(
        self, 
        sender: str, 
        owner_subject: str, 
        owner_body: str, 
        user_subject: str, 
        user_body: str
    ) -> bool:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        filename = f"email_{timestamp}.json"
        filepath = os.path.join(self.mock_dir, filename)
        
        email_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "owner_email": {
                "to": settings.CONTACT_RECEIVER_EMAIL,
                "from": settings.SMTP_FROM_EMAIL,
                "subject": owner_subject,
                "body": owner_body
            },
            "user_email": {
                "to": sender,
                "from": settings.SMTP_FROM_EMAIL,
                "subject": user_subject,
                "body": user_body
            }
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(email_data, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Mock email saved to: {filepath}")
        return True

email_service = EmailService()
