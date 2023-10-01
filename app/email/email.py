from typing import List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr

from app.config import email_settings


class EmailSchema(BaseModel):
    email: List[EmailStr]


class Email:
    def __init__(self, url: str, email: List[EmailStr]):
        self.email = email
        self.url = url
        pass

    async def sendMail(self):
        # Конфигурация для отправляемых сообщений
        conf = ConnectionConfig(
            MAIL_USERNAME=email_settings.EMAIL_USERNAME,
            MAIL_PASSWORD=email_settings.EMAIL_PASSWORD,
            MAIL_FROM=email_settings.EMAIL_FROM,
            MAIL_PORT=email_settings.EMAIL_PORT,
            MAIL_SERVER=email_settings.EMAIL_HOST,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )

        # Определяет тело письма и его получателя
        message = MessageSchema(
            subject="Welcome",
            recipients=self.email,
            body="<p>Hey, welcome to Kristi! To confirm the email address, " +
                    f"follow <a href={self.url}>this link</a></p>",
            subtype=MessageType.html
        )

        # Send the email
        fm = FastMail(conf)
        await fm.send_message(message)
