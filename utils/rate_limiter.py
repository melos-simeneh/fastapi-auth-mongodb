from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address)

def rate_limiter_per_minute(minute: int = 5):
    return limiter.limit(f"{minute}/minute")


