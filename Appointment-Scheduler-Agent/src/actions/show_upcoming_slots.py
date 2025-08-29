from datetime import datetime

from src.schemas import (
    FulfillmentResponse,
    Message,
    WebhookResponse,
    WebhookRequest,
    Text,
)

from src.calendar_utils.calendar_apis import get_random_free_slots


async def show_upcoming_slots(webhook_request: WebhookRequest) -> WebhookResponse:
    """TODO
    1. we want to fetch the free slots
    2. Format the date
    3. Send it in the response
    """
    free_slots = await get_random_free_slots()

    formatted_free_slots = []

    for fs in free_slots:
        formatted_free_slots.append(
            datetime.fromisoformat(fs).strftime("%B %d, %Y at %I:%M %p")
        )

    return WebhookResponse(
        fulfillmentResponse=FulfillmentResponse(
            messages=[
                Message(
                    text=Text(
                        text=["We have the following time slots for the appointment:"]
                    )
                ),
                Message(text=Text(text=["\n".join(formatted_free_slots)])),
                Message(text=Text(text=["Does any of them feel right to you? "])),
                Message(
                    payload={
                        "richContent": [
                            [
                                {
                                    "options": [{"text": "Yes"}, {"text": "No"}],
                                    "type": "chips",
                                }
                            ]
                        ]
                    }
                ),
            ]
        )
    )
