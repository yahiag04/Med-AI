from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from db import get_db, fetch_all
from deps import require_user
from ui import templates

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Any = Depends(get_db),
    user: dict = Depends(require_user),
) -> HTMLResponse:
    rows = fetch_all(
        db,
        """
        SELECT x.id, x.original_filename, x.prediction_label, x.probability, x.urgency,
               x.created_at, x.filename,
               p.first_name, p.last_name, p.dob, p.gender
        FROM xrays x
        JOIN patients p ON p.id = x.patient_id
        ORDER BY (x.urgency = 'rush') DESC, x.created_at DESC
        """,
    )
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "cases": rows},
    )
