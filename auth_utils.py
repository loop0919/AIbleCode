from datetime import datetime, timedelta

import jwt
from decouple import config
from fastapi import HTTPException
from passlib.context import CryptContext
from pytz import timezone
from starlette.status import HTTP_401_UNAUTHORIZED

JWT_KEY: str = config("JWT_KEY")
TZ_AREA: str = config("TZ_AREA")

class AuthJwtCsrf:
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret_key = JWT_KEY
    
    def generate_hashed_password(self, password: str) -> str:
        return self.pwd_ctx.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_ctx.verify(plain_password, hashed_password)
    
    def encode_jwt(self, user_id: str) -> str:
        payload = {
            "exp": datetime.now(tz=timezone(TZ_AREA)) + timedelta(days=0, minutes=5),
            "iat": datetime.now(tz=timezone(TZ_AREA)),
            "sub": user_id
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def decode_jwt(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")
