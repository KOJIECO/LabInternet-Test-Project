import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.database import Base, engine
from app.core.security import rate_limiter

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    rate_limiter.requests.clear()
    yield
    
@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "healthy"
    
@pytest.mark.asyncio
async def test_submit_contact():
    payload = {
        "name": "Тестовый Пользователь",
        "email": "test@example.com",
        "phone": "+79998887766",
        "message": "Тестовое сообщение длиной более пяти символов"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/contact", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data["sentiment"] is not None
    assert data["category"] is not None
    
@pytest.mark.asyncio
async def test_metrics():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "name": "Иван",
            "email": "ivan@example.com",
            "phone": "+79998887766",
            "message": "Привет! Вопрос по стеку технологий."
        }
        await ac.post("/api/contact", json=payload)
        response = await ac.get("/api/metrics")
        
    assert response.status_code == 200
    data = response.json()
    assert data["total_messages"] >= 1
    assert "sentiment_distribution" in data
    assert "category_distribution" in data
    assert len(data["recent_messages"]) >= 1
