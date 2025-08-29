from typing import Dict, List, Any, Literal

from pydantic import BaseModel, Field


class FulfillmentInfo(BaseModel):
    tag: str


class SessionInfo(BaseModel):
    session: str
    parameters: Dict[str, Any] | None = None


class IntentInfo(BaseModel):
    displayName: str
    confidence: float


class ParameterInfo(BaseModel):
    displayName: str
    required: bool
    state: Literal["PARAMETER_STATE_UNSPECIFIED", "EMPTY", "INVALID", "FILLED"]
    value: Any
    justCollected: bool


class FormInfo(BaseModel):
    parameterInfo: List[ParameterInfo] | None = None


class PageInfo(BaseModel):
    currentPage: str
    displayName: str
    formInfo: FormInfo | None = None


class Text(BaseModel):
    text: List[str]
    redactedText: List[str] | None = None
    allowPlaybackInterruption: bool = False


class Message(BaseModel):
    text: Text | None = None
    payload: Dict[str, Any] | None = None
    responseType: Literal[
        "RESPONSE_TYPE_UNSPECIFIED",
        "ENTRY_PROMPT",
        "PARAMETER_PROMPT",
        "HANDLER_PROMPT",
    ] = Field(default="RESPONSE_TYPE_UNSPECIFIED")
    source: str | None = None


class WebhookRequest(BaseModel):
    detectIntentResponseId: str
    languageCode: str
    fulfillmentInfo: FulfillmentInfo | None = None
    intentInfo: IntentInfo | None = None
    pageInfo: PageInfo | None = None
    sessionInfo: SessionInfo | None = None
    messages: List[Message] | None = None
    payload: Dict[str, Any] | None = None
    text: str
    triggerIntent: str | None = None
    transcript: str | None = None
    triggerEvent: str | None = None
    dtmfDigits: str | None = None


class FulfillmentResponse(BaseModel):
    messages: List[Message]
    mergeBehavior: Literal["MERGE_BEHAVIOR_UNSPECIFIED", "APPEND", "REPLACE"] = Field(
        default="APPEND"
    )


class WebhookResponse(BaseModel):
    fulfillmentResponse: FulfillmentResponse | None = None
    pageInfo: PageInfo | None = None
    sessionInfo: SessionInfo | None = None
    payload: Dict[str, Any] | None = None
    targetFlow: str | None = None
    targetPage: str | None = None
