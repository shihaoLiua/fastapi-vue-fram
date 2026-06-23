import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, async_session_factory
from app.redis_client import close_redis
from app.api.auth import router as auth_router
from app.api.users import router as users_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_first_superuser():
    """Create the first superuser if it doesn't exist."""
    from sqlalchemy import select
    from app.models.user import User
    from app.services.auth import create_user

    async with async_session_factory() as db:
        try:
            result = await db.execute(
                select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
            )
            user = result.scalar_one_or_none()

            if not user:
                await create_user(
                    db=db,
                    username=settings.FIRST_SUPERUSER_USERNAME,
                    email=settings.FIRST_SUPERUSER_EMAIL,
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    full_name="Admin",
                    is_superuser=True,
                )
                await db.commit()
                logger.info(
                    f"Superuser created: {settings.FIRST_SUPERUSER_EMAIL}"
                )
            else:
                logger.info("Superuser already exists")
        except Exception as e:
            logger.error(f"Error creating superuser: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    logger.info("Starting up...")
    await init_db()
    await create_first_superuser()
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} started")
    yield
    # Shutdown
    logger.info("Shutting down...")
    await close_redis()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FastAPI + Vue Full-Stack Scaffold",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(users_router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
