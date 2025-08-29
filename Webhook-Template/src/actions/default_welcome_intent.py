from src.schemas import (
    FulfillmentResponse,
    Message,
    WebhookResponse,
    WebhookRequest,
    Text,
    SessionInfo,
)


async def default_welcome_intent(webhook_request: WebhookRequest) -> WebhookResponse:
    return WebhookResponse(
        fulfillmentResponse=FulfillmentResponse(
            messages=[
                Message(text=Text(text=["Added a variable in session."])),
            ]
        ),
        sessionInfo=SessionInfo(
            session=webhook_request.sessionInfo.session,
            parameters={
                "someKey": "somevalue",
                "count": webhook_request.sessionInfo.parameters["count"] + 1,
            },
        ),
    )
