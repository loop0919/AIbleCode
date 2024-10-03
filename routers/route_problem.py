from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from starlette.status import (HTTP_201_CREATED, HTTP_404_NOT_FOUND,
                              HTTP_500_INTERNAL_SERVER_ERROR)

from database import (db_create_problem, db_delete_problem, db_get_problem,
                      db_get_problems, db_update_problem)
from schemas import Problem, ProblemBody, SuccessMsg

router_problem = APIRouter()

@router_problem.post("/api/problem", response_model=Problem)
async def create_problem(request: Request, response: Response, problem: ProblemBody):
    problem = jsonable_encoder(problem)
    res = await db_create_problem(problem)
    response.status_code = HTTP_201_CREATED
    
    if res:
        return res
    raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Problem not failed")


@router_problem.get("/api/problem", response_model=list[Problem])
async def get_problems():
    return await db_get_problems()


@router_problem.get("/api/problem/{id}", response_model=Problem)
async def get_problem(id: str):
    problem = await db_get_problem(id)
    if problem:
        return problem
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Problem of ID:{id} not found")


@router_problem.put("/api/problem/{id}", response_model=Problem)
async def update_problem(id: str, problem: ProblemBody):
    problem = jsonable_encoder(problem)
    res = await db_update_problem(id, problem)
    if res:
        return res
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Failed to Update Problem of ID:{id}")


@router_problem.delete("/api/problem/{id}", response_model=SuccessMsg)
async def delete_problem(id: str):
    res = await db_delete_problem(id)
    if res:
        return {"message": f"Problem of ID:{id} deleted"}
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Failed to Delete Problem of ID:{id}")
