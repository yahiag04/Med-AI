from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from auth import hash_password, verify_password
from db import get_db, fetch_one, execute
from ui import templates

router = APIRouter()


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@router.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Any = Depends(get_db),
) -> HTMLResponse:
    existing = fetch_one(db, "SELECT id FROM users WHERE username = %s", (username,))
    if existing:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Username already exists."},
        )
    password_hash, salt = hash_password(password)
    execute(
        db,
        "INSERT INTO users (username, password_hash, salt, created_at) VALUES (%s, %s, %s, %s)",
        (username, password_hash, salt, datetime.utcnow().isoformat()),
    )
    return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Any = Depends(get_db),
) -> HTMLResponse:
    user = fetch_one(db, "SELECT id, password_hash, salt FROM users WHERE username = %s", (username,))
    if not user or not verify_password(password, user["password_hash"], user["salt"]):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password."},
        )
    request.session["user_id"] = user["id"]
    request.session["username"] = username
    return RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)


@router.post("/logout")
def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
