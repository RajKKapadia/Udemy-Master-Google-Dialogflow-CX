from src.schemas import (
    FulfillmentResponse,
    Message,
    WebhookResponse,
    WebhookRequest,
    Text,
    SessionInfo,
)
from src import logging
from src.database.database import fetch_item_by_name

logger = logging.getLogger(__name__)


async def check_item_availabilty(webhook_request: WebhookRequest) -> WebhookResponse:
    """TODO
    [1] extract the item from request
    [2] go to database find the item
    [3] found add the item
    [4] not found move to ask parameter page"""
    food_item = webhook_request.sessionInfo.parameters["food_item"]
    quantity = webhook_request.sessionInfo.parameters["quantity"]

    order_cart = []
    if "order_cart" in webhook_request.sessionInfo.parameters.keys():
        order_cart = webhook_request.sessionInfo.parameters["order_cart"]

    logger.info(food_item)
    logger.info(quantity)

    db_item = await fetch_item_by_name(item_name=food_item)

    if db_item:
        logger.info(db_item)

        order_cart.append(
            {"food_item": food_item, "quantity": quantity, "price": db_item["price"]}
        )

        return WebhookResponse(
            fulfillmentResponse=FulfillmentResponse(
                messages=[
                    Message(
                        text=Text(
                            text=[f"We have {food_item}, it costs {db_item['price']}."]
                        )
                    ),
                    Message(text=Text(text=["It is added to you cart."])),
                    Message(text=Text(text=["Do you want to add another item?"])),
                ]
            ),
            sessionInfo=SessionInfo(
                session=webhook_request.sessionInfo.session,
                parameters={"order_cart": order_cart},
            ),
        )
    else:
        return WebhookResponse(
            fulfillmentResponse=FulfillmentResponse(
                messages=[
                    Message(text=Text(text=[f"We don't have {food_item}."])),
                    Message(
                        text=Text(
                            text=["Here is our menu for your reference: menu link"]
                        )
                    ),
                ]
            ),
            targetPage="projects/youtube-dialogflow-cx/locations/global/agents/d23c3df0-06ff-4e38-9ea3-469630288825/flows/f16497c9-3464-4505-8c09-901acd20897d/pages/44a51e5a-d7e9-4df9-b49d-1c94e04ee468",
        )
