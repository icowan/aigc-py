import jwt
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser
from starlette.exceptions import HTTPException

from app.config.config import get_config


async def verify_jwt_token(token):
    try:
        config = get_config()
        # 解码 JWT 令牌
        payload = jwt.decode(token, config.app_secret_key, algorithms=[config.jwt_algorithm])
        # 从 payload 中提取用户信息
        username = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=400, detail='Invalid token payload.')

        # 创建用户凭证和用户对象
        # 注意：这里简单地使用了 SimpleUser，你可能需要根据你的应用自定义用户模型
        return AuthCredentials(["authenticated"]), SimpleUser(username)
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=400, detail='Could not validate credentials.')


class JWTAuthenticationBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return None

        auth = conn.headers["Authorization"]
        try:
            scheme, token = auth.split()
            if scheme.lower() != 'bearer':
                return None

        except ValueError:
            raise HTTPException(status_code=400, detail='Invalid authorization header format.')

        return await verify_jwt_token(token)
