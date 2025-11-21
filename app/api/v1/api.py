from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    countries,
    brands,
    products,
    offerings,
    activities,
    staffing,
    pricing,
    wbs,
    admin_stats
)

api_router = APIRouter()

# Auth routes (no prefix, available at /api/v1/login, /api/v1/auth/callback, etc.)
api_router.include_router(auth.router, tags=["authentication"])

# Protected routes
api_router.include_router(countries.router, tags=["countries"])
api_router.include_router(brands.router, tags=["brands"])
api_router.include_router(products.router, tags=["products"])
api_router.include_router(offerings.router, tags=["offerings"])
api_router.include_router(activities.router, tags=["activities"])
api_router.include_router(staffing.router, tags=["staffing"])
api_router.include_router(pricing.router, tags=["pricing"])
api_router.include_router(wbs.router, tags=["wbs"])
api_router.include_router(admin_stats.router, tags=["admin"])