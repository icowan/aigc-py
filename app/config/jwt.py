import jwt


class JwtToken:

    def __init__(self, secret: str, algorithm: str = "HS256"):
        self._secret = secret

    @classmethod
    def generate_token(cls, payload: dict) -> str:
        headers = dict(typ="jwt", alg="HS256")
        resut = jwt.encode(payload=payload, key=cls._secret, algorithm=cls.algorithm, headers=headers)
        return resut

    @classmethod
    def parse_token(cls, token: str) -> tuple:
        verify_status = False
        try:
            payload_data = jwt.decode(token, cls._secret, algorithms=[cls.algorithm])
            verify_status = True
        except jwt.ExpiredSignatureError:
            payload_data = cls._expire_message
        except Exception as _err:
            payload_data = cls._unknown_error_message
        return verify_status, payload_data
