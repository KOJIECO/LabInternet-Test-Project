import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.contact import ContactRepository
from app.schemas.contact import ContactCreate
from app.models.contact import ContactMessage
from app.services.ai import ai_service
from app.services.email import email_service

logger = logging.getLogger(__name__)

class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def process_contact_submission(self, obj_in: ContactCreate) -> ContactMessage:
        logger.info(f"Processing new contact submission from {obj_in.name}")
        db_obj = await self.repository.create(obj_in)
        await self.repository.db.commit()
        await self.repository.db.refresh(db_obj)
        
        logger.info(f"Analyzing message {db_obj.id} with AI service")
        analysis = await ai_service.analyze_message(
            name=db_obj.name,
            message=db_obj.message
        )
        
        logger.info(f"Enriching message {db_obj.id} database record with AI results")
        db_obj = await self.repository.update_ai_analysis(
            message_id=db_obj.id,
            sentiment=analysis["sentiment"],
            category=analysis["category"],
            ai_response=analysis["suggested_reply"]
        )
        await self.repository.db.commit()
        await self.repository.db.refresh(db_obj)
        
        logger.info(f"Triggering email dispatching workflow for message {db_obj.id}")
        await email_service.send_contact_emails(
            name=db_obj.name,
            email=db_obj.email,
            phone=db_obj.phone,
            message=db_obj.message,
            sentiment=db_obj.sentiment,
            category=db_obj.category,
            ai_response=db_obj.ai_response
        )
        
        return db_obj

    async def get_metrics(self) -> dict:
        total = await self.repository.get_total_count()
        sentiment = await self.repository.get_sentiment_distribution()
        category = await self.repository.get_category_distribution()
        recent = await self.repository.get_recent(limit=5)
        
        return {
            "total_messages": total,
            "sentiment_distribution": sentiment,
            "category_distribution": category,
            "recent_messages": recent
        }
