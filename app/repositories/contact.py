from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.contact import ContactMessage
from app.schemas.contact import ContactCreate
from typing import List, Dict

class ContactRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create(self, obj_in: ContactCreate) -> ContactMessage:
        db_obj = ContactMessage(
            name=obj_in.name,
            email=obj_in.email,
            phone=obj_in.phone,
            message=obj_in.message
        )
        self.db.add(db_obj)
        return db_obj
        
    async def update_ai_analysis(
        self, message_id: int, sentiment: str, category: str, ai_response: str
    ) -> ContactMessage:
        result = await self.db.execute(select(ContactMessage).where(ContactMessage.id == message_id))
        db_obj = result.scalar_one()
        db_obj.sentiment = sentiment
        db_obj.category = category
        db_obj.ai_response = ai_response
        return db_obj
        
    async def get_total_count(self) -> int:
        result = await self.db.execute(select(func.count(ContactMessage.id)))
        return result.scalar() or 0
        
    async def get_sentiment_distribution(self) -> Dict[str, int]:
        result = await self.db.execute(
            select(ContactMessage.sentiment, func.count(ContactMessage.id))
            .group_by(ContactMessage.sentiment)
        )
        return {row[0] or "neutral": row[1] for row in result.all()}
        
    async def get_category_distribution(self) -> Dict[str, int]:
        result = await self.db.execute(
            select(ContactMessage.category, func.count(ContactMessage.id))
            .group_by(ContactMessage.category)
        )
        return {row[0] or "other": row[1] for row in result.all()}
        
    async def get_recent(self, limit: int = 5) -> List[ContactMessage]:
        result = await self.db.execute(
            select(ContactMessage).order_by(desc(ContactMessage.created_at)).limit(limit)
        )
        return list(result.scalars().all())
