from typing import Any, List, Optional

import motor.motor_asyncio
from bson import ObjectId
from decouple import config

MONGO_API_KEY = config('MONGO_API_KEY')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY)
database = client.API_DB
collection_users = database.users
collection_problems = database.problems


def serialize(data: Any) -> dict:
    """
    MongoDB のオブジェクトをdictに変換する。  
    ただし、"_id"を"id"に変換する。
    
    Args:
        data (Any): MongoDBのオブジェクト
    
    Returns:
        dict: 変換後のdict
    """
    return {("id" if key == "_id" else key): str(value) for key, value in data.items()}


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
