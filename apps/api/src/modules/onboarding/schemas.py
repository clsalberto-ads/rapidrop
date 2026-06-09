
from pydantic import BaseModel


class OnboardingStatusResponse(BaseModel):
    current_step: int
    status: str
    completed_at: str | None = None
    steps_total: int = 5


class OnboardingStepUpdate(BaseModel):
    step: int
