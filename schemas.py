from typing import Optional

from fastapi import Query
from pydantic import BaseModel


class Problem(BaseModel):
    id: str = Query(..., example="0123456789abcdef01234567")
    title: str = Query(..., example="タイトル")
    problem: str = Query(..., example="## 問題文")
    educational: str = Query(..., example="## 解説")


class ProblemBody(BaseModel):
    title: str = Query(..., example="タイトル")
    problem: str = Query(..., example="## 問題文")
    educational: str = Query(..., example="## 解説")


class SuccessMsg(BaseModel):
    message: str = Query(..., example="Success")


class UserBody(BaseModel):
    user_id: str = Query(..., example="user_id")
    password: str = Query(..., example="password")

class UserInfo(BaseModel):
    id: Optional[str] = None
    user_id: str = None
