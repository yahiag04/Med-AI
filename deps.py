from fastapi import HTTPException, Request


def require_user(request: Request) -> dict:
    user_id = request.session.get("user_id")
    username = request.session.get("username")
    if not user_id:
        raise HTTPException(status_code=401)
    return {"id": user_id, "username": username}
