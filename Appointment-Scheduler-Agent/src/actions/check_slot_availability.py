from datetime import datetime
from typing import Dict, Any

from src.schemas import (
    FulfillmentResponse,
    Message,
    WebhookResponse,
    WebhookRequest,
    Text,
)
from src.calendar_utils.calendar_apis import is_slot_free


def simple_format_meeting(meeting_date: Dict[str, Any], meeting_time: Dict[str, Any]):
    dt = datetime(
        int(meeting_date["year"]),
        int(meeting_date["month"]),
        int(meeting_date["day"]),
        int(meeting_time["hours"]),
        int(meeting_time["minutes"]),
        int(meeting_time["seconds"]),
    )
    return dt.strftime("%B %d, %Y at %I:%M %p")


TARGET_PAGE = "projects/youtube-dialogflow-cx/locations/global/agents/060a498a-c554-4c86-bbce-0c55aafa23dd/flows/08c71139-88ae-49f7-923d-885d7c562db7/pages/6d592956-1707-4d29-987b-6e9ed2b90f26"


async def check_slot_availability(webhook_request: WebhookRequest) -> WebhookResponse:
    """TODO
    1. we first extract the meeting_date and meeting_time
    2. check the slot availability
    3. shoe the response"""

    is_free = await is_slot_free(
        meeting_date=webhook_request.sessionInfo.parameters["meeting_date"],
        meeting_time=webhook_request.sessionInfo.parameters["meeting_time"],
    )

    date_time_str = simple_format_meeting(
        meeting_date=webhook_request.sessionInfo.parameters["meeting_date"],
        meeting_time=webhook_request.sessionInfo.parameters["meeting_time"],
    )

    if is_free:
        return WebhookResponse(
            fulfillmentResponse=FulfillmentResponse(
                messages=[
                    Message(
                        text=Text(
                            text=[f"We have a slot available at {date_time_str}."]
                        )
                    ),
                    Message(text=Text(text=["Do you confirm that?"])),
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
    else:
        # We need to navigate to a different page
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
