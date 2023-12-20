import jwt
from datetime import datetime, timedelta

def generate_jwt_token(user_email, role, secret_key, expires_in_days=1):

    expiration = datetime.utcnow() + timedelta(days=expires_in_days)
    token_payload = {
        "sub": user_email,  
        "role": role, 
        "exp": expiration 
    }
    token = jwt.encode(token_payload, secret_key, algorithm="HS384")
    return token