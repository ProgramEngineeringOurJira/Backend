from typing import List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.config import email_settings


class Email:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Email, cls).__new__(cls)
        return cls.instance
    
    # Конфигурация для отправляемых сообщений
    conf: ConnectionConfig = ConnectionConfig(
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

    # Конструктор сообщения по конфигурации
    fm : FastMail = FastMail(conf)

    async def sendMail(self, url: str, email: ):
        # Определяет тело письма и его получателя
        message = MessageSchema(
            subject="Welcome",
            recipients=[email],
            body="<p>Hey, welcome to Kristi! To confirm the email address, "
            + f"follow <a href={url}>this link</a></p>",
            subtype=MessageType.html,
        )

        await self.fm.send_message(message)
