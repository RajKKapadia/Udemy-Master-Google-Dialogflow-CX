from datetime import datetime

from src.schemas import (
    FulfillmentResponse,
    Message,
    WebhookResponse,
    WebhookRequest,
    Text,
)
from src.calendar_utils.calendar_apis import get_free_slots_for_day


TARGET_PAGE = "projects/youtube-dialogflow-cx/locations/global/agents/060a498a-c554-4c86-bbce-0c55aafa23dd/flows/08c71139-88ae-49f7-923d-885d7c562db7/pages/6d592956-1707-4d29-987b-6e9ed2b90f26"


async def show_upcoming_slots_for_the_day(
    webhook_request: WebhookRequest,
) -> WebhookResponse:
    free_slots = await get_free_slots_for_day(
        meeting_date=webhook_request.sessionInfo.parameters["meeting_date"]
    )

    formatted_free_slots = []

    for fs in free_slots:
        formatted_free_slots.append(
            datetime.fromisoformat(fs).strftime("%B %d, %Y at %I:%M %p")
        )

    if len(formatted_free_slots) == 0:
        # Navigate to another page
        return WebhookResponse(
            fulfillmentResponse=FulfillmentResponse(
                messages=[
                    Message(
                        text=Text(
                            text=["We are sorry, but we don't have any free slots."]
                        )
                    )
                ],
            ),
            targetPage=TARGET_PAGE,
        )
    else:
        return WebhookResponse(
            fulfillmentResponse=FulfillmentResponse(
                messages=[
                    Message(
                        text=Text(
                            text=[
                                "We have the following time slots for the appointment:"
                            ]
                        )
                    ),
                    Message(text=Text(text=["\n".join(formatted_free_slots)])),
                    Message(text=Text(text=["Does any of them feel right to you?"])),
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
