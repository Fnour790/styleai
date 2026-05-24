from fastapi import APIRouter

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/today")
async def get_today_recommendation():
    return {"message": "Recommendations coming soon!"}