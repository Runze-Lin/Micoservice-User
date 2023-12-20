import jwt
from datetime import datetime, timedelta

def generate_jwt_token(user_id, role, secret_key, expires_in_days=1):
    print(f"Generating JWT token for user ID: {user_id}, role: {role}")

    try:
        expiration = datetime.utcnow() + timedelta(days=expires_in_days)
        print(f"Token will expire at: {expiration}")

        token_payload = {
            "sub": user_id, 
            "role": role,
            "exp": expiration
        }
        print(f"Token payload: {token_payload}")

        token = jwt.encode(token_payload, secret_key, algorithm="HS384")
        print(f"Token generated: {token}")

        return token

    except Exception as e:
        print(f"Error generating token: {e}")
        raise e
