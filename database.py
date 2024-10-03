from typing import Any, List, Optional

import motor.motor_asyncio
from bson import ObjectId
from decouple import config
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from auth_utils import AuthJwtCsrf

MONGO_API_KEY = config('MONGO_API_KEY')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY)
database = client.API_DB
collection_users = database.users
collection_problems = database.problems

auth = AuthJwtCsrf()

def serialize(data: Any, not_show: List[str] = []) -> dict:
    """
    MongoDB のオブジェクトをdictに変換する。  
    ただし、"_id"を"id"に変換する。
    
    Args:
        data (Any): MongoDBのオブジェクト
        not_show (List[str], optional): 表示しないキーのリスト
    
    Returns:
        dict: 変換後のdict
    """
    return {("id" if key == "_id" else key): str(value) for key, value in data.items() if key not in not_show}


async def db_create_problem(data: dict) -> Optional[dict]:
    """
    問題をMongoDBに登録する。
    
    Args:
        data (dict): 登録する問題の情報
    
    Returns:
        Optional[dict]: 登録した問題の情報, 登録に失敗した場合はNone
    """
    problem = await collection_problems.insert_one(data)
    new_problem = await collection_problems.find_one({"_id": problem.inserted_id})
    
    if new_problem:
        return serialize(new_problem)
    
    return None


async def db_get_problems() -> List[dict]:
    """
    問題の一覧を取得する。
    
    Returns:
        List[dict]: 問題の一覧
    """
    problems = []
    
    for problem in await collection_problems.find().to_list(length=100):
        problems.append(serialize(problem))
    
    return problems


async def db_get_problem(id: str) -> Optional[dict]:
    """
    問題を取得する。
    
    Args:
        id (str): 問題のID
    
    Returns:
        Optional[dict]: 問題の情報, 問題が存在しない場合はNone
    """
    problem = await collection_problems.find_one({"_id": ObjectId(id)})
    
    if problem:
        return serialize(problem)
    
    return None


async def db_update_problem(id: str, data: dict) -> Optional[dict]:
    """
    問題の情報を更新する。
    
    Args:
        id (str): 問題のID
        data (dict): 更新する情報
    
    Returns:
        Optional[dict]: 更新後の問題の情報, 更新に失敗した場合はNone
    """
    problem = await collection_problems.find_one({"_id": ObjectId(id)})
    
    if problem:
        updated_problem = await collection_problems.update_one({"_id": ObjectId(id)}, {"$set": data})
        
        if updated_problem.modified_count > 0:
            new_problem = await collection_problems.find_one({"_id": ObjectId(id)})
            return serialize(new_problem)
    
    return None


async def db_delete_problem(id: str) -> bool:
    """
    問題を削除する。
    
    Args:
        id (str): 問題のID
    
    Returns:
        bool: 削除に成功した場合はTrue, 失敗した場合はFalse
    """
    problem = await collection_problems.find_one({"_id": ObjectId(id)})
    
    if problem:
        deleted_problem = await collection_problems.delete_one({"_id": ObjectId(id)})
        
        if deleted_problem.deleted_count > 0:
            return True
    
    return False


async def db_signup(data: dict) -> dict:
    """
    ユーザーを登録する。
    
    Args:
        data (dict): 登録するユーザーの情報
    
    Returns:
        Optional[dict]: 登録したユーザーの情報, 登録に失敗した場合はNone
    
    Raises:
        HTTPException: ユーザーが既に存在する場合、またはパスワードが8文字未満の場合
    """
    user_id = data.get("user_id")
    password = data.get("password")
    overlap_user = await collection_users.find_one({"user_id": user_id})
    
    if overlap_user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User already exists")
    
    if not password or len(password) < 8:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters")
    
    user = await collection_users.insert_one({
        "user_id": user_id,
        "password": auth.generate_hashed_password(password)
    })
    new_user = await collection_users.find_one({"_id": user.inserted_id})
    
    return serialize(new_user, not_show=["password"])

async def db_login(data: dict) -> str:
    """
    ログインする。
    
    Args:
        data (dict): ログインするユーザーの情報
    
    Returns:
        str: トークン
    
    Raises:
        HTTPException: ユーザーが存在しない場合、またはパスワードが一致しない場合
    """
    user_id = data.get("user_id")
    password = data.get("password")
    
    user = await collection_users.find_one({"user_id": user_id})
    
    if not user or not auth.verify_password(password, user["password"]):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Incorrect user_id or password")
    
    token = auth.encode_jwt(user["user_id"])
    return token
