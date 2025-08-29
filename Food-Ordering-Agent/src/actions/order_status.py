from src.schemas import (
    FulfillmentResponse,
    Message,
    WebhookResponse,
    WebhookRequest,
    Text,
)
from src import logging
from src.database.database import get_order_details

logger = logging.getLogger(__name__)


async def order_status(webhook_request: WebhookRequest) -> WebhookResponse:
    """TODO
    [1] extract the order_cart
    [2] create the order in database"""
    order_number = int(webhook_request.sessionInfo.parameters["order_number"])

    db_order = await get_order_details(order_id=order_number)

    #     #     print(f"Order #{order['order_number']} details:")
    #     #     print(f"Amount: {order['amount']}")
    #     #     print(f"Created at: {order['created_at']}")
    #     #     print("Items:")
    #     #     for item in order["items"]:
    #     #         print(f"- {item['quantity']}x {item['item_name']} (₹{item['price']} each)")
    out_string = f"Order #{db_order['order_number']} details:\n"
    out_string += f"Amount: {db_order['amount']}\n"
    out_string += "Items:\n"

    for item in db_order["items"]:
        out_string += (
            f"- {item['quantity']} x {item['item_name']} (₹{item['price']} each)"
        )

    if order_number:
        return WebhookResponse(
            fulfillmentResponse=FulfillmentResponse(
                messages=[
                    Message(text=Text(text=["Here is your order details."])),
                    Message(text=Text(text=[out_string])),
                    Message(text=Text(text=["Your order will reach you soon."])),
                ]
            )
        )
    else:
        return WebhookResponse(
            fulfillmentResponse=FulfillmentResponse(
                messages=[
                    Message(
                        text=Text(
                            text=[
                                f"We did not find any order with the number {order_number}, please check that."
                            ]
                        )
                    ),
                    Message(text=Text(text=["Let me know if you need anything else."])),
                ]
            )
        )
