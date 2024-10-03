from fastapi import FastAPI

from routers.route_auth import router_auth
from routers.route_problem import router_problem
from schemas import SuccessMsg

app = FastAPI()
app.include_router(router_problem)
app.include_router(router_auth)

@app.get("/", response_model=SuccessMsg)
def root():
    return {"message": "Hello World! Access to /docs for API documentation."}
