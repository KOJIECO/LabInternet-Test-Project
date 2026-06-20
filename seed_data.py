import asyncio
import logging
from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal, Base, engine
from app.models.contact import ContactMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed():
    logger.info("Starting database seeding...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with SessionLocal() as db:
        messages = [
            ContactMessage(
                name="Алексей HR",
                email="alex.hr@company.ru",
                phone="+79991112233",
                message="Здравствуйте! Ищем опытного Python/FastAPI разработчика на проект автоматизации. Заинтересовало ваше портфолио.",
                sentiment="positive",
                category="job_offer",
                ai_response="Здравствуйте, Алексей! Спасибо за проявленный интерес к моему профилю. Буду рад обсудить подробности вакансии."
            ),
            ContactMessage(
                name="Дмитрий",
                email="dmitry@techcorp.com",
                phone="+79992223344",
                message="Привет, Eduard. Можем ли мы использовать вашу систему управления товарами BIGPLAY на коммерческой основе?",
                sentiment="neutral",
                category="partnership",
                ai_response="Приветствую, Дмитрий! Спасибо за предложение. Мы можем обсудить условия интеграции и лицензирования."
            ),
            ContactMessage(
                name="Елена",
                email="elena@gmail.com",
                phone="+79993334455",
                message="Какую именно СУБД вы рекомендуете использовать для больших нагрузок: PostgreSQL или MongoDB?",
                sentiment="neutral",
                category="question",
                ai_response="Елена, здравствуйте! Для реляционных данных под нагрузкой PostgreSQL обычно является лучшим решением."
            ),
            ContactMessage(
                name="КриптоРеклама",
                email="crypto_ads@spam.org",
                phone="+1234567890",
                message="Уникальное предложение! Заработайте 1000$ в день на нашей криптоплатформе прямо сейчас!",
                sentiment="negative",
                category="spam",
                ai_response="Спасибо за обращение. Спам-предложения не рассматриваются."
            ),
            ContactMessage(
                name="Иван Петров",
                email="ivan.p@mail.ru",
                phone="+79994445566",
                message="Отличный стек технологий и прекрасное оформление портфолио. Удачи в поиске проектов!",
                sentiment="positive",
                category="other",
                ai_response="Иван, спасибо большое за вашу поддержку и теплые слова!"
            )
        ]
        db.add_all(messages)
        await db.commit()
        logger.info("Successfully seeded 5 initial records.")
        
if __name__ == "__main__":
    asyncio.run(seed())
