from fastapi import HTTPException, status, Header
from twilio.rest import Client
from typing import Optional
from src import config


async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> bool:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is required",
        )

    if config.X_API_KEY != x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return True


client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)


async def send_message(to: str, message: str) -> None:
    """
    Send message to a Telegram user.

    Parameters:
        - to(str): sender whatsapp number in this whatsapp:+919876543210 form
        - message(str): text message to send

    Returns:
        - None
    """
    _ = await client.messages.create(from_="whatsapp:+14155238886", body=message, to=to)
