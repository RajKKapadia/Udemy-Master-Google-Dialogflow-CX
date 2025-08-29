from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.utils import verify_api_key
from src import logging
from src.schemas import (
    WebhookRequest,
    WebhookResponse,
    FulfillmentResponse,
    Message,
    Text,
)
from src.actions.show_upcoming_slots import show_upcoming_slots
from src.actions.check_slot_availability import check_slot_availability
from src.actions.save_appointment import save_appointment
from src.actions.show_upcoming_slots_for_the_day import show_upcoming_slots_for_the_day

logger = logging.getLogger(__name__)

app = FastAPI(title="Dialogflow CX Webhook API")

templates = Jinja2Templates(directory="templates")


@app.get("/chat", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/webhook", response_model=WebhookResponse)
async def dialogflow_webhook(
    webhook_request: WebhookRequest, is_verified: bool = Depends(verify_api_key)
):
    try:
        tag = webhook_request.fulfillmentInfo.tag
        if tag == "showUpcomingSlots":
            return await show_upcoming_slots(webhook_request=webhook_request)
        elif tag == "saveAppointment":
            return await save_appointment(webhook_request=webhook_request)
        elif tag == "checkSlotAvailability":
            return await check_slot_availability(webhook_request=webhook_request)
        elif tag == "showUpcomingSlotsForTheDay":
            return await show_upcoming_slots_for_the_day(
                webhook_request=webhook_request
            )
        else:
            return WebhookResponse(
                fulfillmentResponse=FulfillmentResponse(
                    messages=[
                        Message(text=Text(text=[f"No handler for the tag: {tag}"]))
                    ]
                )
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Webhook processing error: {str(e)}"
        )
