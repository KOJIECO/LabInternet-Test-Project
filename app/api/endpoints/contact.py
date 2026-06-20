from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import rate_limit_check
from app.schemas.contact import ContactCreate, ContactResponse, HealthResponse, MetricsResponse
from app.services.contact import ContactService
from app.services.ai import ai_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/contact", 
    response_model=ContactResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_check)]
)
async def submit_contact_form(
    payload: ContactCreate,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"API Request: POST /api/contact from email={payload.email}")
    service = ContactService(db)
    result = await service.process_contact_submission(payload)
    return result

@router.get("/health", response_model=HealthResponse)
async def check_health(db: AsyncSession = Depends(get_db)):
    logger.info("API Request: GET /api/health")
    db_status = "healthy"
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Healthcheck database connection error: {e}")
        db_status = "unhealthy"

    ai_status = "active" if ai_service.client_configured else "fallback_mode"

    overall_status = "healthy"
    if db_status == "unhealthy":
        overall_status = "unhealthy"

    return HealthResponse(
        status=overall_status,
        database=db_status,
        ai_service=ai_status
    )

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    logger.info("API Request: GET /api/metrics")
    service = ContactService(db)
    metrics_data = await service.get_metrics()
    return metrics_data
