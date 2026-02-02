import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from config import UPLOAD_DIR
from db import get_db, fetch_one, execute
from deps import require_user
from services.model import predict_image
from ui import templates

router = APIRouter()


@router.get("/cases/new", response_class=HTMLResponse)
def new_case_form(
    request: Request,
    user: dict = Depends(require_user),
) -> HTMLResponse:
    return templates.TemplateResponse("new_case.html", {"request": request, "user": user, "error": None})


@router.post("/cases/new", response_class=HTMLResponse)
def create_case(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    dob: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    xray: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db),
    user: dict = Depends(require_user),
) -> HTMLResponse:
    if not xray.filename:
        return templates.TemplateResponse(
            "new_case.html",
            {"request": request, "user": user, "error": "Please upload an X-ray image."},
        )

    ext = Path(xray.filename).suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg"}:
        return templates.TemplateResponse(
            "new_case.html",
            {"request": request, "user": user, "error": "Only PNG and JPG images are supported."},
        )

    file_id = f"{uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / file_id
    with file_path.open("wb") as f:
        shutil.copyfileobj(xray.file, f)

    label, prob = predict_image(request.app.state.model, request.app.state.device, file_path)
    urgency = "rush" if label == "pneumonia" else "normal"

    patient_id = execute(
        db,
        """
        INSERT INTO patients (first_name, last_name, dob, gender, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (first_name, last_name, dob, gender, notes, datetime.utcnow().isoformat()),
    )

    execute(
        db,
        """
        INSERT INTO xrays (patient_id, filename, original_filename, prediction_label, probability, urgency, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (patient_id, file_id, xray.filename, label, prob, urgency, datetime.utcnow().isoformat()),
    )

    return RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)


@router.get("/cases/{case_id}", response_class=HTMLResponse)
def case_detail(
    case_id: int,
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
    user: dict = Depends(require_user),
) -> HTMLResponse:
    row = fetch_one(
        db,
        """
        SELECT x.id, x.original_filename, x.prediction_label, x.probability, x.urgency,
               x.created_at, x.filename,
               p.first_name, p.last_name, p.dob, p.gender, p.notes
        FROM xrays x
        JOIN patients p ON p.id = x.patient_id
        WHERE x.id = ?
        """,
        (case_id,),
    )
    if not row:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse(
        "case_detail.html",
        {"request": request, "user": user, "case": row},
    )


@router.post("/cases/{case_id}/delete")
def delete_case(
    case_id: int,
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
    user: dict = Depends(require_user),
) -> RedirectResponse:
    row = fetch_one(
        db,
        "SELECT filename FROM xrays WHERE id = ?",
        (case_id,),
    )
    if not row:
        raise HTTPException(status_code=404)

    execute(db, "DELETE FROM xrays WHERE id = ?", (case_id,))

    file_path = UPLOAD_DIR / row["filename"]
    if file_path.exists():
        file_path.unlink()

    return RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)
