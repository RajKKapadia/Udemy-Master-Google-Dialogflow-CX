from typing import Annotated, Any, Dict

from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.utils import send_message, verify_api_key
from src import detect_intent, logging
from src.schemas import (
    WebhookRequest,
    WebhookResponse,
    FulfillmentResponse,
    Message,
    Text,
)
from src.actions.check_item_availability import check_item_availabilty
from src.actions.show_temp_summary import show_temp_summary
from src.actions.remove_item import remove_item
from src.actions.show_summary import show_summary
from src.actions.confirm_order import confirm_order
from src.actions.order_status import order_status

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
        if tag == "checkItemAvailabilty":
            return await check_item_availabilty(webhook_request=webhook_request)
        elif tag == "showTempSummary":
            return await show_temp_summary(webhook_request=webhook_request)
        elif tag == "removeItem":
            return await remove_item(webhook_request=webhook_request)
        elif tag == "showSummary":
            return await show_summary(webhook_request=webhook_request)
        elif tag == "confirmOrder":
            return await confirm_order(webhook_request=webhook_request)
        elif tag == "orderStatus":
            return await order_status(webhook_request=webhook_request)
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


@app.post("/whatsapp")
async def handle_post_whatsapp(form_data: Annotated[Dict[str, Any], Form]):
    """TODO
    (0) extract the information from the twilio requests
    (1) detect the intent
    (2) get all the messages that we want to send
    (3) send all messages
    """
    logger.info(form_data)
    message = form_data["Body"]
    sender_id = form_data["From"]

    """Translation service, detect the language code"""

    response_messages = await detect_intent.detect_intent_async(
        session_id=f"{sender_id}", text_input=message
    )

    if response_messages["status"]:
        async for m in response_messages["message"]:
            await send_message(to=sender_id, message=m)
        return "OK"
    else:
        return "OK"
