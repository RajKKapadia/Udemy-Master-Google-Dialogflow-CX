from typing import List, Dict, Any

from src.schemas import (
    FulfillmentResponse,
    Message,
    WebhookResponse,
    WebhookRequest,
    Text,
)
from src import logging

logger = logging.getLogger(__name__)


async def show_summary(webhook_request: WebhookRequest) -> WebhookResponse:
    """TODO
    [1] extract the order_cart
    [2] create a string
    1. Jeera Rice X 2"""
    order_cart: List[Dict[str, Any]] = webhook_request.sessionInfo.parameters[
        "order_cart"
    ]
    logger.info(order_cart)

    formatted_order_cart = []
    total_price = 0
    i = 1
    for oc in order_cart:
        temp_price = int(oc["quantity"]) * int(oc["price"])
        logger.info(temp_price)
        formatted_order_cart.append(
            f"{i}. {oc['food_item']} X {int(oc['quantity'])} = {temp_price}"
        )
        total_price += temp_price
        i += 1

    logger.info("I am here")

    return WebhookResponse(
        fulfillmentResponse=FulfillmentResponse(
            messages=[
                Message(text=Text(text=["Here is your order summary:"])),
                Message(text=Text(text=["\n".join(formatted_order_cart)])),
                Message(text=Text(text=[f"Total cost: {total_price}"])),
                Message(text=Text(text=["Do you confirm this summary?"])),
            ]
        )
    )
