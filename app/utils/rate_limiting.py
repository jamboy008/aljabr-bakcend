from slowapi import Limiter
from slowapi.util import get_remote_address
from app.utils.config import settings

# Only trust the actual peer address. Configure trusted proxy IPs on uvicorn.
limiter = Limiter(key_func=get_remote_address, storage_uri=settings.RATE_LIMIT_STORAGE)
