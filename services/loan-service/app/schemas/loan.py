from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.loan import LoanStatus

class LoanCreate(BaseModel):
    asset_id: int
    responsible_name: str
    loan_date: datetime
    expected_return_date: datetime

class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    responsible_name: str
    loan_date: datetime
    expected_return_date: datetime
    actual_return_date: datetime | None = None
    status: LoanStatus