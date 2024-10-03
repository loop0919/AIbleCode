from fastapi import APIRouter, Request, Response
from fastapi.encoders import jsonable_encoder

from auth_utils import AuthJwtCsrf
from database import db_login, db_signup
from schemas import SuccessMsg, UserBody, UserInfo

router_auth = APIRouter()
auth = AuthJwtCsrf()


@router_auth.post("/api/signup", response_model=UserInfo)
async def signup(user: UserBody):
    user = jsonable_encoder(user)
    new_user = await db_signup(user)
    return new_user

@router_auth.post("/api/login", response_model=SuccessMsg)
async def login(response: Response, user: UserBody):
    user = jsonable_encoder(user)
    token = await db_login(user)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True, samesite="none", secure=True)
    return {"message": "Login Success"}
