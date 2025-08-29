from src.schemas import (
    FulfillmentResponse,
    Message,
    SessionInfo,
    WebhookResponse,
    WebhookRequest,
    Text,
)


async def remove_item(webhook_request: WebhookRequest) -> WebhookResponse:
    """TODO:
    [1] extract the order_cart
    [2] remove the item
    [3] send the response back and replace the order_cart"""

    order_cart = webhook_request.sessionInfo.parameters["order_cart"]
    food_item = webhook_request.sessionInfo.parameters["food_item"]
    quantity = webhook_request.sessionInfo.parameters["quantity"]

    updated_order_cart = []

    for oc in order_cart:
        if oc["food_item"] == food_item:
            oc["quantity"] = int(oc["quantity"]) - quantity
        if int(oc["quantity"]) == 0:
            pass
        else:
            updated_order_cart.append(oc)

    if len(updated_order_cart) == 0:
        return WebhookResponse(
            fulfillmentResponse=FulfillmentResponse(
                messages=[
                    Message(
                        text=Text(
                            text=[
                                "There is no item in yout cart, add items from our menu. Here is menu link."
                            ]
                        )
                    ),
                ]
            ),
            sessionInfo=SessionInfo(
                session=webhook_request.sessionInfo.session,
                parameters={"order_cart": updated_order_cart},
            ),
            targetPage="projects/youtube-dialogflow-cx/locations/global/agents/d23c3df0-06ff-4e38-9ea3-469630288825/flows/f16497c9-3464-4505-8c09-901acd20897d/pages/44a51e5a-d7e9-4df9-b49d-1c94e04ee468",
        )
    else:
        return WebhookResponse(
            fulfillmentResponse=FulfillmentResponse(
                messages=[
                    Message(
                        text=Text(
                            text=[f"We have removed {quantity} number of {food_item}."]
                        )
                    ),
                    Message(text=Text(text=["Do you want to remove another item?"])),
                ]
            ),
            sessionInfo=SessionInfo(
                session=webhook_request.sessionInfo.session,
                parameters={"order_cart": updated_order_cart},
            ),
        )
