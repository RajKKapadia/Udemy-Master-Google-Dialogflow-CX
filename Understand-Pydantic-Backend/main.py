from fastapi import FastAPI

from schemas import CustomRequest, CustomResponse

app = FastAPI()


@app.get("/")
async def handle_get_home():
    return "OK"


@app.post("/test", response_model=CustomResponse)
async def handle_post_test(custom_req_object: CustomRequest):
    print(custom_req_object)
    return CustomResponse(status="OK", message="Success.")
