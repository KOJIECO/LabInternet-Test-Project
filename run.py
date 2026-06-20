import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    reload_active = settings.ENVIRONMENT == "development"
    print(f"Starting server on http://{settings.HOST}:{settings.PORT} (reload={reload_active})")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=reload_active)
