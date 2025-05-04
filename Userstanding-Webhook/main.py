from fastapi import FastAPI
from fastapi.requests import Request

app = FastAPI(title="Dialogflow Webhook")


@app.get("/")
async def handle_get():
    return "OK"


@app.post("/webhook")
async def handle_post_webhook(request: Request):
    body = await request.json()
    print(body)
    return {
        "fulfillmentResponse": {"messages": [{"text": {"text": ["Sample response"]}}]}
    }
