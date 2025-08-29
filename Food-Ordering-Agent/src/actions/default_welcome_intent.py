from src.schemas import (
    FulfillmentResponse,
    Message,
    WebhookResponse,
    WebhookRequest,
    Text,
)


async def default_welcome_intent(webhook_request: WebhookRequest) -> WebhookResponse:
    return WebhookResponse(
        fulfillmentResponse=FulfillmentResponse(
            messages=[
                Message(text=Text(text=["Sample response"])),
                Message(
                    payload={
                        "richContent": [
                            [
                                {
                                    "options": [
                                        {"text": "Option two"},
                                        {"text": "Option one"},
                                    ],
                                    "type": "chips",
                                }
                            ]
                        ]
                    }
                ),
            ]
        )
    )
