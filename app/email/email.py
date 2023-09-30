from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from app.config import email_settings


class EmailSchema(BaseModel):
    email: List[EmailStr]


class Email:
    def __init__(self, email: List[EmailStr]):
        self.email = email
        pass

    async def sendMail(self):
        # Define the config
        conf = ConnectionConfig(
            MAIL_USERNAME=email_settings.EMAIL_USERNAME,
            MAIL_PASSWORD=email_settings.EMAIL_PASSWORD,
            MAIL_FROM=email_settings.EMAIL_FROM,
            MAIL_PORT=email_settings.EMAIL_PORT,
            MAIL_SERVER=email_settings.EMAIL_HOST,

            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )

        # Define the message options
        message = MessageSchema(
            subject="Welcome",
            recipients=self.email,
            body="<p>Hey, welcome to Kristi!</p>",
            subtype=MessageType.html
        )

        # Send the email
        fm = FastMail(conf)
        await fm.send_message(message)
