from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_302_FOUND

from config import APP_SECRET_KEY, BASE_DIR, UPLOAD_DIR, WEIGHTS_PATH
from db import DB_PATH, init_db
from routers.auth import router as auth_router
from routers.cases import router as cases_router
from routers.dashboard import router as dashboard_router
from services.model import get_device, load_model

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=APP_SECRET_KEY)

if not UPLOAD_DIR.exists():
    UPLOAD_DIR.mkdir(parents=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(auth_router)
app.include_router(cases_router)
app.include_router(dashboard_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db(DB_PATH)
    device = get_device()
    app.state.model = load_model(WEIGHTS_PATH, device)
    app.state.device = device


@app.get("/", response_class=HTMLResponse)
def root(request: Request) -> HTMLResponse:
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)
    return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
