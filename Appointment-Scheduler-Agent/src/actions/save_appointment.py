from datetime import datetime
from typing import Dict, Any

from src.schemas import (
    FulfillmentResponse,
    Message,
    WebhookResponse,
    WebhookRequest,
    Text,
)
from src.calendar_utils.calendar_apis import create_event, append_to_google_sheet

from src import logging

logger = logging.getLogger(__name__)


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


async def save_appointment(webhook_request: WebhookRequest) -> WebhookResponse:
    await create_event(
        meeting_date=webhook_request.sessionInfo.parameters["meeting_date"],
        meeting_time=webhook_request.sessionInfo.parameters["meeting_time"],
    )

    await append_to_google_sheet(
        input_dict={
            "Name": webhook_request.sessionInfo.parameters["client_name"]["name"],
            "Email": webhook_request.sessionInfo.parameters["client_email"],
            "Status": "Pending",
            "Timestamp": datetime.now().strftime("%c"),
            "MeetingTime": simple_format_meeting(
                meeting_date=webhook_request.sessionInfo.parameters["meeting_date"],
                meeting_time=webhook_request.sessionInfo.parameters["meeting_time"],
            ),
        }
    )

    return WebhookResponse(
        fulfillmentResponse=FulfillmentResponse(
            messages=[
                Message(text=Text(text=["Your appointment is saved. See you soon."]))
            ]
        )
    )
