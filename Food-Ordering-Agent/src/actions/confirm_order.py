from typing import List, Dict, Any

from src.schemas import (
    FulfillmentResponse,
    Message,
    WebhookResponse,
    WebhookRequest,
    Text,
)
from src import logging
from src.database.database import create_order

logger = logging.getLogger(__name__)


async def confirm_order(webhook_request: WebhookRequest) -> WebhookResponse:
    """TODO
    [1] extract the order_cart
    [2] create the order in database"""
    order_cart: List[Dict[str, Any]] = webhook_request.sessionInfo.parameters[
        "order_cart"
    ]
    logger.info(order_cart)

    formatted_order_cart = []
    for oc in order_cart:
        formatted_order_cart.append(
            {"item_name": oc["food_item"], "quantity": oc["quantity"]}
        )

    order_number = await create_order(items=formatted_order_cart)

    return WebhookResponse(
        fulfillmentResponse=FulfillmentResponse(
            messages=[
                Message(text=Text(text=["You order is confirmed."])),
                Message(text=Text(text=[f"Your order number is {order_number}"])),
            ]
        )
    )
