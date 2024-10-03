from pydantic import BaseModel


class Problem(BaseModel):
    id: str
    title: str
    problem: str
    educational: str


class ProblemBody(BaseModel):
    title: str
    problem: str
    educational: str


class SuccessMsg(BaseModel):
    message: str
