from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.user import User, UserRole
from app.schemas.notification import LabReportResponse, LabRunRequest, LabRunResponse
from app.services.notifications.lab.runner import run_all

router = APIRouter(prefix="/lab", tags=["Laboratorio de patrones"])


@router.post("/notifications", response_model=LabRunResponse)
def run_notification_lab(
    payload: LabRunRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMINISTRADOR)),
):
    """Ejecuta el mismo evento con las tres variantes y devuelve la bitácora de cada una."""
    reports = run_all(db, payload.event_type, payload.site, payload.channel, user.full_name)
    return LabRunResponse(
        event_type=payload.event_type,
        site=payload.site,
        channel=payload.channel,
        reports=[LabReportResponse(**report.as_dict()) for report in reports],
    )