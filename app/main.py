from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.database.Base import MyDb
from app.database.connation import engine
from app.routers import auth, applications, products
from app.utils.config import settings
from app.utils.rate_limiting import limiter


@asynccontextmanager
async def lifespan(app):
    yield
    engine.dispose()


app = FastAPI(title="ALJABR API", version="1.0.0", lifespan=lifespan,
              docs_url="/docs" if settings.DOCS_ENABLED else None,
              redoc_url=None, openapi_url="/openapi.json" if settings.DOCS_ENABLED else None)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
                   allow_credentials=False, allow_methods=["GET", "POST", "PUT", "DELETE"],
                   allow_headers=["Authorization", "Content-Type"])


@app.middleware("http")
async def response_security(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.url.path.startswith(("/auth", "/applications")):
        response.headers["Cache-Control"] = "no-store"
    return response


for router in (auth.router, applications.router, products.router):
    app.include_router(router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.get("/health/ready", tags=["Health"])
def ready(db: MyDb):
    from fastapi import HTTPException
    from sqlalchemy.exc import SQLAlchemyError
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(503, "Database unavailable") from None
    return {"status": "ok"}
