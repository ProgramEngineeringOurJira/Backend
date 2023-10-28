from uuid import UUID, uuid4

from fastapi import Request
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from app.config import email_settings
from app.core.redis_session import Redis
from app.schemas.models.auth import UserRegister


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
    fm: FastMail = FastMail(conf)

    async def sendRegistrationMail(self, request: Request, redis: Redis, user_register: UserRegister):
        # Определяет тело письма и его получателя
        uuid_id = str(uuid4())
        url = f"{request.url.scheme}://{request.url.hostname}:{request.url.port}/v1/verifyemail/{uuid_id}"
        await redis.set_uuid_email(uuid_id, user_register)
        message = MessageSchema(
            subject="Welcome",
            recipients=[user_register.email],
            body="<p>Hey, welcome to Kristi! To confirm the email address, "
            + f"follow <a href={url}>this link</a></p>",
            subtype=MessageType.html,
        )
        await self.fm.send_message(message)

    async def sendInvitationMail(self, request: Request, email: EmailStr, workplace_id: UUID, workplace_name: str):
        url = (
            f"{request.url.scheme}://{request.url.hostname}:{request.url.port}/v1/workplaces/{workplace_id}/invitation"
        )
        message = MessageSchema(
            subject="Welcome",
            recipients=[email],
            body=f'<p>Hi! You have been invited to the workplace "{workplace_name}". '
            + f"Follow <a href={url}>this link</a> to connect to the wopkplace</p>",
            subtype=MessageType.html,
        )
        await self.fm.send_message(message)
